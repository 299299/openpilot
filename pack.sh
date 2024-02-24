#!/bin/bash

cd ..

rm -rf op/

cp -rf openpilot/ op/

cd op/

rm -rf .git/

cd ..

zip -r op.zip op/