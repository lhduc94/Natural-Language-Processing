import numpy as np
from collections import Counter
from time import time

def getngrams(filename, is1gram):
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
        totalcount1gram = count
        return (ngrams,totalcount1gram)
    else:
        firstgram = []
        for ngramsword in ngrams.keys():
            firstgram.append(ngramsword.split(" ")[0])
        _1statistic = dict(Counter(firstgram))

        totalcount2gram = count
        return (ngrams,totalcount2gram,_1statistic)

a = getngrams('datasets/news1gram',True)
print type(a[0])
b = getngrams('datasets/news2grams',False)
stat = {"totalcount1gram": a[1],"totalcount2gram": b[1]}
np.save('1gram.npy', a[0])
np.save('2gram.npy', b[0])
np.save('1statistic',b[2])
np.save('statistic',stat)


# start = time()
# read_dictionary = np.load('1gram.npy').item()
# print len(read_dictionary)
# print time() - start
# print read_dictionary
# start = time()
# read_dictionary2 = np.load('2gram.npy').item()
# print len(read_dictionary2)
# print time() - start
# start = time()
# read_dictionary3 = np.load('1statistic.npy').item()
# print len(read_dictionary3)
# print time() - start
# start = time()
# read_dictionary4 = np.load('statistic.npy').item()
# print read_dictionary4
# print time() - start