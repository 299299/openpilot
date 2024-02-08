#!/bin/bash

 IP=192.168.3.53

 files=`git diff --name-only`
 for file in $files; do
   #echo $file
   set -x
   scp -r root@$IP:/data/openpilot/$file
   set +x