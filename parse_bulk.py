#!/usr/bin/python

import sys
import re
from datetime import datetime
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection, serializer, compat, exceptions, helpers
import logging
logging.basicConfig(filename='parse.log',level=logging.INFO)

# rollback recent changes to serializer that choke on unicode
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

with open(sys.argv[1], 'r') as f:
        data=f.read()

recs = data.split("<PubmedArticle>");
# drop preamble
recs.pop(0)

articles = []

dateData=''
for r in recs:
        #Year
        #dateCompletedYear = re.findall('<DateCompleted>(?s).*<Year>(.*?)</Year>', r)
        pubDate = re.findall('<PubDate>(?s).*<Year>(.*?)</Year>', r)
        #print(dateCompletedYear)
        if pubDate:
            pubDate = int(pubDate[0])
        else:
            pubDate = 0
        
        #DOI
        doi = re.findall('<ArticleId IdType="doi">(.*?)</ArticleId>',r)
        if doi:
            doi = doi[0]
        else:
            doi=''

        #PMID
        pmid = re.findall('<PMID Version=.*>(.*?)</PMID>', r)
        if pmid:
                pmid = pmid[0]
        else:
                pmid = ""
             
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
            articles.append({'_index': 'medline', '_id':pmid, '_type': '_doc', "_op_type": 'index', '_source': {"doi":doi,"year":pubDate,"pmid": pmid, "title": title, "abstract": abstract, "timestamp": datetime.now().isoformat(), "type": type}})

res = helpers.bulk(es, articles, raise_on_exception=False, request_timeout=60)

logging.info(datetime.now().isoformat() + " imported " + str(res[0]) + " records from " + sys.argv[1])
