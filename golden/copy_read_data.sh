#!/usr/bin/env bash

IP=192.168.3.53

OUTPUT_DIR=$1

time_stamp=$(date +%Y-%m-%d-%T)

mkdir -p $OUTPUT_DIR/$time_stamp/

scp -r comma@$IP:/data/media/0/realdata/* $OUTPUT_DIR/$time_stamp/