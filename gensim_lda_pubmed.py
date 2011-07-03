#!usr/bin/python
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from gensim import corpora, models, similarities
from nltk.corpus import stopwords
from optparse import OptionParser
import string
from nltk.stem.porter import *
from gensim.parsing import stem_text

"""
Some options using the option parser 
"""
usage = "usage: python %prog -i [inputfile] -m [ldamodel] -d [dictionary] -c [corpus output name] -k [number of topics to extract]"
parser = OptionParser(usage=usage)
parser.add_option("-i", "--inputfile",action="store", dest="inputfile",help="Enter the file containing PubMed abstracts", metavar="IFILE")
parser.add_option("-m", "--model",action="store",dest="model",help="Enter the name of file where you want to store output model", metavar="MFILE")
parser.add_option("-d", "--dictionary",action="store",dest="dicto",help="Enter the name of file where you want to store dictionary", metavar="DFILE")
parser.add_option("-c", "--corpusname",action="store",dest="corpname",help="Enter the name of file where you want to store corpus", metavar="CFILE")
parser.add_option("-k", "--numtopics",action="store",dest="ntopics",type="int",help="Number of topics", metavar="NTOP")
#parser.add_option("-v", action="store_true",help="Steming", dest="stem")
#parser.add_option("-q", action="store_false",help="No stemming", dest="stem")
(options, args) = parser.parse_args()
if (len(options.inputfile)<0):
	parser.print_help()
if (len(options.model)<0):
        parser.print_help()
if (len(options.dicto)<0):
        parser.print_help()
if (options.ntopics<=0):
        parser.print_help()
if (len(options.corpname)<0):
        parser.print_help()

def main():
  """
  Creating dictionary while removing stopwords and words that occur only once.
  """
  model=options.model
  inputfile=options.inputfile
  dicto=options.dicto
  ntopics=options.ntopics
  corpname=options.corpname
  stoplist = stopwords.words('english')
  texts = [[word.translate(None,string.punctuation) for word in document.lower().split() if word not in stoplist] for document in open(inputfile)]
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
  corpora.MmCorpus.serialize(corpname, corpus)
  tfidf = models.TfidfModel(corpus)
  corpus_tfidf = tfidf[corpus]
  
  """
  Running LDA
  """
  lda =models.LdaModel(corpus=corpus_tfidf, id2word=dictionary, num_topics=ntopics, update_every=5, passes=50)
  lda.print_topics(topics=ntopics,topn=10)
  lda.save(model)
  doc_lda = lda[corpus_tfidf]
  print(doc_lda)
  for doc in doc_lda:
    print(doc)
  
if __name__ == "__main__":
  main()