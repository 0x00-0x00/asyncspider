#!/bin/bash

if [[ $# < 2 ]]; then
    echo "Uso: $0 -f PASTA_DE_ARQUIVOS"
    exit 0
fi

while getopts "f:" opt; do
    case $opt in
        f)folder=$OPTARG;;
        ?);;
    esac
done

if [[ $folder == "" ]]; then
    exit 0
fi


md5sum $folder/* | sort | awk {'print $1'} | uniq -c | sort | awk {'print $2": "$1'}
