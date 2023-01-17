import gensim
import os
import sys
from parse_vrt import vrt2lemmalists

processed_corpus = []
dirname = sys.argv[1]


for filename in os.listdir(dirname):
    if not filename.endswith('.vrt'):
        continue
    # Exercise: parallelise parsing the corpora
    processed_corpus += vrt2lemmalists(os.path.join(dirname, filename))

sys.stderr.write("Building gensim dictionary... ")
dictionary = gensim.corpora.Dictionary(processed_corpus)
sys.stderr.write("Done.\n")
sys.stderr.write("Computing BOW corpus...")
bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]
sys.stderr.write("Done.\n")
