#!/usr/bin/env bash

set -a
source .env
set +a

usage() { 
    echo "Usage: $0
    -e <enigma_host> : enigma host
    -W <write_file>  : csv write file
    -R <read_file>   : csv read file
    -m               : create one time link for mail password";
    exit 1; 
}

while getopts e:R:W:mh flag
do
    case "${flag}" in
        e) enigma_host=${OPTARG};;
        W) write_file=${OPTARG};;
        R) read_file=${OPTARG};;
        m) mail_password=1;;
        h) usage;;
        *) usage;;
    esac
done

python3 generate_onetime_password_for_mail.py write_file=$write_file read_file=$read_file enigma_host=$enigma_host mail_password=$mail_password
