#!/usr/local/bin/python3
import os
import sys
import pip
import string
import itertools
from collections import defaultdict
from collections import Counter
from utils import *

# install emoji package if it is not imported
try:
    import emoji
except ImportError:
    install('emoji')
    import emoji

try:
    import scipy
except ImportError:
    install('scipy')
    import scipy

try:
    import nltk
except ImportError:
    install('nltk')
    import nltk

# import the tweet tokenizer
from nltk.tokenize import TweetTokenizer
from scipy import sparse

# the headers of the files we are using. Declared as a global
HEADERS = ['userid','lat','lon','unixtimex1000','tweet','polygonid','landusecode','landusecategory']
TOKENIZER = TweetTokenizer()
EMOJI = list(emoji.UNICODE_EMOJI.keys())

#### funtions####
# uses generator functions to keep memory use low

### file parseing ###
# load all files in a directory and treat it as data
# lines are generated from the file 1 by 1
def load(fpath):
    with open(fpath, 'r') as fin:
        yield from fin

# strips any whitespace or newlines from the ends of the line
def stripln(iterable): # a batch of lines is passed as an interable
    yield from (l.strip() for l in iterable)

# splits the tab delimited lines of the file
def tokenize(iterable):  # iterable of a batch of lines
    yield from (l.split('\t') for l in iterable)

# assigns headers to the tokens of the lines. Returns the lines as dictionaries with headers as the key
def extract_data(iterable):  # iterable is a batch of lines
    yield from ({header: tvalue for header,tvalue in zip(HEADERS, tokens)} for tokens in iterable)

# parse the file and return an iterable (generator) of
# each line/tweet in the form of a dictionary
# based on the column header in the file
def parser(fpath):  # filepath to load
    yield from extract_data(tokenize(stripln(load(fpath))))

####  the next set of functions operate on the tweet message itself ###

# a utility function returns True if the string input is punctuation
def is_punc(string_token):
    return all(map(lambda char: char in string.punctuation, string_token))

# is the string an emoji character?
def is_emoji(string_token):
    return string_token in EMOJI

# is this string a hashtag?
def is_hashtag(string_token):
    return string_token.startswith('#')


# tokenize the tweet message and ruturn just the message.
# accepts a parsed line of data
def npl_message(iterable):
    yield from (TOKENIZER.tokenize(data['tweet']) for data in iterable)

# scrub the tweet by removing references to users (@user), 
# spurious punctuation (emoji is unicode), 
# and http urls from the tweet messages.
# input is an iterable of tokenized tweets
def scrub(iterable):
    drop_users = ([t for t in tweet if not t.startswith('@')] for tweet in iterable)  # drop users
    drop_urls  = ([t for t in tweet if not t.startswith('http:') and not t.startswith('https:') and not t.startswith('ftp:')] for tweet in drop_users)  # drop urls
    drop_punc  = ([t for t in tweet if not is_punc(t)] for tweet in drop_urls)  # drop puncuation
    yield from (tweet for tweet in drop_punc if len(tweet)!=0)  # don't return totally scrubbed away tweets

# separate the tokens of the tweet into words, hashtags, or emojis
def word_emoji_hashtag(iterable):  # iterable is a set of scrubbed tweets
    for tweet in iterable:
        data = {}
        data['emojis'] = []
        data['hashtags'] = []
        data['words'] = []
        for t in tweet:
            if is_emoji(t):
                data['emojis'].append(t)
            elif is_hashtag(t):
                data['hashtags'].append(t)
            else:
                data['words'].append(t.lower())
        yield data

# return word, hashtag, emoji bins from each line of file data
def binned_data(iterable):  # iterable are the dictionary representations of each line of the file
    nlp_tweets = npl_message(iterable)
    scrubbed_tweets = scrub(nlp_tweets)
    yield from word_emoji_hashtag(scrubbed_tweets)  # returns a dict of 'emojis','hashtags','words' for each tweet

# build a co-occurrence matrixes of tokenized data by a window of lines
def generate_matrix(data, kind=[]):  # data should be passed in chunks of window_size
    # type checks
    for k in kind:
        assert k in ('emojis','words','hashtags'), "Unknown Data Kind!"

    # generate an index of unique tokens based on data
    index = set()
    for d in data:
        for k in kind:
            for token in d[k]:
                index.add(token)
    index = list(index)

    # make an output sparse matrix
    matrix = sparse.lil_matrix((len(index), len(index)))

    # if index of row co-occures with index of col then matrix[row,col] += 1
    for d in data:

        # get all the tokens within a tweet from all the kinds
        tokens = []
        for k in kind:
            for token in d[k]:
                tokens.append(token)

        # generate co-occurence for the tokens
        for p in itertools.combinations(tokens, 2):
            idxr = index.index(p[0])
            idxc = index.index(p[1])

            # increment the spare matrix
            matrix[idxr, idxc] += 1

    return index, matrix

# resolve the values of the matrix based on the index from greatest frequency to least
def resolve(index, matrix):
    print(len(index), matrix.shape)
    output = {}
    # collect all the values
    for i in range(matrix.shape[0]):
        for j in range(i, matrix.shape[1]):
            val = matrix[i,j]
            if val>1:  # skip all 1 values
                idxpair = [index[i],index[j]]
                idxpair.sort()
                output[tuple(idxpair)] = val
    return output

def load_lexicon():
    lexicon = dict()
    with open('../data/positive-words.txt','r') as positive:
        words = [term.replace('\n','') for term in positive]
        [lexicon.update({w: 1}) for w in words]

    with open('../data/negative-words.txt','r',encoding='latin1') as negative:
        words = [term.replace('\n','') for term in negative]
        [lexicon.update({w: -1}) for w in words]

    with open('../data/lexicon-emoji.txt','r') as smileys:
        for term in smileys:
            e, v = term.strip().split(' ')
            lexicon[e] = float(v)

    return lexicon

def apply_lexicon(lexicon, resolved_dict):

    def lookup(k):
        if k in lexicon:
            return lexicon[k]
        else:
            return 0

    # sum the tuple pair values
    pair_sums = list(map(lambda k: lookup(k[0]) + lookup(k[1]), resolved_dict.keys()))

    if len(pair_sums) == 0: return "No Pair Sums"

    # average all the pair_sums
    return sum(pair_sums) / len(pair_sums)



if __name__ == "__main__":
    PATH = "../data/test10000.txt"

    # build up the chain of generators
    print("LOAD DATA")
    data = parser(PATH)

    # we can filter data by other attriutes in the file
    # here if we want to. This will happen before it is
    # passed to binned_data

    # load the lexicon
    lexicon = load_lexicon()

    separated_kinds = list(binned_data(data))

    for i in range(0, len(separated_kinds), 1000):  # step in window size of 1000
        window = separated_kinds[i: i+1000]

        print("WINDOW ", i, " ", len(window))

        idx,emats = generate_matrix(window, ['emojis'])
        print(apply_lexicon(lexicon,resolve(idx,emats)))

        idx,hmats = generate_matrix(window, ['hashtags', 'emojis'])
        print(apply_lexicon(lexicon,resolve(idx,hmats)))

        # commented out for testing because it is slow
        #idx,wmats = generate_matrix(window, ['words'])
        #print(apply_lexicon(lexicon,resolve(idx,wmats)))
