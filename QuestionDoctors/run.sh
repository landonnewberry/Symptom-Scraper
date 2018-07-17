#!/bin/bash
file=../data/qd_corpus.txt

if [ ! -e "$file" ]; then
    echo "File does not exist"
else 
    rm $file
fi 

python qdscraper.py

