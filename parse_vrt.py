import os
import sys
from lxml import etree


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
        if text_count % 1000 == 0:
            sys.stderr.write(f"\r{text_count} texts read")
        text = parser.close()
        this_text = []
        for leaf in text.iter():
            tokens = leaf.text.strip()
            if tokens != "":
                for token in tokens.split('\n'):
                    this_text.append(token.split('\t')[lemma_col-1])
                    token_count += 1
        retval.append(this_text)
    sys.stderr.write(f"\r  {text_count} texts read\n")
    sys.stderr.write(f"  {token_count} tokens total\n")
    return retval

def parse_vrt_in_dir(dirname):
    retval = []
    for filename in os.listdir(dirname):
        if not filename.endswith('.vrt'):
            continue
        # Exercise: parallelise parsing the corpora
        retval += vrt2lemmalists(os.path.join(dirname, filename))
    return retval

if __name__ == '__main__':
    parse_vrt_in_dir(sys.argv[1])
