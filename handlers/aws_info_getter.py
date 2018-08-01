"""Retrieve JSON obj of required account information."""

import datetime
import logging

import boto3
import dateutil.parser
from botocore.client import Config
from botocore.exceptions import ClientError, ParamValidationError


class AwsInfoGetter(object):
    """AWS info retriever."""

    def __init__(self, region, role_to_assume_arn, duration):
        """Initialize."""
        self.region = self.get_region(region)
        self.ec2 = boto3.client(
          'ec2', region_name=self.region, config=Config(
            read_timeout=120, retries={"max_attempts": 10}))
        self.sts = boto3.client('sts', region_name=self.region)
        self.role_to_assume_arn = role_to_assume_arn
        self.duration = duration

    def get_region(self, region):
        """Get AWS region."""
        if not region:
            region = "us-east-1"
        return region

    def get_assume_role_input(self, role_arn, duration):
        """Create input for assume_role."""
        return {
            'RoleArn': role_arn,
            'RoleSessionName': 'get_account_info_script',
            'DurationSeconds': duration
        }

    def assume_role(self, **kwargs):
        """Assume stack update role."""
        response = self.sts.assume_role(**kwargs)
        logging.info("assume_role: {}".format(response))
        return response

    def get_elevated_session_input(self, response):
        """Create input for get_elevated_session."""
        return {
         'aws_access_key_id': response['Credentials']['AccessKeyId'],
         'aws_secret_access_key': response['Credentials']['SecretAccessKey'],
         'aws_session_token': response['Credentials']['SessionToken']
        }

    def get_elevated_session(self, **kwargs):
        """Create new boto3 session with assumed role."""
        data_retrieval_session = boto3.Session(**kwargs)
        elevated_ec2_client = (
          data_retrieval_session.client('ec2', region_name=self.region))
        return elevated_ec2_client

    def get_sgs(self, assumed_role):
        """Retrieve list of security groups."""
        sgs = []
        response = assumed_role.describe_security_groups()
        for item in response['SecurityGroups']:
            security_group = {}
            for _key in item.items():
                security_group['Name'] = item['GroupName']
                security_group['GroupId'] = item['GroupId']
                security_group['VpcId'] = item['VpcId']
            if security_group:
                sgs.append(security_group)
        return sgs

    def get_linux_amis(self, assumed_role):
        """Retrieve list of linux amis."""
        logging.debug('retrieving linux amis..')
        amis = []
        response = assumed_role.describe_images(
            Filters=[
                {'Name': 'state', 'Values': ['available']},
                {'Name': 'is-public', 'Values': ['true']},
                {'Name': 'owner-id', 'Values': ['701759196663']},
                {'Name': 'virtualization-type', 'Values': ['hvm']}
            ])
        for item in response['Images']:
            ami = {}
            for _key in item.items():
                if(self.date_check(item['CreationDate'])
                   and "spel-minimal-centos-7" in item['Name']):
                    ami['Name'] = item['Name']
                    ami['ImageId'] = item['ImageId']
                    ami['OSType'] = "CentOS"
                elif(self.date_check(item['CreationDate'])
                     and "spel-minimal-rhel-7" in item['Name']):
                    ami['Name'] = item['Name']
                    ami['ImageId'] = item['ImageId']
                    ami['OSType'] = "RHEL7"
            if ami:
                amis.append(ami)
        return amis

    def get_windows_amis(self, assumed_role):
        """Retrieve list of windows amis."""
        logging.debug('retrieving windows amis..')
        amis = []
        response = assumed_role.describe_images(
            Filters=[
                {'Name': 'state', 'Values': ['available']},
                {'Name': 'is-public', 'Values': ['true']},
                {'Name': 'owner-alias', 'Values': ['amazon']},
                {'Name': 'virtualization-type', 'Values': ['hvm']}
            ])
        for item in response['Images']:
            ami = {}
            for _key in item.items():
                if(item['CreationDate']
                   and self.date_check(item['CreationDate'])
                   and "Windows_Server-2016-English-Full-Base" in item['Name']
                   and "LongIDTest-" not in item['Name']):
                    ami['Name'] = item['Name']
                    ami['ImageId'] = item['ImageId']
                    ami['OSType'] = "Windows Server 2016"
            # elif(item['CreationDate']
            #      and date_check(item['CreationDate'])
            #      and "Windows_Server-2012-English-Full-Base" in item['Name']
            #      and "LongIDTest-" not in item['Name']):
            #     ami['Name'] = item['Name']
            #     ami['ImageId'] = item['ImageId']
            #     ami['OSType'] = "Windows Server 2012"
            # else:
            #     continue
            if ami:
                amis.append(ami)
        return amis

    def date_check(self, date):
        """Check date is at least 60 days old."""
        # 2018-03-14T19:30:27.000Z
        today = datetime.date.today()
        margin = datetime.timedelta(days=60)
        d = dateutil.parser.parse(date)
        date = datetime.date(d.year, d.month, d.day)
        # check if date is within 60 days of today
        return date + margin >= today

    def get_key_pairs(self, assumed_role):
        """Retrieve list of key pairs."""
        keys = []
        response = assumed_role.describe_key_pairs()
        for item in response['KeyPairs']:
            key = {}
            for _key in item.items():
                key['KeyName'] = item['KeyName']
            if key:
                keys.append(key)
        return keys

    # def get_vpcs(assumed_role):
    #     """Retrieve list of vpcs."""
    #     vpcs = []
    #     response = assumed_role.describe_vpcs(
    #         Filters=[
    #             {'Name': 'state', 'Values': ['available']}
    #         ])
    #     for item in response['Vpcs']:
    #         vpc = {}
    #         for _key in item.items():
    #             try:
    #                 if item['Tags'][0]['Value']:
    #                     vpc['Name'] = item['Tags'][0]['Value']
    #                     vpc['VpcId'] = item['VpcId']
    #             except KeyError as e:
    #                 continue
    #             if vpc:
    #                 vpcs.append(vpc)
    #     return vpcs

    def get_subnets(self, assumed_role):
        """Retrieve list of subnets."""
        subnets = []
        response = assumed_role.describe_subnets(
            Filters=[
                {'Name': 'state', 'Values': ['available']}
            ])
        for item in response['Subnets']:
            subnet = {}
            try:
                if item['Tags'][0]['Value']:
                    subnet['Name'] = item['Tags'][0]['Value']
                    subnet['SubnetId'] = item['SubnetId']
                    subnet['VpcId'] = item['VpcId']
            except KeyError as e:
                continue
            if subnet:
                subnets.append(subnet)
        return(subnets)

    def get_everything(self, assumed_role):
        """Return complete json object with all info."""
        sorted_dict = {}
        logging.debug('retrieving amis..')
        sorted_dict['amis'] = {
                               "linux": self.get_linux_amis(assumed_role),
                               "windows": self.get_windows_amis(assumed_role)
                               }
        logging.debug('retrieving key pairs..')
        sorted_dict['key_pairs'] = self.get_key_pairs(assumed_role)
        logging.debug('retrieving subnets..')
        sorted_dict['subnets'] = self.get_subnets(assumed_role)
        logging.debug('retriveing security groups..')
        sorted_dict['security_groups'] = self.get_sgs(assumed_role)
        logging.debug('returing sorted dictionary of all results..')
        return sorted_dict

    def assumed_role_get_everything(self):
        """Return complete json object with all info."""
        assume_role_input = self.get_assume_role_input(self.role_to_assume_arn,
                                                       self.duration)
        try:
            assume_role_response = self.assume_role(**assume_role_input)
            logging.info(
              "Assumed target role for {} seconds".format(self.duration))
            elevated_session_input = self.get_elevated_session_input(
              assume_role_response)
            elevated_ec2_client = self.get_elevated_session(
              **elevated_session_input)
            logging.info("Retrieved elevated ec2 client.")
            response = self.get_everything(elevated_ec2_client)
            logging.debug('sending response: {}'.format(response))
            return response
        except ParamValidationError as e:
            logging.error(
              "Error occured while attempting to assume the role:" +
              " {}".format(e))
            return "ERROR: Assume role failed"
        except ClientError as e:
            logging.error(
              "Error occured while attempting to assume the role:" +
              " {}".format(e))
            return "ERROR: Assume role failed"


# role_to_assume = "arn:aws:iam::1234567891:role/readOnlyRole"
# mytest = AwsInfoGetter(None, role_to_assume, 900)
# print(mytest.assumed_role_get_everything())
