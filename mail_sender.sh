#!/usr/bin/env bash

set -a
source .env
set +a

usage() { 
    echo "Usage: $0
    -S <smtp_server>        : SMTP host
    -L <smtp_username>      : SMTP username
    -P <smtp_password>      : SMTP password
    -s <sender_email>       : Sender E-mail
    -f <csv_file_name>      : csv file name
    -t <template_file_name> : template for mail send
    -b <subject>            : mail subject
    -a <attach_file>        : attach file name";
    exit 1; 
}

while getopts S:L:P:s:f:t:b:a:vh flag
do
    case "${flag}" in
        S) smtp_server=${OPTARG};;
        L) smtp_username=${OPTARG};;
        P) smtp_password=${OPTARG};;
        s) sender_email=${OPTARG};;
        f) csv_file_name=${OPTARG};;
        t) template_file_name=${OPTARG};;
        b) subject=${OPTARG};;
        a) attach_file=${OPTARG};;
        v) verbose=1;;
        h) usage;;
        *) usage;;
    esac
done

python3 mail_sender.py smtp_server=$smtp_server smtp_username=$smtp_username smtp_password=$smtp_password sender_email=$sender_email csv_file_name=$csv_file_name template_file_name=$template_file_name subject=$subject attach_file=$attach_file verbose=$verbose
