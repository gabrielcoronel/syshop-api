#! /bin/bash

git ls-files | grep '\.py$' | xargs wc -l
