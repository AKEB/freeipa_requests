#!/usr/bin/env bash

set -a
source .env
set +a

usage() { 
    echo "Usage: $0
    -H <host>     : freeipa host with https://
    -l <login>    : freeipa admin login
    -p <password> : freeipa admin password
    -u <username> : freeipa username
    -c            : check login
    -g <group>    : add to group
    -r            : reset password 
    -o            : reset otp";
    exit 1; 
}

while getopts H:l:p:g:roh flag
do
    case "${flag}" in
        H) host=${OPTARG};;
        l) login=${OPTARG};;
        p) password=${OPTARG};;
        g) group=${OPTARG};;
        u) username=${OPTARG};;
        c) check=1;;
        r) reset=1;;
        o) otp=1;;
        h) usage;;
        *) usage;;
    esac
done

python3 freeipa.py host=$host login=$login password=$password username=$username group=$group reset=$reset otp=$otp check=$check
