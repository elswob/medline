#!/usr/bin/python

import sys
import re
import gzip
from datetime import datetime
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection, serializer, compat, exceptions, helpers
import logging
logging.basicConfig(filename='parse-ngrams.log',level=logging.INFO)

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

articles = []
fName=sys.argv[1]
print(fName)
ngram_type='unigram'
if 'bigram' in fName:
    ngram_type='bigram'
elif 'trigram' in fName:
    ngram_type='trigram'

with gzip.open(fName, 'r') as f:
    for line in f:   
        if ngram_type == 'unigram':
            pmid,t1,count = line.rstrip().split('\t')
            value=t1
            articles.append({'_index': 'medline-unigrams', '_id':pmid+':'+value, '_type': '_doc', "_op_type": 'index', '_source': {"pmid": pmid, "type": ngram_type, "value": value, "count": int(count)}})
        elif ngram_type == 'bigram':
            pmid,t1,t2,count = line.rstrip().split('\t')
            value=t1+' '+t2
            articles.append({'_index': 'medline-bigrams', '_id':pmid+':'+value, '_type': '_doc', "_op_type": 'index', '_source': {"pmid": pmid, "type": ngram_type, "value": value, "count": int(count)}})
        elif ngram_type == 'trigram':
            pmid,t1,t2,t3,count = line.rstrip().split('\t')
            value=t1+' '+t2+' '+t3
            articles.append({'_index': 'medline-trigrams', '_id':pmid+':'+value, '_type': '_doc', "_op_type": 'index', '_source': {"pmid": pmid, "type": ngram_type, "value": value, "count": int(count)}})
        #print(ngram_type,pmid,value,count)
    
#print(articles)
res = helpers.bulk(es, articles, raise_on_exception=False, request_timeout=60)
es.indices.refresh('medline-unigrams',request_timeout=60)
es.indices.refresh('medline-bigrams',request_timeout=60)
es.indices.refresh('medline-trigrams',request_timeout=60)

logging.info(datetime.now().isoformat() + " imported " + str(res[0]) + " records from " + sys.argv[1])
