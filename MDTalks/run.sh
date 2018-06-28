#!/bin/bash
file=../data/mdtalks_corpus.txt

if [ ! -e "$file" ]; then
    echo "File does not exist"
else 
    rm $file
fi 

python mdtalksscraper.py

