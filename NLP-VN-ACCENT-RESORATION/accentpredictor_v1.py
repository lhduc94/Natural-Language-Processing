# -*- coding: utf-8 -*-
from collections import Counter
import re
import math
from time import time
import numpy as np

def normalisestring(_string):
    return _string.strip()

accents = {u"a":[u"a",u"à",u"á",u"ả",u"ạ",u"ã",u"â",u"ầ",u"ấ",u"ẩ",u"ậ",u"ẫ",u"ă",u"ằ",u"ắ",u"ẳ",u"ặ",u"ẵ"],
           u"e":[u"e",u"è",u"é",u"ẻ",u"ẹ",u"ẽ",u"ê",u"ề",u"ế",u"ể",u"ệ",u"ễ"],
           u"i":[u"i",u"ì",u"í",u"ỉ",u"ị",u"ĩ"],
           u"o":[u"o",u"ò",u"ó",u"ỏ",u"ọ",u"õ",u"ô",u"ồ",u"ố",u"ổ",u"ộ",u"ỗ",u"ơ",u"ờ",u"ớ",u"ở",u"ợ",u"ỡ"],
           u"u":[u"u",u"ù",u"ú",u"ủ",u"ụ",u"ũ",u"ư",u"ừ",u"ứ",u"ử",u"ự",u"ữ"],
           u"y":[u"y",u"ỳ",u"ý",u"ỷ",u"ỵ",u"ỹ"],
           u"d":[u"d",u"đ"]}

class AccentPredictor:
    def __init__(self):
        self._1gram = {}
        self._2gram = {}
        self._1statistic = {}
        self.totalcount1gram = 0
        self.totalcount2gram = 0
        self._size1gram = 0
        self._size2gram = 0
        self.loadngram()

    def loadngram(self):
        print "loading ngram...."

        start = time()
        self._1gram = np.load('1gram.npy').item()
        print "load 1gram", time() - start

        start = time()
        self._2gram = np.load('2gram.npy').item()
        print "load 2gram", time() - start

        start =  time()
        self._1statistic = np.load('1statistic.npy').item()
        print "load 1statistic", time() - start

        stats = np.load('statistic.npy').item()
        self.totalcount1gram = stats['totalcount1gram']
        self.totalcount2gram = stats['totalcount2gram']

        self._size1gram = len(self._1gram)
        self._size2gram = len(self._2gram)

        print "done!"

    def get_word(self, _input):
        t = set()
        t.add(_input)
        for c in _input:
            if c in accents.keys():
                for i in accents[c]:
                    temp = _input.replace(c, i)
                    if self._1gram.get(temp, -1) != -1:
                        t.add(temp)
        return t

    def predict_accents(self, _string):
        _input = normalisestring(_string).lower()
        words = _input.split(" ")
        number_word = len(words)

        numberp = []
        trace = [[0 for i in range(100)] for j in range(number_word)]
        q = [[0 for i in range(100)] for j in range(number_word)]

        default_log =  math.log(1.0 / (2 * (self._size2gram + self.totalcount2gram)))
        count1gram = self._size1gram + self.totalcount1gram
        min = -1000

        posiblechange = []
        start = time()
        for i, word in enumerate(words):
            globalposiblechanges = self.get_word(word)
            numberp.append(len(globalposiblechanges))
            posiblechange.append(list(globalposiblechanges))
        print "posiblechange", time() - start

        if number_word == 1:
            return words[0]
        else:
            for i in xrange(1, len(words)):
                recentpossiblenum = numberp[i]
                oldpossiblenum = numberp[i - 1]
                for j in xrange(recentpossiblenum):
                    q[i][j] = min
                    temp = min
                    for k in xrange(oldpossiblenum):
                        _new = posiblechange[i][j]
                        _old = posiblechange[i - 1][k]
                        log = -100.0
                        number2gram = self._2gram.get(_old + " " + _new, 0)
                        number1gram = self._1gram.get(_old, 0)
                        if number1gram > 0 and number2gram > 0 :
                            log = math.log(float(number2gram + 1) / (number1gram + self._1statistic[_old]))
                        else:
                            # log = math.log(1.0 / (2 * (self._size2gram + self.totalcount2gram)))
                            log = default_log
                        if i == 1:
                            # log += math.log(float(number1gram + 1) / (self._size1gram + self.totalcount1gram))
                            log += math.log(float(number1gram + 1) / count1gram)
                        if temp != q[i - 1][k]:
                            if temp == min:
                                temp = q[i - 1][k]
                        value = float(q[i - 1][k]) + log
                        # print i - 1, k, q[i - 1][k]
                        # print value
                        # print _old, _new, log, number2gram, number1gram
                        if q[i][j] < value:
                            q[i][j] = value
                            trace[i][j] = k

            max = min
            k = 0
            for i in xrange(numberp[number_word - 1]):
                if max <= q[number_word - 1][i]:
                    max = q[number_word - 1][i]
                    k = i

            result = posiblechange[number_word - 1][k]
            k = trace[number_word - 1][k]
            i = number_word - 2
            while i >= 0:
                result = posiblechange[i][k] + " " + result
                k = trace[i][k]
                i = i - 1
        return result.strip()

    def check_in(self,_string):
        if self._2gram.get(_string, -1) != -1 :
            print 'in'
        else :
            print 'not in'


if __name__ == '__main__':
    ap = AccentPredictor()
    sum = 0
    for i in xrange(10):
        start = time()
        print ap.predict_accents('hoang phi hong xuat kich')
        s = time() - start
        print s
        sum += s
    print 'avg time: ',float(sum) / 10