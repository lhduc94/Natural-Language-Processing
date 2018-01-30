import pymssql
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
cn = pymssql.connect(server = "172.20.2.110",user = "duclh",password= "lehuynhduc",database ="RecommendDB",as_dict=True,charset='UTF-8')
cur = cn.cursor()
cur.execute("[paytv_search_autocomplete] 'VOD'")
datas = cur.fetchall()
file = open('title.txt','w')
for item in datas:
    if item[u'lang'] =='vi':
        file.write(str(item[u'keyword']).lower()+'\n')
        print item[u'keyword']
file.close()
