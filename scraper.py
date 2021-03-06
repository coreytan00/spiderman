import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import unquote
from urllib import robotparser
from utils import download
import requests
from simhash import Simhash, SimhashIndex
import socket

def scraper(config, robot_cache_a, robot_cache_d, robot_url_cache, mem, mem2, 
	longest_page, common_dict, ics_subdomains, url, resp):
	links = extract_next_links(url, resp)
	return [link for link in links if is_valid(config, robot_cache_a, robot_cache_d, 
		robot_url_cache, mem, mem2, longest_page, common_dict, ics_subdomains, link)] 

def extract_next_links(url, resp):
	lst = []
	parsed = urlparse(url)
	if resp.status == 200: #or if resp.ok --> <=200. try to grab.
		html_doc = resp.raw_response.text
		soup = BeautifulSoup(html_doc, 'html.parser')
		for link in soup.find_all('a'):
			hlink = link.get('href')
			#check hlink if it's a path name, append url shceme and netloc
			if type(hlink)==str:
				if len(hlink) == 0 or hlink[0] == "#":
					hlink = url
				elif len(hlink) >= 1 and hlink[0] == "/":
					hlink = parsed.scheme + "://" + parsed.netloc + hlink
				elif len(hlink) >= 2 and hlink[0:2] == "//":
					hlink = parsed.scheme + ":" + hlink
				lst.append(hlink)
	return lst

	
"""
This method uses the Simhash library from
https://github.com/leonsim/simhash/blob/master/simhash/__init__.py
The original code can be found at
https://leons.im/posts/a-python-implementation-of-simhash-algorithm/
"""
def is_valid(config, robot_cache_a, robot_cache_d, robot_url_cache, mem, mem2, 
	longest_page, common_dict, ics_subdomains, url):
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
				+ r"|epub|dll|cnf|tgz|sha1|sql"
				+ r"|thmx|mso|arff|rtf|jar|csv"
				+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

			extbool2 = not re.match(
				r".*\.(css|js|bmp|gif|jpe?g|ico"
				+ r"|png|tiff?|mid|mp2|mp3|mp4"
				+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
				+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
				+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
				+ r"|epub|dll|cnf|tgz|sha1|sql"
				+ r"|thmx|mso|arff|rtf|jar|csv"
				+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.query.lower())
	
			extbool3 = not re.match(
				r".*/(css|js|bmp|gif|jpe?g|ico"
				+ r"|png|tiff?|mid|mp2|mp3|mp4"
				+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
				+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
				+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
				+ r"|epub|dll|cnf|tgz|sha1|sql"
				+ r"|thmx|mso|arff|rtf|jar|csv"
				+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)/.*", parsed.path.lower())
			
			ebool = extbool and extbool2 and extbool3
	
			sub_bool  = re.match(r"(www.)?[-a-zA-Z0-9.]*\.ics\.uci\.edu", parsed.netloc)
			sub_bool2 = re.match(r"(www.)?[-a-zA-Z0-9.]*\.cs\.uci\.edu", parsed.netloc)
			sub_bool3 = re.match(r"(www.)?[-a-zA-Z0-9.]*\.informatics\.uci\.edu", parsed.netloc)
			sub_bool4 = re.match(r"(www.)?[-a-zA-Z0-9.]*\.stat\.uci\.edu", parsed.netloc)
			sub_bool5 = (re.match(r"(www.)?[-a-zA-Z0-9.]*today\.uci\.edu", parsed.netloc) 
            	and (parsed.path == "/department/information_computer_sciences/"))

			sbool = sub_bool or sub_bool2 or sub_bool3 or sub_bool4 or sub_bool5

			if (ebool and sbool):
				try:
					if parsed.netloc not in robot_url_cache:
						robot_url_cache.add(parsed.netloc)
						robot_site = parsed.scheme + "://" + parsed.netloc + "/robots.txt"
						robot_resp = download.download(robot_site, config, logger=None)
						if robot_resp.status == 200:
							robot_txt = robot_resp.raw_response.text
							parse(parsed, robot_txt, robot_cache_a, robot_cache_d)
		
					if url not in mem:
						site_resp = requests.get(url)
						if site_resp.status_code == 200:
							#simhash here
							doc = site_resp.text
							soup = BeautifulSoup(doc, 'html.parser')
							#filter text from site
							[s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
							text_only = soup.getText()
							filtered_text = text_only.split()

							#LOW INFO CONTENT
							if len(filtered_text)<20:
								return False

							s = Simhash(filtered_text)
							index=SimhashIndex(mem2) #k=2
							if index.get_near_dups(s) != []:
								return False
							else:
								if url in robot_cache_a:
									check(filtered_text, common_dict, longest_page, ics_subdomains, sub_bool, parsed.netloc, url)
									mem.add(url)
									mem2.append((str(url),s))
									return True
								elif url in robot_cache_d:
									return False
								else:
									check(filtered_text, common_dict, longest_page, ics_subdomains, sub_bool, parsed.netloc, url)
									mem.add(url)
									mem2.append((str(url),s))
									return True
						else:
							return False
					else:
						return False
				except socket.gaierror:
					return False
				except requests.exceptions.Timeout:
					return False
				except requests.exceptions.TooManyRedirects:
					return False
				except requests.exceptions.ConnectionError:
					return False
				except requests.exceptions.RequestException:
					return False
			else:
				return False

	except TypeError:
		#print ("TypeError for ", parsed)
		return False

def check(filtered_text, common_dict, longest_page, ics_subdomains, sub_bool, site, url):
	#find longest page in terms of number of words.
	if len(filtered_text) > longest_page[1]:
		longest_page[0] = url
		longest_page[1] = len(filtered_text)
	#most common words
	for word in filtered_text:
		word = word.lower()
		if re.match(r"[a-zA-Z0-9]+", word) and word not in STOPWORDS:
			common_dict[word] +=1
	#ics subdomains
	if sub_bool: #that means it is ics domain
		ics_subdomains[site].add(url)


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
	"you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves', ' '
]

#TODO:
#MAKE SURE TO INCLUDE SUBDOMAINS -- use re.match with parsed.netloc.
#AND CHECK ROBOT - make sure delay?? nothing is wrong with .5 seconds
#defragment urls?
