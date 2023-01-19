import gensim
import os
import sys
import time
from parse_vrt import parse_vrt_in_dir

processed_corpus = []
dirname = sys.argv[1]

corpus_lemmalists = parse_vrt_in_dir(dirname)

sys.stderr.write("Building gensim dictionary... "); sys.stderr.flush()
start_time = time.time()

# Exercise 4: parallelise computing the dictionary
# Hint: you will nead to read the gensim API documentation
dictionary = gensim.corpora.Dictionary(corpus_lemmalists)
sys.stderr.write(f"Done in {time.time() - start_time:.2f} s\n")
sys.stderr.write("Computing BOW corpus... "); sys.stderr.flush()
start_time = time.time()

# Exercise 3: Parallelise computing bow_corpus
# Hint: send the corpus in suitable-sized chunks to processes that map
# the corpus with the function dictionary.doc2bow
bow_corpus = [dictionary.doc2bow(text) for text in corpus_lemmalists]
sys.stderr.write(f"Done in {time.time() - start_time:.2f} s\n")
sys.stderr.write("Computing LDA model... "); sys.stderr.flush()
start_time = time.time()

# Exercise 2: replace LdaModel with a parallel version
# Hint: you can simply replace the model name, but do look at the API,
# choose a number of processes, and test which one works best. Warning:
# memory consumption will grow with number of processes, it's possible to run
# out if you have a lot of cores!
lda = gensim.models.LdaModel(bow_corpus, num_topics = 10)
sys.stderr.write(f"Done in {time.time() - start_time:.2f} s\n")
for topic in enumerate(lda.show_topics(num_topics = 10,
                                       num_words = 10,
                                       formatted = False)):
    print(f"Topic {topic[0] + 1}:")
    for word, probability in topic[1][1]:
        print("  " + dictionary[int(word)])
