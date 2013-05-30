#!usr/bin/python
"""
gensim_lda_pubmed.py

Created by Shreyas Karnik on 2011-07-02.
"""
import logging
from gensim import corpora, models
from nltk.corpus import stopwords
from optparse import OptionParser

usage = "usage: python %prog -i [inputfile] -k [number of topics to extract] -v [verbose output FALSE by default] -t [TRUE/ FALSE for TFIDF weights] -r [return topics per document TRUE/FALSE (default FALSE)]"
parser = OptionParser(usage=usage)
parser.add_option("-i", "--inputfile", action="store", dest="inputfile", help="Enter the file containing PubMed abstracts", metavar="IFILE")
parser.add_option("-k", "--numtopics", action="store", dest="ntopics", type="int", help="Number of topics", metavar="NTOP")
parser.add_option("-t", "--tfidf", action="store", dest="tfidf", help="TFIDF weignting (default TRUE)", metavar="TFIDF", default="TRUE")
parser.add_option("-v", action="store", help="Verbose Output TRUE/FALSE (default FALSE)", dest="verbose", default="FALSE")
parser.add_option("-r", action="store", help="Return topics per document TRUE/FALSE (default FALSE)", dest="fit", default="FALSE")
options, args = parser.parse_args()
if len(options.inputfile) < 0:
    parser.print_help()
if options.ntopics <= 0:
    parser.print_help()


def main():
    model = options.inputfile + "_lda.model"
    inputfile = options.inputfile
    dicto = options.inputfile + "_lda.dict"
    ntopics = options.ntopics
    corpname = options.inputfile + "_lda.corpus"
    stoplist = stopwords.words('english')
    if options.verbose == "TRUE":
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    else:
        logger = logging.getLogger()
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
        log_file_name = inputfile + "_lda.log"
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
    logging.info("Reading and tokenizing {}".format(inputfile))
    dictionary = corpora.Dictionary(line.lower().split() for line in open(inputfile))
    stop_ids = [dictionary.token2id[stopword] for stopword in stoplist if stopword in dictionary.token2id]
    #removing stopwords
    once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
    dictionary.filter_tokens(stop_ids + once_ids)
    dictionary.compactify()
    """
    Dictionary created and stored for future reference
    """
    dictionary.save(dicto)
    """
    Creating corpus and storing to disk, for later use
    using tfidf weights
    """
    corpus = [dictionary.doc2bow(text) for text in texts]
    if options.tfidf == "TRUE":
        tfidf = models.TfidfModel(corpus)
        corpus = tfidf[corpus]
        corpora.MmCorpus.serialize(corpname, corpus)
    else:
        corpora.MmCorpus.serialize(corpname, corpus)
    """
    Running LDA
    """
    lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=ntopics, passes=40, update_every=1, chunksize=800)
    """
    Printing LDA output
    """
    logging.info("LDA finished printing {} topics with 12 top words".format(ntopics))
    lda.print_topics(topics=ntopics, topn=12)
    lda.save(model)
    if options.fit:
        out_fit_file = options.inputfile + "_lda.tc"
        logging.info("Topic allocation written in {}".format(out_fit_file))
        f = open(out_fit_file, "a")
        doc_lda = lda[corpus]
        for doc in doc_lda:
            f.write(str(doc) + "\n")
    if not options.verbose:
        logging.info("Processing finished please check {} for details".format(log_file_name))


if __name__ == "__main__":
    main()
