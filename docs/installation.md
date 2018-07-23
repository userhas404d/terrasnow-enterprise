# Installation

The following instructions outline how to install TerraSnow Enterprise using the included terraform deployable host that is maintained in this project's repo under `/scripting_host`.

## Assumptions

- A working familiarity with terraform module development and terraform based resource deployment within AWS
- A passing understanding of ServiceNow workflows

## Requirements

- Admin access to the target AWS account
- Latest version of terraform installed locally
- Pre-configured [Gitlab](https://about.gitlab.com/) instance
- Pre-configured ServiceNow Instance
- A MidServer deployed in the target AWS account that has been associated with the target ServiceNow instance
- Web console access to Terraform Enterprise

NOTE: All of these services can be used with TerraSnow Enterprise in their SaaS form(s) with the exception of the ServiceNow MidServer.


## Setup

Start by first cloning the [TerraSnow Enterprise](https://github.com/userhas404d/terrasnow-enterprise/) repo.

NOTE: Configuration management aims to be as consolidated as possible through the use of a config file. However, there are some caveats so please read through this documentation carefully.

### Configuration File

Terraform Enterprise and ServiceNow environment specific details are stored within a configuration file.
These settings are pulled from this configuration automatically and as needed.

This file must be stored in an S3 bucket that is read-accessible by the TerraSnow instance. Additionally it is recommended that this file be stored in an encrypted S3 bucket due to its sensitive nature.

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

[TERRAFORM_ENTERPRISE]
INSTANCE_NAME=
ATLAS_TOKEN=
```

#### ServiceNow

Overview of the `config.ini` settings for ServiceNow specific information

| Value              | Description                                                     |
|--------------------|-----------------------------------------------------------------|
| INSTANCE_NAME      | url of the target ServiceNow instance ex: https://mysninstance.com    |
| SN_API_USER_NAME   | user name of the user performing API actions against ServiceNow |
| SN_API_USER_PWD    | password of the user performing API actions against ServiceNow  |
| TF_CATALOG         | sys_id of the target Catalog                                    |
| CATEGORY           | sys_id of the target Category                                   |
| TFE_WORKFLOW       | sys_id of the TF catalog item order workflow                    |

#### Terraform enterprise

Overview of the `config.ini` settings for Terraform Enterprise specific information

| Value              | Description                                                  |
|--------------------|--------------------------------------------------------------|
| INSTANCE_NAME      | url of the target TFE instance ex: https://app.terraform.io        |
| ATLAS_TOKEN        | User API access token to create and populate TFE workspaces  |

### ServiceNow

NOTE: These procedures outline installing this project without an associated ServiceNow application and will be built within the global scope. However, all ServiceNow scripts/workflows have been written to work within a scoped application.

#### MID Server

Deploy a mid server into the target AWS environment. This mid server will be making the api calls against TerraSnow in order to deploy resources against terraform enterprise.

#### API User

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

2. Keep the username and password of this user on hand for addition into the Terrasnow configuration file

#### Terraform Catalog

1. Create a new catalog within ServiceNow by using the instructions in the following [link](https://docs.servicenow.com/bundle/helsinki-it-service-management/page/product/service-catalog-management/task/t_DefineCatalogDetails.html) or with the ServiceNow shortcut `sc_catalog.list`
2. Create a category for the terraform resources catalog
3. Copy the `sys_id` of the catalog (Retrievable from the sys_id option of the right click context menu in the catalog list view) and update the value of `TF_CATALOG` in `config.ini`
4.  Copy the `sys_id` of the terraform resources catalog category (retrievable from the sys_id option of the right click context menu in the catalog Categories tab) and update the value of `CATEGORY` in `config.ini`

#### Order Workflow

1. Create a new workflow in ServiceNow using the following instructions [here](https://docs.servicenow.com/bundle/jakarta-servicenow-platform/page/administer/workflow-administration/task/t_CreateAWorkflow.html)
2. Create 4 Run Script activities (Core > Utilities > Run Script), link them, and populate them with the following scripts via copy paste:

NOTE: It is useful when troubleshooting to capture Run Script activity content via log message activities during activity transitions.

| Order | Script Name                       | Requires variable replacements    |
|-------|-----------------------------------|-----------------------------------|
| 1     | CreateWebhookRequestBodies.js     | NO                                |
| 2     | SendTFEWorkflowCreationRequest.js | YES                               |
| 3     | SendTFEVariablesRequest.js        | YES                               |
| 4     | SendUploadConfigRequest.js        | YES                               |

For the three workflow activities listed here that require variable replacement ensure `YOUR_WEBHOOK_URL` and `YOUR_MIDSEVER_DNS_NAME` are replaced with environment specific details.

3. Once the workflow has been created copy its `sys_id` and update the value of `self.workflow` in `config.ini`


### Terraform Enterprise

NOTE: Testing and development was done against Terraform Enterprise using a single Organization.

#### User API Token

1. Generate an API token for a Terraform Enterprise user: `TFE console > User Settings > Tokens`
2. Update the value of `ATLAS_TOKEN` in `config.ini`

### TerraSnow Instance

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
