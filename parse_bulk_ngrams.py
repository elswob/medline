#!/usr/bin/python

import sys
import re
import os
from datetime import datetime
import json
from nltk_functions import get_unigrams,get_bigrams,get_trigrams
import logging
logging.basicConfig(filename='parse.log',level=logging.INFO)


print('Reading ',sys.argv[1])
fName=os.path.basename(sys.argv[1])
print(fName)
with open(sys.argv[1], 'r') as f:
        data=f.read()

recs = data.split("<PubmedArticle>");
# drop preamble
recs.pop(0)

articles = []

dateData=''
u=open('data/ngrams/'+fName+'.unigrams.txt','w')
b=open('data/ngrams/'+fName+'.bigrams.txt','w')
t=open('data/ngrams/'+fName+'.trigrams.txt','w')
for r in recs:
        #Year
        #dateCompletedYear = re.findall('<DateCompleted>(?s).*<Year>(.*?)</Year>', r)
        #pubDate = re.findall('<PubDate>(?s).*<Year>(.*?)</Year>', r)
        #print(dateCompletedYear)
        #if pubDate:
        #    pubDate = int(pubDate[0])
        #else:
        #    pubDate = 0
        
        #DOI
        #doi = re.findall('<ArticleId IdType="doi">(.*?)</ArticleId>',r)
        #if doi:
        #    doi = doi[0]
        #else:
        #    doi=''

        #PMID
        pmid = re.findall('<PMID Version=.*>(.*?)</PMID>', r)
        if pmid:
                pmid = pmid[0]
        else:
                pmid = ""
        #print(pmid)     
        #title          
        title = re.findall('<ArticleTitle>(.*?)</ArticleTitle>', r)
        if title:
                title = title[0]
        else:
                title = ""
                
        #abstract
        abstract = re.findall('<Abstract>([\s\S]*?)</Abstract>', r)
        if abstract:
                abstract = re.sub("\n\s*", "", abstract[0])
                abstract = re.sub('<AbstractText Label="(.*?)".*?>', "\\1: ", abstract)
                abtract = re.sub('</AbstractText>', "", abstract)
        else:
                abstract = ""
        
        #pub type
        type = re.findall("<PublicationType UI=.*?>(.*?)</PublicationType>", r)
        if type:
                type = str(type)
        else:
                type = str([])
        #print(pmid,title,abstract,pubDate,type)        
        if pmid != '':
            unigrams=get_unigrams(title+' '+abstract)
            for n in unigrams:
                u.write(pmid+'\t'+n['t1']+'\t'+str(n['count'])+'\n')
            #print(unigrams)
            bigrams=get_bigrams(title+' '+abstract)
            for n in bigrams:
                b.write(pmid+'\t'+n['t1']+'\t'+n['t2']+'\t'+str(n['count'])+'\n')
            #print(bigrams)
            trigrams=get_trigrams(title+' '+abstract)
            for n in trigrams:
                t.write(pmid+'\t'+n['t1']+'\t'+n['t2']+'\t'+n['t3']+'\t'+str(n['count'])+'\n')
            #print(trigrams)
            #articles.append({'_index': 'medline', '_id':pmid, '_type': '_doc', "_op_type": 'index', '_source': {"doi":doi,"year":pubDate,"pmid": pmid, "title": title, "abstract": abstract, "timestamp": datetime.now().isoformat(), "type": type}})

#res = helpers.bulk(es, articles, raise_on_exception=False, request_timeout=60)

#logging.info(datetime.now().isoformat() + " imported " + str(res[0]) + " records from " + sys.argv[1])
