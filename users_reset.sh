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
    -c               : check login
    -g <group>       : add to group
    -r               : reset password 
    -o               : reset otp";
    exit 1; 
}

while getopts H:l:p:g:croh flag
do
    case "${flag}" in
        H) host=${OPTARG};;
        l) login=${OPTARG};;
        p) password=${OPTARG};;
        g) group=${OPTARG};;
        i) otp_issuer=${OPTARG};;
        e) enigma_host=${OPTARG};;
        c) check=1;;
        r) reset=1;;
        o) otp=1;;
        h) usage;;
        *) usage;;
    esac
done

python3 users_reset.py host=$host login=$login password=$password group=$group enigma_host=$enigma_host otp_issuer=$otp_issuer reset=$reset otp=$otp check=$check
