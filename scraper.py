import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
from urllib import robotparser
from utils import download

def scraper(config, robot_cache, robot_url_cache, mem, url, resp):
	links = extract_next_links(url, resp)
	return [link for link in links if is_valid(config, robot_cache, robot_url_cache, mem, link)] #will be thrown in frontier by worker

def extract_next_links(url, resp):
	lst = []
	print("resp .url: ", resp.url)
	print("resp status: ", resp.status)
	print("resp error: ", resp.error)
	if 200<= resp.status < 300:
		html_doc = resp.raw_response.text
		soup = BeautifulSoup(html_doc, 'html.parser')
		for link in soup.find_all('a'):
			hlink = link.get('href')
			lst.append(hlink)
	return lst
	# defend our position of low quality urls.

	#total number of words on a page
	#most common words

def is_valid(config, robot_cache, robot_url_cache, mem, url):
	try:
		parsed = urlparse(url)
		if parsed.scheme not in set(["http", "https"]):
			return False
		else:
			#url = url - parsed.
			extbool = not re.match(
				r".*\.(css|js|bmp|gif|jpe?g|ico"
				+ r"|png|tiff?|mid|mp2|mp3|mp4"
				+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
				+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
				+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
				+ r"|epub|dll|cnf|tgz|sha1"
				+ r"|thmx|mso|arff|rtf|jar|csv"
				+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

			sub_bool  = re.match(r"(www.)?[-a-zA-Z0-9.]*.ics.uci.edu", parsed.netloc)
			sub_bool2 = re.match(r"(www.)?[-a-zA-Z0-9.]*.cs.uci.edu", parsed.netloc)
			sub_bool3 = re.match(r"(www.)?[-a-zA-Z0-9.]*.informatics.uci.edu", parsed.netloc)
			sub_bool4 = re.match(r"(www.)?[-a-zA-Z0-9.]*.stat.uci.edu", parsed.netloc)
			sub_bool5 = (re.match(r"(www.)?[-a-zA-Z0-9.]*.today.uci.edu", parsed.netloc) 
            	and (parsed.path == "/department/information_computer_sciences/"))
			if (extbool and (sub_bool or sub_bool2 or sub_bool3 or sub_bool4 or sub_bool5)):
				if parsed.netloc not in robot_url_cache:
					robot_site = parsed.scheme + "://" + parsed.netloc + "/robots.txt"
					robot_resp = download.download(robot_site, config, logger=None)
					if 200<= robot_resp.status < 300:
						robot_url_cache.add(parsed.netloc)
						robot_txt = robot_resp.raw_response.text
						robot_txt2 = robot_resp.raw_response.content
						print(robot_txt.splitlines())
						#for line in robot_txt:
							#line = line.rstrip("\n")
						#	print(line)
						#findall

					"""
					the game plan is:
						create our similar download function (like the one provided)
						so that we can ensure it downloads from the cache server. check
						download.py. Read the response given(text/read/content/whatever),
						overload can_fetch method so that we can grab the disallowed urls.
						create a set of disallowed urls(complete with domain and path).
						then check if netloc+path are in the disallowed set.

					robot_resp = requests.get(robot_site)
					if robot_resp.ok:
						#crawl through, generate list of disallowed
						disallowed_lst = []
						robot_soup = BeautifulSoup(robot_resp.text, 'html.parser')
						#for link in soup.find_all(''):

						robot_cache[parsed.netloc] = 
				
					#check crawl delay
					#check if url can be accessed
					"""
					
				if url not in mem:
					mem.add(url)
					return True
				else:
					return False

	except TypeError:
		print ("TypeError for ", parsed)
		raise

DOMAINS = [
	"www.ics.uci.edu",
	"www.cs.uci.edu",
	"www.informatics.uci.edu",
	"www.stat.uci.edu",
]


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
