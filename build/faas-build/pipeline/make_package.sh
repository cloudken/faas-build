#!/bin/sh

# input
if [ $# -ne 2 ]; then
    echo "usage: ./make_package.sh base_package faas_package"
    exit 1
fi
base_package=$1
faas_package=$2

tar xvfz $base_package
tar xvfz $faas_package
rm -f $base_package
mv cloudframe* cloudframe
rm -rf cloudframe/cloudframe/resource
cp -rf faasframe*/cloudframe/resource cloudframe/cloudframe/
cd cloudframe
mkdir -p dist
python setup.py sdist
cd ..
cp -f cloudframe/dist/cloudframe-*.tar.gz faas-worker/
