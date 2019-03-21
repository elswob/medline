#cronttab
#0 0 * * * /bin/bash /path/to/update_daily.sh >> /home/be15516/projects/medline/update_log.txt-

threads=4

#use virtualenv
cd /home/be15516/projects/medline
. ./venv3/bin/activate

echo `date`
#download daily data
wget -O dailyUpdates.txt ftp.ncbi.nlm.nih.gov/pubmed/updatefiles
#parse file names
grep -o -P 'pubmed.*?.gz' dailyUpdates.txt | uniq > dailyFiles.txt
#check against existing
comm -3 <(cat dailyFiles.txt | sort) <(ls  data/daily/ | sort) | sed -e 's/^/ftp:\/\/ftp.ncbi.nlm.nih.gov\/pubmed\/updatefiles\//' > newFiles.txt
#download new ones
if [ -s newFiles.txt ]
then
    echo 'Getting new data'
    cat newFiles.txt | xargs -n 1 -P $threads wget -N -P dailyTmp
    #uncompress
    ls dailyTmp/*.gz | xargs -n 1 -P $threads gunzip
    #index the medline data
    echo 'Indexing medline data'
    ls dailyTmp/*.xml | xargs -n 1 -P $threads python3 parse_bulk.py
    #create ngrams
    echo 'Creating and indexing ngrams'
    #index ngrams
    ls dailyTmp/*.xml | xargs -n 1 -P $threads python3 parse_daily_ngrams.py
    #clean up
    ls dailyTmp/*.xml | xargs -n 1 -P $threads gzip
    mv dailyTmp/* data/daily/
else
    echo 'No new data'
fi
#rm updatefiles
#sed -e 's/^/ftp:\/\/ftp.ncbi.nlm.nih.gov\/pubmed\/updatefiles\//' > filelist
#cat filelist | xargs -n 1 -P 8 wget
#ls *.gz | xargs -n 1 -P 8 gunzip
#ls data/daily/*.xml | xargs -n 1 -P 10 python parse_bulk.py
