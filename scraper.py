import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import unquote
from urllib import robotparser
from utils import download
import requests
from simhash import Simhash, SimhashIndex

def scraper(config, robot_cache_a, robot_cache_d, robot_url_cache, mem, mem2, url, resp):
	links = extract_next_links(url, resp)
	return [link for link in links if is_valid(config, robot_cache_a, robot_cache_d, 
		robot_url_cache, mem, mem2, link, resp)] #will be thrown in frontier by worker

def extract_next_links(url, resp):
	lst = []
	if 200<= resp.status < 300:
		html_doc = resp.raw_response.text
		print("resp .url: ", resp.url)
		soup = BeautifulSoup(html_doc, 'html.parser')
		for link in soup.find_all('a'):
			hlink = link.get('href')
			lst.append(hlink)
	return lst
	# defend our position of low quality urls.

	#total number of words on a page
	#most common words

def is_valid(config, robot_cache_a, robot_cache_d, robot_url_cache, mem, mem2, url, resp):
	"""
	mem = set() #memory cache of unique urls
	robot_cache_a = set() #memory cache of allowed urls
    robot_cache_d = set() #memory cache of disallowed urls
    robot_url_cache = set() #memory cache of crawled robots.txt stored as netloc
    """
	try:
		parsed = urlparse(url)
		if parsed.scheme not in set(["http", "https"]):
			return False
		else:
			url = url.replace(parsed.fragment, "")
		
			extbool = not re.match(
				r".*\.(css|js|bmp|gif|jpe?g|ico"
				+ r"|png|tiff?|mid|mp2|mp3|mp4"
				+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
				+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
				+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
				+ r"|epub|dll|cnf|tgz|sha1"
				+ r"|thmx|mso|arff|rtf|jar|csv"
				+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

			extbool2 = not re.match(
				r".*\.(css|js|bmp|gif|jpe?g|ico"
				+ r"|png|tiff?|mid|mp2|mp3|mp4"
				+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
				+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
				+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
				+ r"|epub|dll|cnf|tgz|sha1"
				+ r"|thmx|mso|arff|rtf|jar|csv"
				+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.query.lower())
	
			extbool3 = not re.match(
				r".*/(css|js|bmp|gif|jpe?g|ico"
				+ r"|png|tiff?|mid|mp2|mp3|mp4"
				+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
				+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
				+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
				+ r"|epub|dll|cnf|tgz|sha1"
				+ r"|thmx|mso|arff|rtf|jar|csv"
				+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)/.*", parsed.path.lower())
			
			ebool = extbool and extbool2 and extbool3
	
			sub_bool  = re.match(r"(www.)?[-a-zA-Z0-9.]*.ics.uci.edu", parsed.netloc)
			sub_bool2 = re.match(r"(www.)?[-a-zA-Z0-9.]*.cs.uci.edu", parsed.netloc)
			sub_bool3 = re.match(r"(www.)?[-a-zA-Z0-9.]*.informatics.uci.edu", parsed.netloc)
			sub_bool4 = re.match(r"(www.)?[-a-zA-Z0-9.]*.stat.uci.edu", parsed.netloc)
			sub_bool5 = (re.match(r"(www.)?[-a-zA-Z0-9.]*.today.uci.edu", parsed.netloc) 
            	and (parsed.path == "/department/information_computer_sciences/"))

			sbool = sub_bool or sub_bool2 or sub_bool3 or sub_bool4 or sub_bool5

			if (ebool and sbool):
				if parsed.netloc not in robot_url_cache:
					robot_url_cache.add(parsed.netloc)
					robot_site = parsed.scheme + "://" + parsed.netloc + "/robots.txt"
					robot_resp = download.download(robot_site, config, logger=None)
					if 200<= robot_resp.status < 300:
						robot_txt = robot_resp.raw_response.text
						parse(parsed, robot_txt, robot_cache_a, robot_cache_d)
					"""
					the game plan is:
						create our similar download function (like the one provided)
						so that we can ensure it downloads from the cache server. check
						download.py. Read the response given(text/read/content/whatever),
						grab the disallowed urls.
						create a set of disallowed urls(complete with domain and path).
						then check if netloc+path are in the disallowed set
				
					#check crawl delay
					#check if url can be accessed
					"""
				#else
				#found in robot_url_cache - just means it's been checked.
				#doesn't necessarily mean there is a robots.txt
				if url not in mem:
					
					print("mem: ", mem)

					#simhash here
					doc = resp.raw_response.text
					soup = BeautifulSoup(doc, 'html.parser')
					#filter text from site
					[s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
					text_only = soup.getText()
					filtered_text = " ".join(text_only.split())
					s = Simhash(get_features(filtered_text))

					index=SimhashIndex(mem2,k=10)
					if index.get_near_dups(s) != []:
						print('this is running insteawd')
						return False
					else:
						print('this runs')
						if url in robot_cache_a:
							print("URL ADDED:", url)
							mem.add(url)
							mem2.append((str(url),s))
							return True
						elif url in robot_cache_d:
							return False
						else:
							print("URL ADDED:", url)
							mem.add(url)
							mem2.append((str(url),s))
							return True
				else:
					return False

	except TypeError:
		print ("TypeError for ", parsed)
		raise

#https://github.com/python/cpython/blob/master/Lib/urllib/robotparser.py#L144
#TODO
def parse(parsed, robot_txt, robot_cache_a, robot_cache_d):
	parsed_robot = robot_txt.splitlines()
	#state = 0 --nothing
	#state = 1 --useragent * found
	state = 0

	for line in parsed_robot:
		line = line.split()
		if len(line) == 2:
			key = line[0].strip().lower()
			value = unquote(line[1].strip())
			if key == "user-agent":
				if value == "*":
					state = 1
				else:
					state = 0
			elif state == 1:
				if key == "disallow":
					robot_cache_d.add(parsed.scheme + "://" + parsed.netloc + value)
				elif key == "allow":
					robot_cache_a.add(parsed.scheme + "://" + parsed.netloc + value)

def get_features(text):
	width = 20
	text=text.lower()
	text=re.sub(r'[^\w]+','',text)
	return [text[i:i+width]for i in range(max(len(text)-width + 1, 1))]

STOPWORDS = [
	'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 
	'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 
	'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', 
	"couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 
	'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', 
	"hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 
	'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 
	'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', 
	"it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 
	'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 
	'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't",
	'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 
	'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 
	'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", 
	"they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 
	'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', 
	"what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 
	'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd",
	"you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'
]

#TODO:
#MAKE SURE TO INCLUDE SUBDOMAINS -- use re.match with parsed.netloc.
#AND CHECK ROBOT - make sure delay?? nothing is wrong with .5 seconds
#defragment urls?
