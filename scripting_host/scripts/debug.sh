#!/bin/bash

# fips enable /werkzeug/debug/__init__.py

sed -i '171s/md5/sha256/' /home/maintuser/terrasnow/flask/lib64/python3.4/site-packages/werkzeug/debug/__init__.py
