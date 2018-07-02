# Installation

## Assumptions

- You have a working familiarity with terraform module development and terraform based resource deployment within AWS
- You have a passing understanding of ServiceNow workflows

## Requirements

- Admin access to your AWS account
- Latest version of terraform installed on your local machine
- Pre-configured [Gitlab](https://about.gitlab.com/) instance
- Pre-configured ServiceNow Instance
- A MidServer deployed in your AWS account that has been associated with your target ServiceNow instance

NOTE: all of these services can be used with TerraSnow Enterprise in their SaaS form(s) with the exception of the Mid Server.

## Setup

Start by first cloning this repo to your local machine.

NOTE: Configuration management is pretty messy right now in terms of `sys_id` associations in regards to the catalog, category, and workflow. A future release will aim to simplify this.

### ServiceNow

NOTE: These procedures outline installing this project without an associated ServiceNow application and will be built within the global scope. However, all ServiceNow scripts/workflows have been written to work within a scoped application.

#### MID Server

Deploy a mid server into your AWS environment.

#### API User

1. Create an account on your ServiceNow instance that has the following roles:

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
2. Create a category for your catalog
3. Copy the `sys_id` of the catalog (Retrievable from the sys_id option of the right click context menu in the catalog list view) and update the value of `self.catalogs` in `project_root\handlers\snow_cat_item.py`
4.  Copy the `sys_id` of your category (retrievable from the sys_id option of the right click context menu in the catalog Categories tab) and update the value of `self.category` in `project_root\handlers\snow_cat_item.py`
5. save your changes to `snow_cat_item.py`

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

For the three workflow activities listed here that require variable replacement ensure you replace `YOUR_WEBHOOK_URL` and `YOUR_MIDSEVER_DNS_NAME` with your environment specific details.

3. Once your workflow has been created copy its `sys_id` and update the value of `self.workflow` in `project_root\handlers\snow_cat_item.py`


### TerraSnow Instance

This instance will perform all the 'heavy lifting' when it comes to building the catalog item(s) within ServiceNow as well as the Workspace creation within Terraform Enterprise when the catalog item is ordered.

#### Deployment

1. Navigate to the scripting_host folder and create a `terraform.tfvars` file specific to your target AWS env
2. Configure your local env to target the correct AWS account either via the [AWS cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) or by modifying the provider block in `main.tf`
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
