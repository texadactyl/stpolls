#!/bin/bash 
function oops {
	echo
	echo '*** oops, '$1' ***'
	echo
	exit 86
}

INTERNET_CSV_FILE='pres_polls.csv'
LOCAL_CSV_FILE='data/input.csv'

if [ -d data]; then
    rm -rf data
fi

if [ -r $LOCAL_CSV_FILE ]; then
    rm $LOCAL_CSV_FILE
fi

wget 'https://www.electoral-vote.com/evp2020/Pres/'$INTERNET_CSV_FILE
if [ $? -ne 0 ]; then 
    oops "wget failed"
fi
mv $INTERNET_CSV_FILE $LOCAL_CSV_FILE
