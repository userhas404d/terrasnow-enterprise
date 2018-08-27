# Installation

TerraSnow is maintained in two separate repositories.

The first maintains the TerraSnow Enterprise Instance and backing code as a terraform deployable host. It is maintained in this project's repo under `/scripting_host`.

The second repository hosts the accompanying [ServiceNow scoped application](https://github.com/userhas404d/terrasnow-enterprise-scoped-app).

## Overview
1. [Configure ServiceNow](###Configure-ServiceNow)
    1. [Create the TerraSnow Configuration File](####Create-the-TerraSnow-Configuration-File)
    2. [Configure/Deploy your MID Server](####Configure/Deploy-your-MID-Server)
    3. [Install the TerraSnow Scoped Application](####Install-the-TerraSnow-Scoped-Application)
    4. [Associate the TerraSnow application with your MID server](####Associate-the-TerraSnow-application-with-your-MID-server)
    4. [Create the TerraSnow API User](####Create-the-TerraSnow-API-User)
    5. [Collect the required sys_ids](####Collect-the-required-sys_ids)
2. [Configure Terraform Enterprise](###Configure-Terraform-Enterprise)
3. [Upload the TerraSnow Configuration file to S3](###Upload-the-configuration-file-to-S3)
4. [Deploy the TerraSnow Instance](###Deploy-the-TerraSnow-Instance)
5. [Proceed to the usage section to create your first terraform catalog item](doc:usage)

## Assumptions

- Working familiarity with terraform module development and terraform based resource deployment within AWS
- Passing understanding of ServiceNow application development
- Familiarity with AWS IAM role assignment and configuration

## Requirements

- Admin access to the target AWS account
- The [latest version of terraform](https://www.terraform.io/downloads.html) installed on the machine from which the TerraSnow Instance template will be deployed
- Pre-configured [Gitlab](https://about.gitlab.com/) instance
- Pre-configured ServiceNow Instance
- Web console access to Terraform Enterprise
- A MID Server
  > **NOTE:**
  >
  > ######MID Server:
  > The MID Server must be deployed in the target AWS account with an instance role that has been granted assume role privileges to the accounts in which terraform resources will be deployed.
  >
  > The MID Server must be associated with your ServiceNow instance
  >
  > ######SaaS vs. Self Hosted:
  > All of these services can be used with TerraSnow Enterprise in their SaaS form(s) with the exception of the ServiceNow MidServer.


## Setup

1. Clone the [TerraSnow Enterprise](https://github.com/userhas404d/terrasnow-enterprise/) repo to your workstation.

2. Create a file called `config.ini` in the root of the `terrasnow-enterprise` directory. See the [Configuration File](### Configuration File) section of this document for this file's structure.

3. Fork the [TerraSnow Enterprise Scoped Application](https://github.com/userhas404d/terrasnow-enterprise-scoped-app) project into a personal repo.

>**NOTE:** The scoped application can be loaded into your ServiceNow instance directly from this repo. However, you will be unable to commit any local changes you make unless you follow [these steps](https://community.servicenow.com/community?id=community_blog&sys_id=d2cc6265dbd0dbc01dcaf3231f9619ee) to point your application at a different repository.

###Configure ServiceNow

The following instructions outline the steps required to configure your ServiceNow instance for use with the TerraSnow application.

####Create the TerraSnow Configuration File

>**NOTE:** Terraform Enterprise and ServiceNow environment specific details are stored within a configuration file.
>
>These settings are pulled by the TerraSnow Instance automatically and as needed.

This file must be stored in an S3 bucket that is read-accessible by the TerraSnow instance (configurable via the associated AWS Instance Role). Additionally, it is recommended that this file be stored in an encrypted S3 bucket due to its sensitive nature.

The expected file structure is as follows:

File Name: `config.ini`

Contents:
```
[SERVICENOW]
INSTANCE_NAME=
SN_API_USER_NAME=
SN_API_USER_PWD=
TF_CATALOG=
CATEGORY=
TFE_WORKFLOW=
SYS_PACKAGE=

[TERRAFORM_ENTERPRISE]
INSTANCE_NAME=
ATLAS_TOKEN=
```

####ServiceNow

Overview of the `config.ini` settings for ServiceNow specific information

| Value              | Description                                                     |
|--------------------|-----------------------------------------------------------------|
| INSTANCE_NAME      | url of the target ServiceNow instance ex: https://mysninstance.com    |
| SN_API_USER_NAME   | user name of the user performing API actions against ServiceNow |
| SN_API_USER_PWD    | password of the user performing API actions against ServiceNow  |
| TF_CATALOG         | sys_id of the target Catalog                                    |
| CATEGORY           | sys_id of the target Category                                   |
| TFE_WORKFLOW       | sys_id of the TF catalog item order workflow                    |
| SYS_PACKAGE        | sys_id of the TerraSnow scoped application                      |

####Terraform enterprise

Overview of the `config.ini` settings for Terraform Enterprise specific information

| Value              | Description                                                  |
|--------------------|--------------------------------------------------------------|
| INSTANCE_NAME      | url of the target TFE instance ex: https://app.terraform.io        |
| ATLAS_TOKEN        | User API access token to create and populate TFE workspaces  |


####Configure/Deploy your MID Server

Deploy a MID server into the target AWS environment. This mid server will be making the API calls against the TerraSnow Instance in order to deploy resources against TerraForm Enterprise.

> **NOTE:**
>
> The MID Server must be deployed in the target AWS account with an instance role that has been granted assume role privileges to the accounts in which terraform resources will be deployed.
>
> The MID Server must be associated with your ServiceNow instance
>

####Install the TerraSnow Scoped Application

Import the TerraSnow scoped application from your personal repo by following the official ServiceNow instructions for [Importing applications from source control](https://docs.servicenow.com/bundle/kingston-application-development/page/build/applications/task/t_ImportAppFromSourceControl.html).

####Associate the TerraSnow application with your MID server

1. From your ServiceNow instance navigate to `Service Mapping` > `MID Servers`
2. Select the MID server that was deployed to your target AWS account.
3. Select the `Supported Applications` tab and click `Edit...`
4. Add `terraform-snow` and confirm that it now shows in the `Supported Applications` list

####Create the TerraSnow API User

1. Create an account on the ServiceNow instance that has the following roles:

| role_name                  | requirement  |
|----------------------------|--------------|
| admin                      | place_holder |
| api_analytics_read         | place_holder |
| catalog_editor             | place_holder |
| catalog                    | place_holder |
| catalog_admin              | place_holder |
| credential_admin           | place_holder |
| rest_api_explorer          | place_holder |
| user_criteria_admin        | place_holder |
| web_service_admin          | place_holder |

2. Add the user name and the user's password to the values for `SN_API_USER_NAME` and `SN_API_USER_PWD` respectively in `config.ini`

> **NOTE:** You _must_ login to your ServiceNow instance with this user at least once and select the `terraform-snow` application scope.
> If you fail to do so TerraSnow catalog items will be created in the global scope.

####Collect the required sys_ids

##### From the Terraform Resources Catalog

1. Within the TerraSnow Scoped application locate the Terraform Template Catalog (`Terraform Resources Scoped App`)
2. Copy the `sys_id` of the catalog (Retrievable from the sys_id option of the right click context menu in the catalog list view) and update the value of `TF_CATALOG` in `config.ini`
3. Copy the `sys_id` of the terraform resources catalog category (retrievable from the sys_id option of the right click context menu in the catalog Categories tab) and update the value of `CATEGORY` in `config.ini`

##### From the Terraform Resources Workflow

1. Locate the `terrasnow-enterprise - scoped` workflow within the TerraSnow scoped application
2. From the workflow properties context menu, right click and copy its `sys_id`
3. Update the value of `TFE_WORKFLOW` in `config.ini`


###Configure Terraform Enterprise

>**NOTE:** Testing and development was done against Terraform Enterprise using a single Organization.

### Generate a user API Token

1. Generate an API token for a Terraform Enterprise user: `TFE console > User Settings > Tokens`
2. Update the value of `ATLAS_TOKEN` in `config.ini`

###Upload the configuration file to S3

Requirements:

1. This bucket _must_ be private
2. The IAM Instance Role that is assigned to the TerraSnow Instance must have read access to this bucket

Recommendations:

1. Ensure the bucket is encrypted.
2. Configure the bucket with versioning to prevent inadvertent loss of information

###Deploy the TerraSnow Instance

This instance will perform all the 'heavy lifting' when it comes to building the catalog item(s) within ServiceNow as well as the Workspace creation within Terraform Enterprise when the catalog item is ordered.

#### Deployment

NOTE: Successful deployment requires that the environment specific configuration file has been populated with the correct information and uploaded to S3.

1. Navigate to the scripting_host folder and create a `terraform.tfvars` file specific to the target AWS env
2. Configure the local env to target the correct AWS account either via the [AWS cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) or by modifying the provider block in `main.tf`
3. Run `terraform apply`
4. Proceed to the usage section for catalog item creation and gitlab repo configuration.

#### API Endpoints

On successful deployment the instance is configured with the following endpoints:

| Endpoint                   | Description                                                                                                                  |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------|
| `/`                        | Sends `200` regardless of content, used for testing                                                                          |
| `/aws-assume-role-webhook` | Listens for AWS assume role data, creates the required TFE credential env vars                                               |
| `/gitlab-webhook`          | Listens for tag update events sent from gitlab and creates the associated SN catalog item                                    |
| `/tfe-run-webhook`         | Listens for workflow run events, uploads the source terraform module to the target workspace to trigger a TFE workflow event |
| `/variables-webhook`       | Listens for ServiceNow variables creation requests, sends associated API call to SN to create the variable                   |
| `/workflow-webhook`        | Listens for TFE workspace creation events, creates an empty workspace                                                        |

#### Create your first Terraform Catalog item

See the [usage](doc:usage) section of this guide for more details.
