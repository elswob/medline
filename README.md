# medline
Create a basic local medline instance for high throughput informatics

## Motivation

NCBI requests that eutils requests be limited to 3/second, which makes some high throughput analyses of
Pubmed data challenging.  It is not difficult to create your own local version of Pubmed/medline built on 
ElasticSearch (a convenient REST interface and management system layered on top the Lucene indexing and
search library).

## Pre-requisites

You will need a recent version of the Java Runtime Environment (OpenJDK's JRE or Oracle's JRE), and python
to follow the steps outlined below.  In a Debian type environment, these requirements can be met like so:

```
sudo apt-get update
sudo apt-get install python
sudo apt-get install python-pip
sudo apt-get install openjdk-8-jre-headless 
sudo pip install elasticsearch
```

You will also need about 200GB of free disk space to hold the Medline data files for indexing.  However,
these XML files hold a lot of information we will not retain, so the final ElasticSearch index is < 10GB.

Finally, you will need [ElasticSearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html).  

## Download the data

First we generate a file list for wget.  You can just do this by cut and paste in your favorite editor, but
we can also accomplish it via the command line:

```
wget ftp.ncbi.nlm.nih.gov/pubmed/baseline
grep -o -P 'medline.*?.gz' baseline | uniq |
sed -e 's/^/ftp:\/\/ftp.ncbi.nlm.nih.gov\/pubmed\/baseline/' > filelist

```

Then fetch the files:

```
wget -i filelist
gunzip *.gz

```

Or if you have multiple cores, which of course you do, you can speed things up with `xargs` (here for 8 cores):

```
cat filelist | xargs -n 1 -P 8 wget
ls *.gz | xargs -n 1 -P 8 gunzip
```

## Index the data

Now all we need to do is load and index the data into elasticsearch.  Assuming elastic search is running on your
local machine on port 9200, it's as easy as:

```
ls *.xml | xargs -n 1 -P ./parse_bulk.py
```

This creates a 'medline' index on elasticsearch, loads the records, and indexes them.  This will take a couple hours.
Check the logfile created (parse.log) to make sure everything went ok.  In particular,
review the outpuf of

```
grep root parse.log
```

To make sure 30,000 records were imported from each xml file (except the last one which will have fewer). You can get an
exact counts of records uploaded thusly:

```
grep root ../parse.log | cut -f 3 -d' ' | paste -sd+ | bc

```

It should be around 29 million.

Note that the sciprt parse_bulk.py is pretty basic.  It extracts just PMID, title, and abstract from each record in the XML
files, and then indexes them with the standard analyzer.  This is a reasonable approach (the standard analyzer is well
suited for english language and runs everything through a lower case transform for case-insensitive searching).  However,
you might want to import more fields and/or be more sophisticated with your indexing.  Hopefully the script is a useful
starting point.

## To Do

We need to also download and index the daily update files for records added since the previous annual baseline.  Exact same
approach should work, but with the files in ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/.