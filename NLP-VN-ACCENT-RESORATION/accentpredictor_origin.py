from collections import Counter
import re
import math
from time import time


def normalisestring(_string):
    return _string.strip()


class AccentPredictor:
    def __init__(self):
        self._1gram = {}
        self._2gram = {}
        self._1statistic = {}
        self.accents = set()
        self.max = 18
        self.min = -1000

        self.totalcount1gram = 0
        self.totalcount2gram = 0
        self._size1gram = 0
        self._size1gram = 0
        self.globalposiblechanges = set()
        self.maxwordlength = 8
        self.maxn = 100
        self.maxp = 100

        self.loadngram(_1gramfile='datasets/news1gram', _2gramfile='datasets/news2grams',
                       _accentinfofile='datasets/AccentInfo.txt')

    def loadngram(self, _1gramfile, _2gramfile, _accentinfofile):
        print "loading ngram...."
        self._1gram = self.getngrams(filename=_1gramfile, is1gram=True)
        self._2gram = self.getngrams(filename=_2gramfile, is1gram=False)
        self.accents = self.getaccentinfo(filename=_accentinfofile)
        print self.accents.__len__()
        print "done!"

    def getngrams(self, filename, is1gram):
        ngrams = {}
        count = 0
        with open(filename, 'r') as f:
            for line in f:
                ngramword, ngramcount = line.split("\t")
                try:
                    ngramword = ngramword.decode("utf-8")
                    ngrams[ngramword] = int(ngramcount)
                    count += int(ngramcount)
                except:
                    print "abc"
                    print count
                    pass

        if is1gram:
            self._size1gram = len(ngrams)
            self.totalcount1gram = count
        else:
            firstgram = []
            for ngramsword in ngrams.keys():
                firstgram.append(ngramsword.split(" ")[0])
            self._1statistic = dict(Counter(firstgram))
            self._size2gram = len(ngrams)
            self.totalcount2gram = count
        return ngrams

    def getaccentinfo(self, filename):
        output = set()
        with open(filename, 'r') as f:
            for line in f:
                output.add(line.decode("utf-8"))
        return output

    def getposiblechanges(self, _input, index, posiblechanges):
        if len(_input) > self.maxwordlength:
            return
        if index > len(_input):
            return
        elif index == len(_input):
            if _input in self._1gram.keys():
                self.globalposiblechanges.add(_input)
            return
        check = False
        for s in posiblechanges:
            if _input[index] in s:
                for i in range(len(s)):
                    tmp = _input
                    tmp = tmp[:index] + s[i] + tmp[index + 1:]
                    # print tmp
                    stmp = ""
                    for j in range(len(_input)):
                        stmp += tmp[j] + ""
                    self.getposiblechanges(stmp, index + 1, posiblechanges)
                check = True
        if not check:
            self.getposiblechanges(_input, index + 1, posiblechanges)

    def setposiblechanges(self):
        self.globalposiblechanges.clear()
        self.globalposiblechanges = set()

    def getgramcount(self, ngramword, ngrams):
        if ngramword in ngrams.keys():
            return ngrams[ngramword]
        else:
            return 0

    def predictaccents(self, _string):
        inputsentences = re.split("[.,!?;]", _string)
        output = []
        for _input in inputsentences:
            self.setposiblechanges()
            _in = normalisestring(_input)
            lowercasein = _in.lower()
            words = lowercasein.split(" ")
            numberp = []
            trace = [[0 for i in range(self.maxp)] for j in range(len(words))]
            q = [[0 for i in range(self.maxp)] for j in range(len(words))]

            posiblechange = []
            start = time()
            for i, word in enumerate(words):
                self.globalposiblechanges = set()
                self.getposiblechanges(word, 0, self.accents)
                if len(self.globalposiblechanges) == 0:
                    self.globalposiblechanges.add(word)
                numberp.append(len(self.globalposiblechanges))
                posiblechange.append(list(self.globalposiblechanges))
            print "posiblechange", time() - start
            if len(words) == 1:
                max = 0
                sure = words[0]
                for i in range(numberp[0]):
                    possible = posiblechange[0][i]
                    number1gram = self.getgramcount(possible,self._1gram)
                    if max < number1gram:
                        max = number1gram
                        sure = possible
                output.append(sure.strip() + "\n")
            else:
                for i in range(1, len(words)):
                    recentpossiblenum = numberp[i]
                    oldpossiblenum = numberp[i - 1]
                    for j in range(recentpossiblenum):
                        q[i][j] = self.min
                        temp = self.min
                        for k in range(oldpossiblenum):
                            _new = posiblechange[i][j]
                            _old = posiblechange[i - 1][k]
                            log = -100.0
                            number2gram = self.getgramcount(_old + " " + _new, self._2gram)
                            number1gram = self.getgramcount(_old, self._1gram)
                            if number1gram > 0 and number2gram > 0 :
                                log = math.log(float(number2gram + 1) / (number1gram + self._1statistic[_old]))
                            else:
                                log = math.log(1.0 / (2 * (self._size2gram + self.totalcount2gram)))
                            if i == 1:
                                log += math.log(float(number1gram + 1) / (self._size1gram + self.totalcount1gram))
                            if temp != q[i - 1][k]:
                                if temp == self.min:
                                    temp = q[i - 1][k]
                            value = float(q[i - 1][k]) + log
                            # print i - 1, k, q[i - 1][k]
                            # print value
                            # print _old, _new, log, number2gram, number1gram
                            if q[i][j] < value:
                                q[i][j] = value

                                trace[i][j] = k
                max = self.min
                k = 0
                for i in range(numberp[len(words) - 1]):
                    if max <= q[len(words) - 1][i]:
                        max = q[len(words) - 1][i]
                        k = i
                result = posiblechange[len(words) - 1][k]
                k = trace[len(words) - 1][k]
                i = len(words) - 2
                while i >= 0:
                    result = posiblechange[i][k] + " " + result
                    k = trace[i][k]
                    i = i - 1
                    print result
                output.append(result.strip())
        return output


if __name__ == '__main__':
    ap = AccentPredictor()
    start = time()
    for s in ap.predictaccents('chien tranh giua cac vi sao'):
        print s
    print time() - start
