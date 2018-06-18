"""Returns temporary aws credentials."""
import logging as log

import boto3

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
log.basicConfig(filename='terrasnow_enterprise.log', level=log.INFO,
                format=FORMAT)

sts = boto3.client('sts')


def get_assume_role_input(role_arn, duration):
    """Create input for assume_role."""
    return {
        'RoleArn': role_arn,
        'RoleSessionName': 'terrasnow_enterprise',
        'DurationSeconds': duration
    }


def assume_role(**kwargs):
    """Assume stack update role."""
    response = sts.assume_role(**kwargs)
    log.info("assume_role: {}".format(response))
    return response


def get_elevated_session_input(response):
    """Create input for get_elevated_session."""
    return {
     'aws_access_key_id': response['Credentials']['AccessKeyId'],
     'aws_secret_access_key': response['Credentials']['SecretAccessKey'],
     'aws_session_token': response['Credentials']['SessionToken']
    }


def get_assumed_role_credentials(role_arn, duration):
    """Return assumed role."""
    assume_role_input = get_assume_role_input(role_arn, duration)
    assume_role_response = assume_role(**assume_role_input)
    log.info("Assumed role: {} for {} seconds".format(role_arn, duration))
    return get_elevated_session_input(assume_role_response)
