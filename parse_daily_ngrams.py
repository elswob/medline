#!/usr/bin/python

import sys
import re
import os
from datetime import datetime
import json
from nltk_functions import get_unigrams,get_bigrams,get_trigrams
from elasticsearch import Elasticsearch, RequestsHttpConnection, serializer, compat, exceptions, helpers
import logging
logging.basicConfig(filename='ngram-parse.log',level=logging.INFO)

# rollback recent changes to serializer that choke on unicode$
class JSONSerializerPython2(serializer.JSONSerializer):
        def dumps(self, data):
                # don't serialize strings
                if isinstance(data, compat.string_types):
                        return data
                try:
                        return json.dumps(data, default=self.default, ensure_ascii=True)
                except (ValueError, TypeError) as e:
                        raise exceptions.SerializationError(data, e)

es = Elasticsearch(serializer=JSONSerializerPython2())  # use default of localhost, port 9200

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
articles=[]
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
                value=n['t1']
                articles.append({'_index': 'medline-unigrams', '_type': '_doc', "_op_type": 'index', '_source': {"pmid": pmid, "type": "unigram", "value": value, "count": int(n['count'])}})
            #print(unigrams)
            bigrams=get_bigrams(title+' '+abstract)
            for n in bigrams:
                value=n['t1']+' '+n['t2']
                articles.append({'_index': 'medline-bigrams', '_type': '_doc', "_op_type": 'index', '_source': {"pmid": pmid, "type": "bigram", "value": value, "count": int(n['count'])}})
            #print(bigrams)
            trigrams=get_trigrams(title+' '+abstract)
            for n in trigrams:
                value=n['t1']+' '+n['t2']+' '+n['t3']
                articles.append({'_index': 'medline-trigrams', '_type': '_doc', "_op_type": 'index', '_source': {"pmid": pmid, "type": "trigram", "value": value, "count": int(n['count'])}})
            #print(trigrams)

res = helpers.bulk(es, articles, raise_on_exception=False, request_timeout=60)

logging.info(datetime.now().isoformat() + " imported " + str(res[0]) + " records from " + sys.argv[1])
print(datetime.now().isoformat() + " imported " + str(res[0]) + " records from " + sys.argv[1])
