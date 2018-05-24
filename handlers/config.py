"""Load Configuration."""
# Borrowed from:
# https://github.com/nlindblad/chat-lambda/blob/master/src/config.py

import configparser
import logging as log
import tempfile

import boto3

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
log.basicConfig(filename='snowgetter.log', level=log.INFO, format=FORMAT)


class ConfigFromS3(object):
    """Configuration Class."""

    def __init__(self, bucket_name, key, region_name):
        """Read configuration file from S3 and parse it."""
        defaults = {
            "aws_region": region_name
        }
        session = boto3.session.Session(region_name=region_name)
        self.bucket = session.resource('s3').Bucket(bucket_name)
        temporary_file = tempfile.NamedTemporaryFile()
        self.bucket.download_file(key, temporary_file.name)
        self.config = configparser.ConfigParser(defaults=defaults)
        with open(temporary_file.name, 'r') as f:
            self.config.readfp(f)
        temporary_file.close()
