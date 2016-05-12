#!/usr/bin/env python3

import re
import string
import sys
import argparse
from collections import Counter

__all__ = ['WordFinder', 'Book']

lemmas = {}
with open('lemmas.txt') as fin:
    for line in fin:
        line = line.strip()
        headword = line.split('\t')[0]
        try:
            related = line.split('\t')[1]
        except IndexError:
            related = None
        lemmas[headword] = related


valid_words = set()
for headword, related in lemmas.items():
    valid_words.add(headword)
    if related:
        valid_words.update(set(related.split()))


class WordFinder(object):

    def __init__(self):
        """Create a lame container for 'quick' search

        Structure of main_table
        {
            'a':{
                     'abandon': {'abandons', 'abandoned', 'abandoning'},
                     'apply': {'applies', 'applied', 'applying'},
                     'abeam': None,
                     ...
                },
            'b': {...},
            'c': {...},
            ...
        }

        Structure of special_table
        {
            'although': {'altho', 'tho', 'though'},
            'bad': {'badder', 'baddest', 'badly', 'badness', 'worse', 'worst'},
            ...
        }
        """
        self.main_table = {}
        for char in string.ascii_lowercase:
            self.main_table[char] = {}
        self.special_table = {}

        for headword, related in lemmas.items():
            if len(headword) > 1:
                if related:
                    for word in related.split():
                        if word[0] != headword[0]:
                            self.special_table[headword] = set(related.split())
                            break
                    else:
                        self.main_table[headword[0]][headword] = set(related.split())
                else:
                    self.main_table[headword[0]][headword] = None

    def find_headword(self, word):
        """Search the 'table' and return the original form of a word"""
        word = word.lower()
        alpha_table = self.main_table[word[0]]
        if word in alpha_table:
            return word

        for headword, related in alpha_table.items():
            if related and (word in related):
                return headword

        for headword, related in self.special_table.items():
            if word == headword:
                return word
            if word in related:
                return headword
        # This should never happen after the removal of words not in valid_words
        # in Book.__init__()
        return None

    # TODO
    def find_related(self, headword):
        pass


def is_dirt(word):
    return word not in valid_words


def list_dedup(list_object):
    """Return the deduplicated copy of given list"""
    temp_list = []
    for item in list_object:
        if item not in temp_list:
            temp_list.append(item)
    return temp_list


class Book(object):

    def __init__(self, filepath):
        with open(filepath) as bookfile:
            content = bookfile.read().lower()
            self.temp_list = re.split('[^a-zA-Z]', content)
            self.temp_list = [item for item in self.temp_list if not is_dirt(item)]
            finder = WordFinder()
            self.temp_list = [finder.find_headword(item) for item in self.temp_list]

    def freq(self):
        """Count the occurencies of every word and return a collections.Counter object"""
        cnt = Counter()
        for word in self.temp_list:
            cnt[word] += 1
        return cnt

    # TODO
    def stat(self):
        pass


if __name__ == '__main__':
    platform = sys.platform
    if re.match(r'linux|darwin|freebsd\d+', platform):
        newline = '\n'
    elif re.match('win32', platform):
        answer = input('The code is not tested on Windows yet. Feedback is welcome. Continue? Y/n')
        if (answer == '') or re.match('y|yes', answer.lower()):
            newline = '\r\n'
        else:
            sys.exit(0)
    else:
        sys.exit('Unsupported platform.\n')    # Really need to terminate?

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input_file')
    parser.add_argument('-o', '--output', dest='output_file')
    args = parser.parse_args()

    book = Book(args.input_file)
    result = book.freq()
    # Maximum width of the ocurrence column
    max_width = max(len(str(v)) for v in result.values())

    report = []
    for word in sorted(result, key=lambda x: result[x], reverse=True):
        report.append('{:>{}} {}'.format(result[word], max_width, word))

    if args.output_file:
        with open(args.output_file, 'w') as output:
            output.write(newline.join(report))
            output.write(newline)
    else:
        print(newline.join(report))