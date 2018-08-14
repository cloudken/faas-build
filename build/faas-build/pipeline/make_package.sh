#!/bin/bash

# input
if [ $# -ne 2 ]; then
    echo "usage: ./make_package.sh base_package faas_package"
    exit 1
fi
base_package=$1
faas_package=$2

tar xvfz base_package
tar xvfz faas_package
rm -f base_package
mv cloudframe* cloudframe
cp -rf faasframe/resource cloudframe/cloudframe/
cd cloudframe
mkdir -p dist
cd dist
rm -f cloudframe-*.tar.gz
cd ..
python setup.py sdist
cp -f dist/cloudframe-*.tar.gz build/faas-build/
