#!/usr/bin/env bash

set -a
source .env
set +a

usage() { 
    echo "Usage: $0
    -H <host>        : freeipa host with https://
    -l <login>       : freeipa admin login
    -p <password>    : freeipa admin password
    -i <otp_issuer>  : otp issuer
    -e <enigma_host> : enigma host
    -W <write_file>  : csv write file
    -R <read_file>   : csv read file
    -c               : check login
    -g <group>       : add to group
    -r               : reset password
    -o               : reset otp";
    exit 1; 
}

while getopts H:l:p:g:R:W:fvcroh flag
do
    case "${flag}" in
        H) host=${OPTARG};;
        l) login=${OPTARG};;
        p) password=${OPTARG};;
        g) group=${OPTARG};;
        i) otp_issuer=${OPTARG};;
        e) enigma_host=${OPTARG};;
        W) write_file=${OPTARG};;
        R) read_file=${OPTARG};;
        v) verbose=1;;
        c) check=1;;
        r) reset=1;;
        f) fix=1;;
        o) otp=1;;
        h) usage;;
        *) usage;;
    esac
done

python3 users_reset.py fix=$fix host=$host login=$login password=$password write_file=$write_file read_file=$read_file group=$group enigma_host=$enigma_host otp_issuer=$otp_issuer reset=$reset otp=$otp check=$check verbose=$verbose
