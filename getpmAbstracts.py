#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
getpmAbstracts.py
_author_ = Shreyas Karnik
"""





import urllib
import urllib2
import sys
from optparse import OptionParser
import xml.etree.ElementTree as ET
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from gensim.parsing import stem_text
import string
reload(sys)
sys.setdefaultencoding('utf-8')
usage = "usage:python %prog -q [query] -o [output] -s [flag for steming]"
parser = OptionParser(usage=usage)
parser.add_option("-q", "--query",action="store", dest="query",help="Enter the PubMed query (PubMed style queries supported)", metavar="QUERY")
parser.add_option("-o", "--output",action="store",dest="outfile",help="Enter the output file name to store result", metavar="OFILE")
parser.add_option("-s", "--stem",action="store_true",dest="stem",help="To stem result", metavar="STEM")
(options, args) = parser.parse_args()

if (len(options.query)<0):
	parser.print_help()

if (len(options.outfile)<0):
        parser.print_help()


######functions
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

def de_safe_xml(kinda_xml):
    """Converts an escaped HTML/XML into a more normal string."""
    htmlCodes = (('&', '&amp;'),('<', '&lt;'),('>', '&gt;'),('"', '&quot;'),("'", '&#39;'))
    for rep, orig in htmlCodes:
     	kinda_xml = kinda_xml.replace(orig, rep)
    return kinda_xml

def main():
	query=options.query
	ofile=options.outfile
	esearch = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=xml&retmax=10000000&term=%s' % (query)
	handle = urllib.urlopen(esearch)
	data = handle.read()
	root = ET.fromstring(data)
	f = open(ofile, 'a')
	ids = [x.text for x in root.findall("IdList/Id")]
	print 'Got %d articles' % (len(ids))
	count=0
	for group in chunker(ids, 100):
		efetch = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?&db=pubmed&retmode=xml&id=%s" % (','.join(group))
    		handle = urllib.urlopen(efetch)
    		data = handle.read()
		root = ET.fromstring(data)
		for article in root.findall("PubmedArticle"):
			abstract_text=''
			pmid = article.find("MedlineCitation/PMID").text
        		title = article.findtext("MedlineCitation/Article/ArticleTitle")
			abstract = article.findall("MedlineCitation/Article/Abstract/AbstractText")
			#print (len(abstract))
			if(len(abstract)>0):
				count=count+1
				for abst_part in abstract:
					abstract_text+=' '+str(abst_part.text)
				title.encode('utf-8', 'replace')
				abstract_text.encode('utf-8', 'replace')     		
				final=str(title)+" "+str(abstract_text)
				final.encode('utf-8', 'replace')
			        if(options.stem==True):
					final=final.translate(None,string.punctuation)
					f.write(stem_text(final.lower())+"\n")
				else:
				  final=final.translate(None,string.punctuation)
				  f.write(final+"\n")
			else:
			   print 'skipping PMID %s as length of abstract is zero' % pmid
	print 'written to %s articles to file %s' % (count,ofile)
if __name__ == "__main__":
    main()
