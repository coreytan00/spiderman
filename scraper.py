import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scraper(mem, url, resp):
    links = extract_next_links(mem, url, resp)
    return [link for link in links if is_valid(link)] #will be thrown in frontier by worker

def extract_next_links(mem, url, resp):
    lst = []
    print("url: ", url)
    print("resp raw response: ", resp.raw_response)
    print("resp .url: ", resp.url)
    print("resp status: ", resp.status)
    print("resp error: ", resp.error)
    print("resp text: ", resp.text)
    print("resp json: ", resp.json())
    #if url not in mem:
    	#find the hrefs.
    return lst
    # defend our position of low quality urls.

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

DOMAINS = [
	".ics.uci.edu/",
	".cs.uci.edu/",
	".informatics.uci.edu/",
	".stat.uci.edu/",
	"today.uci.edu/department/information_computer_sciences/"
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