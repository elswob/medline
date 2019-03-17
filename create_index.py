#!/usr/bin/python

import sys
import re
from datetime import datetime
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection, serializer, compat, exceptions, helpers


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

def make_medline_index():
    request_body ={
        "settings":{
        "number_of_shards" : 5,
        "number_of_replicas":1,
        #"index.codec": "best_compression",
        #"refresh_interval":-1,
        "index.max_result_window": 1000000
        },
        "mappings":{
            "_doc" : {
                "properties": {
                    "pmid": { "type": "keyword"},
                    "doi": { "type": "keyword"},
                    "title": { "type": "text"},
                    "abstract": { "type": "text"},
                    "timestamp": {"type": "date"},
                    "year": {"type": "long"},
                    "type": {"type": "text"}
                }
            }
        }
    }
    es.indices.create(index = 'medline', body = request_body, request_timeout=60)

def make_ngram_index(index_name):
    request_body ={
	    "settings":{
	    "number_of_shards" : 5,
	    "number_of_replicas":1,
        "refresh_interval":-1,
	    "index.max_result_window": 1000000
	    },
	    "mappings":{
	        "_doc" : {
	            "properties": {
	                "pmid": { "type": "keyword"},
	                "type": { "type": "keyword"},
	                "value": { "type": "text"},
	                "count": { "type": "long"}
	            }
	        }
	    }
	}
    es.indices.create(index = index_name, body = request_body, request_timeout=60)


make_ngram_index('medline-unigrams')
make_ngram_index('medline-bigrams')
make_ngram_index('medline-trigrams')
