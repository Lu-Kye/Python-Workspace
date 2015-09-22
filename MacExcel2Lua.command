#!/bin/sh
# encoding: utf-8

p=$(pwd)
echo "Start Parsing"

# mkdir -p OutCSV

luas_path=$p/luas
rm -rf $luas_path
mkdir -p $luas_path

config_path=$p/../../client-refactory/Develop/Assets/Resources/Script/Config
table_path=$p/../Lua/Table

python excel2lua/excel2lua.py

echo $config_path
echo $luas_path
echo $config_path

rm -rf $config_path
mkdir -p $config_path
cp -a $luas_path/. $config_path

rm -rf $table_path
mkdir -p $table_path
cp -a $luas_path/. $table_path

rm -rf $luas_path

#echo $luas_path/.
