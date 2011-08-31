#!usr/bin/python
"""
gensim_lda_pubmed.py

Created by Shreyas Karnik on 2011-07-02.
Copyright (c) 2011 Shreyas Karnik.
"""
import logging
from gensim import corpora, models, similarities
from nltk.corpus import stopwords
from optparse import OptionParser
import string
from nltk.stem.porter import *
from gensim.parsing import stem_text

"""
Some options using the option parser 
"""
usage = "usage: python %prog -i [inputfile] -k [number of topics to extract] -v [verbose output FALSE by default] -t [TRUE/ FALSE for TFIDF weights] -r [return topics per document TRUE/FALSE (default FALSE)]"
parser = OptionParser(usage=usage)
parser.add_option("-i", "--inputfile",action="store", dest="inputfile",help="Enter the file containing PubMed abstracts", metavar="IFILE")
#parser.add_option("-m", "--model",action="store",dest="model",help="Enter the name of file where you want to store output model", metavar="MFILE")
#parser.add_option("-d", "--dictionary",action="store",dest="dicto",help="Enter the name of file where you want to store dictionary", metavar="DFILE")
#parser.add_option("-c", "--corpusname",action="store",dest="corpname",help="Enter the name of file where you want to store corpus", metavar="CFILE")
parser.add_option("-k", "--numtopics",action="store",dest="ntopics",type="int",help="Number of topics", metavar="NTOP")
parser.add_option("-t", "--tfidf",action="store",dest="tfidf",help="TFIDF weignting (default TRUE)", metavar="TFIDF",default="TRUE")
parser.add_option("-v",action="store",help="Verbose Output TRUE/FALSE (default FALSE)", dest="verbose",default="FALSE")
parser.add_option("-r",action="store",help="Return topics per document TRUE/FALSE (default FALSE)", dest="fit",default="FALSE")
#parser.add_option("-q", action="store_false",help="No stemming", dest="stem")
(options, args) = parser.parse_args()
if (len(options.inputfile)<0):
	parser.print_help()
#if (len(options.model)<0):
#        parser.print_help()
#if (len(options.dicto)<0):
#        parser.print_help()
if (options.ntopics<=0):
        parser.print_help()
#if (len(options.corpname)<0):
#        parser.print_help()

def main():
 
  model=options.inputfile+"_lda.model"
  inputfile=options.inputfile
  dicto=options.inputfile+"_lda.dict"
  ntopics=options.ntopics
  corpname=options.inputfile+"_lda.corpus"
  stoplist = stopwords.words('english')
  if(options.verbose=="TRUE"):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
  else:
    logger = logging.getLogger()
    formatter =logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    log_file_name=inputfile+"_lda.log"
    hdlr = logging.FileHandler(log_file_name)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)
  
  """
  Starting the number crunching
  """
  """
  Creating dictionary while removing stopwords and words that occur only once.
  """
  
  texts = [[word for word in document.lower().split() if word not in stoplist] for document in open(inputfile)]
  #texts = [[word.translate(None,string.punctuation) for word in document.lower().split() if word not in stoplist] for document in open(inputfile)]
  print ("Reading and tokenizing %s") % (inputfile)
  dictionary = corpora.Dictionary(line.lower().split() for line in open(inputfile))
  #dictionary = corpora.Dictionary(line.lower().split() for line in open(inputfile))
  stop_ids = [dictionary.token2id[stopword] for stopword in stoplist if stopword in dictionary.token2id]
  #removing stopwords
  once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
  dictionary.filter_tokens(stop_ids + once_ids)
  dictionary.compactify()
  print dictionary
  """
  Dictionary created and stored for future reference
  """
  dictionary.save(dicto)
  """
  Creating corpus and storing to disk, for later use
  using tfidf weights
  """
  corpus = [dictionary.doc2bow(text) for text in texts]
  if(options.tfidf=="TRUE"):
    tfidf = models.TfidfModel(corpus)
    corpus = tfidf[corpus]
    corpora.MmCorpus.serialize(corpname, corpus)
  else:
    corpora.MmCorpus.serialize(corpname, corpus) 
  """
  Running LDA
  """
  lda =models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=ntopics,passes=40,update_every=1,chunksize=800)
  """
  Printing LDA output
  """
  print("LDA finished printing %d topics with 12 top words") %(ntopics)
  lda.print_topics(topics=ntopics,topn=12)
  lda.save(model)                                                                                    
  if(options.fit=="TRUE"):
    out_fit_file=options.inputfile+"_lda.tc"
    print "Topic allocation written in %s" % (out_fit_file)
    f=open(out_fit_file,"a")
    doc_lda = lda[corpus]
    for doc in doc_lda:
      f.write(str(doc)+"\n")  
  if(options.verbose=="FALSE"):
    print "Processing finished please check %s for details" %(log_file_name) 
if __name__ == "__main__":
  main()
