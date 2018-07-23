# Scripting Host

Documentation that outlines the configuration of the terraform deployable scripting host.

## Module Input Variables

**Variable**: `subnet_id`
**Description**: The target subnet id for the TerraSnow instance

**Variable**: `env_type`
**Description**: Suffix added to the instance name (dev, test, prod, etc.)

**Variable**: `alias_name`
**Description**: Value used in building the instance name and the instance domain name.

**Variable**: `target_r53_zone`
**Description**: Target route 53 zone in which to build the resulting domain name entry.

**Variable**: `pub_access_sg`
**Description**: The security group within the target AWS account that allows public access.

**Variable**: `priv_access_vpc_id`
**Description**: ID of the VPC that provides private access within the target AWS account.

**Variable**: `priv_alb_subnets`
**Description**: List of subnets that are backed by the private ALB.

**Variable**: `subnet_id`
**Description**: The id of the security group in which to place the instance

**Variable**: `sg_allow_inbound_from`
**Description**: Source security group to allow inbound traffic into the instance's private security group.

**Variable**: `instance_type`
**Description**: AWS instance type (t2.micro, t2.medium, etc.)

**Variable**: `key_name`
**Description**: SSH public key used to login to the TerraSnow instance.

**Variable**: `instance_role`
**Description**: Role to associate with the TerraForm Scripting host instance. Requires read access to the S3 bucket where the TerraSnow configuration file is stored.

**Variable**: `private_gitlab_server`
**Description**: "hostname of the gitlab server. ex: gitlab.mydomain.net. Passed as a variable into the TerraSnow host initialization script. Used to add the gitlab host as a trusted ssh endpoint and enable use of `git clone` via SSH.

## Outputs

**Variable**: `_private_ip`
**Value**: IPv4 IP address
**Description**: The private IP address of the TerraSnow instance

**Variable**: `aws_assume_role_webhook`
**Value**: https://INSTANCE_FQDN/aws-assume-role-webhook
**Description**: The AWS assume role API endpoint of the TerraSnow instance

**Variable**: `gitlab_webhook`
**Value**: https://INSTANCE_FQDN/gitlab-webhook
**Description**: The gitlab webhook endpoint of the TerraSnow instance

**Variable**: `pub_deployment_key`
**Value**: https://INSTANCE_FQDN/pub-key/key.txt
**Description**: The web accessible path to the public key of the TerraSnow instance. This key is added to the target gitlab repo as a [deploy key](https://docs.gitlab.com/ee/ssh/#per-repository-deploy-keys) with read access to enable the TerraSnow instance to successfully `git clone`.

**Variable**: `tfe_workflow_webhook`
**Value**: https://INSTANCE_FQDN/workflow-webhook
**Description**: The Terraform Enterprise workspace API endpoint of the TerraSnow instance.

**Variable**: `sn_variables_webhook`
**Value**: http://INSTANCE_FQDN/variables-webook
**Description**: The webhook that triggers the ServiceNow catalog item variables.

## Overview

The included terraform module will deploy the following resources.

### Terraform Enterprise Scripting Host

**Description**: An EC2 instance of the size of your choosing (via the `instance_type` variable).

**Requirements**:
- An IAM role that at a minimum has read access to the S3 bucket where the TerraSnow configuration file is stored.
- An AWS environment that has a security group that provides public access. Port 443 is required as all communications done with the TerraSnow api endpoints are over https via the TerraSnow alb.

### Application Load balancer

**Description**: Created via the included `alb` module. An ALB that proxies http connections from the TerraSnow instance to https. Backed by an AWS issued https certificate.

**Requirements**: A separate public access security group within the target AWS account.

### TerraSnow Initialization Script

**Description**: A bash script that will install and configure the flask application on an EC2 instance.

**Requirements**: The EC2 instance on which this script is run will require internet access.
