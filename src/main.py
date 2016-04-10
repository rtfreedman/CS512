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
    import nltk
except ImportError:
    install('nltk')
    import nltk

# import the tweet tokenizer
from nltk.tokenize import TweetTokenizer

## funtions
# uses generator functions to keep memory use low

# load all files in a directory and treat it as data
def load(fpath):
    with open(fpath, 'r') as fin:
        yield from fin

# strips any whitespace or newlines from the ends of the line
def strip_line(loaded_path):
    yield from (l.strip() for l in loaded_path)

# splits the tab delimited lines of the file
def tokenize_line(lines):
    yield from (l.split('\t') for l in lines)

# assigns headers to the tokens of the lines. Returns the lines as dictionaries
def extract_data(line_tokens):
    headers = ['userid','lat','lon','unixtimex1000','tweet','polygonid','landusecode','landusecategory']
    yield from ({k: v for k,v in zip(headers, tokens)} for tokens in line_tokens)

# operates on the message to tokenize it as a tweet
def tokenize_message(messages):
    tknzr = TweetTokenizer()
    yield from (tknzr.tokenize(m['tweet']) for m in messages)

# remove any users from the tokenized tweets
def remove_users(tokenized_tweets):  # @user
    yield from ([t for t in token if not t.startswith('@')] for token in tokenized_tweets)

# remove random punctuation from the tokenized tweets. Don't worry, emoji is unicode so this won't kill it.
def remove_punctuation(tokenized_tweets):  # emojis are unicode
    def _filter_(strng):
        if len([i for i in strng if not i in string.punctuation]) == 0:
            return False
        else:
            return True

    yield from ([t for t in token if _filter_(t)] for token in tokenized_tweets)

# remove all urls tokens that begin with http
def remove_http(tokenized_tweets):
    yield from ([t for t in token if not t.startswith('http:')] for token in tokenized_tweets)

# separate the tokens of the tweet into words, hashtags, or emojis
def word_emoji_hashtag(tokenized_tweets):
    def is_emoji(token):
        return token in emoji.EMOJI_UNICODE.values()

    def is_hashtag(token):
        return token.startswith('#')

    for tweet in tokenized_tweets:
        data = defaultdict(list)
        data['emojis'] = [t for t in tweet if is_emoji(t)]
        data['hashtags'] = [t for t in tweet if is_hashtag(t)]
        data['words'] = [t.lower() for t in tweet if not is_emoji(t) and not is_hashtag(t)]
        yield data

# return lines of header tagged data for a filename
def tagged_data(fpath):
    items=load(fpath)  # generate data
    lines = strip_line(items)  # generate stripped lines
    tokens = tokenize_line(lines)  # generate tokens of lines
    yield from extract_data(tokens)  # cast tokens to dicts

# return word, hashtag, emoji bins from each line of file data
def binned_data(tagged_data):
    tokenized_tweets = tokenize_message(data)  # tokenize the messages
    non_user_tokens = remove_users(tokenized_tweets)  # remove user tokens
    non_punc_tokens = remove_punctuation(non_user_tokens)  # remove punctuation only tokens
    non_url_tokens = remove_http(non_punc_tokens)  # remove url tokens
    yield from word_emoji_hashtag(non_url_tokens)  # returns a dict of 'emojis','hashtags','words' for each tweet

# build a co-occurrence matrixes of tokenized data by a window of lines
def generate_matrix(kind, binned_data, window_size=1000):
    assert kind in ('emojis','words','hashtags'), "Unknown Data Kind!"

    # truncate binned data to make it a multiple of window_size
    if len(binned_data) < window_size:
        print("window size is to large")
        return
    elif len(binned_data) % window_size != 0:
        binned_data = binned_data[:-(len(binned_data)%window_size)]

    for index in range(0, len(binned_data), window_size):
        # get window of data
        win_data = binned_data[index:index+window_size]
        # make unique kind pair for each value of kind in each tweet
        window_comat = Counter()
        for tweet in win_data:
            tweet_comat = Counter()
            kdata = tweet[kind]
            for p in itertools.combinations(kdata,2):
                pair = list(p)
                pair.sort()
                tweet_comat.update({tuple(pair): 1})
            window_comat = window_comat + tweet_comat
        yield window_comat







if __name__ == "__main__":
    PATH = "../data/test10000.txt"

    # build up the chain of generators
    data = tagged_data(PATH)
    separated_kinds = list(binned_data(data))
    emats = generate_matrix('emojis',separated_kinds,window_size=1000)
    hmats = generate_matrix('hashtags',separated_kinds,window_size=1000)
    wmats = generate_matrix('words',separated_kinds,window_size=1000)

    # print out matrix for first window
    e = next(iter(emats))
    h = next(iter(hmats))
    w = next(iter(wmats))
    print(e)
    print(h)
#    print(w)

