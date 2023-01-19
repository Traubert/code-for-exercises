import os
import sys
from lxml import etree
from multiprocessing import Pool # process-based parallelism

def vrt2lemmalists(filename, max_texts = None, lemma_col = 3):
    '''
    Parse each text in a VRT file into a list of lemmas, and return a list of those lists.
    '''

    sys.stderr.write(f"Reading {filename}\n")
    retval = []
    fobj = open(filename, "rb")
    parser = etree.XMLParser(recover = True)
    
    text_count = 0
    token_count = 0
    for line in fobj:
        if max_texts and text_count >= max_texts:
            break
        parser.feed(line)
        if line.strip() != b'</text>':
            continue
        # A text has ended
        text_count += 1
        text = parser.close()
        this_text = []
        for leaf in text.iter():
            tokens = leaf.text.strip()
            if tokens != "":
                for token in tokens.split('\n'):
                    this_text.append(token.split('\t')[lemma_col-1])
                    token_count += 1
        retval.append(this_text)
    sys.stderr.write(f"Finished reading {filename}, {text_count} texts and {token_count} tokens\n")
    return retval

def parse_vrt_in_dir(dirname):
    # Solution (one possible one): we map each filename to a vrt2lemmalists call using multiprocessing.Pool
    retval = []
    # First we get the valid file names
    filenames = [os.path.join(dirname, filename) for filename in os.listdir(dirname) if filename.endswith('.vrt')]
    # Then we initialize a Pool object
    pool = Pool() # by default, processes = number of cores
    for result in pool.map(vrt2lemmalists, filenames):
        retval += result
    return retval

if __name__ == '__main__':
    parse_vrt_in_dir(sys.argv[1])
