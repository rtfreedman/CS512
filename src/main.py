#!/usr/local/bin/python3
import os
import sys
import pip
import string
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
        data['words'] = [t for t in tweet if not is_emoji(t) and not is_hashtag(t)]
        yield data

if __name__ == "__main__":
    PATH = "../data/test10000.txt"

    # build up the chain of generators
    items=load(PATH)  # generate data
    lines = strip_line(items)  # generate stripped lines
    tokens = tokenize_line(lines)  # generate tokens of lines
    data = extract_data(tokens)  # cast tokens to dicts
    tokenized_tweets = tokenize_message(data)  # tokenize the messages
    non_user_tokens = remove_users(tokenized_tweets)  # remove user tokens
    non_punc_tokens = remove_punctuation(non_user_tokens)  # remove punctuation only tokens
    non_url_tokens = remove_http(non_punc_tokens)  # remove url tokens
    separated_kinds = word_emoji_hashtag(non_url_tokens)  # returns a dict of 'emojis','hashtags','words' for each tweet

    # none of the chain of generators execute until this for loop happens.
    # for now generate a binning of the emojis
    binning = Counter()
    for s in separated_kinds:
        [binning.update({e:1}) for e in s['emojis']]

    i = 0
    for e in binning.most_common():
        i += 1
        print(e)
        if i > 10: break


