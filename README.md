## Terrasnow-Enterprise

### Description
Enables the deployment of AWS resources from ServiceNow via Terraform Enterprise

### Overview

This project contains a terraform template to deploy a Ngnix reverse proxied, Flask based endpoint that handles Gitlab [`Tag`](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#tag-events) and [`Push`](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#push-events) events by creating a ServiceNow Terraform Module Catalog Item in the Terraform Resources Catalog that is contained in [this](https://github.com/userhas404d/terraform-snow) companion project

### Requirements

- Pre-configured AWS account
- Latest version of terraform installed on your local machine
- Pre-configured Gitlab instance
- Pre-configured ServiceNow Instance
- Pre-configured Terraform Enterprise Instance
- Credentials of ServiceNow user with API access

### How to Use

#### Adding Terraform Modules to ServiceNow Catalog
*Note: Module repositories must meet the same requirements as those outlined for addition to the [Terraform Module Private Registry](https://www.terraform.io/docs/enterprise/registry/publish.html)*
1. Create a Gitlab repo with the `terraform-<PROVIDER>-<MODULE_NAME>` name format
2. Add the terraform scripting host (tfsh) url as a webhook under Repo > Settings > Integrations
    - Select `Tag push events` and `Enable SSL verification`
    - Click the `Add Webhook` button to complete
3. Add the terraform scripting host public key to the repo
4. Add a version tag to your project before commit that follows the [PEP 440](https://www.python.org/dev/peps/pep-0440/) standard (ex: 1.0.2)

#### Deploying Terraform Resources from ServiceNow

### Setup

#### ServiceNow
- ServiceNow instance REST api account credentials

#### Terraform Enterprise
- Generate a [USER oauth token](https://www.terraform.io/docs/enterprise/users-teams-organizations/users.html)
- Add Gitlab as a [VCS](https://www.terraform.io/docs/enterprise/vcs/index.html) in your Terraform Enterprise organization

#### Generate conf.ini
Create this file and upload it to an encrypted S3 bucket.
```
[SERVICENOW]
INSTANCE_NAME=
SN_API_USER_NAME=
SN_API_USER_PWD=

[TERRAFORM_ENTERPRISE]
INSTANCE_NAME=
ATLAS_TOKEN=
```

#### Scripting Host (Deploy it)
1. Clone this repo
2. Configure your local env to target the correct AWS account
3. Navigate to the `scripting_host` folder and create a `terraform.tfvars` file specific to your target AWS env
4. Run `terraform apply`

#### Gitlab
- Add the `Scripting Host` as an application in your `gitlab` account
- Add the `Scripting Host`'s public key (available at https://yourscriptinghost/pub-key/key.txt) as a [`Deploy Key`](https://www.terraform.io/docs/enterprise/vcs/index.html) with read access

### Workflow Overview

1. A Gitlab project is created for the source terraform module and associated with the webhook listener on tag update
2. When the webhook receives a tag update event it queries the target servicenow instance for a catalog item matching the project name and version number.
- if a catalog item is not found it creates a new one
- if a catalog item is found and the version is the same as the previous it takes no action
3.
