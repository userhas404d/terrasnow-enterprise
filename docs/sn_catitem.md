# ServiceNow Catalog Item

The details below include descriptions of the variables, client scripts, and script includes utilized in each ServiceNow terraform resource catalog item. Unless otherwise stated variables and client scripts are created automatically.

## Variables

ServiceNow catalog item variables are automatically populated with the default values of their terraform module counterparts. Variables that are defined in the terraform module without a default value are created as required ServiceNow catalog item variables.

The provided terraform module's variable description is populated in both the ServiceNow variable question text and tool tip.

### tfv_

**Type:** String

**Description:** Denotes the prefix given to the variables included in the terraform module's variables.tf file.

### adv_toggle

**Type:** CheckBox

**Description:** Advanced mode toggle that is used to show/hide catalog item variables that are not marked as required.

### Roles

**Type:** Select Box

**Description:** Used in conjunction with the `populateAWSRoleInfoOnLoad.js` client script. Contains the AWS account information for the user's select role.

### gen_OS_Type

**Type:** String

**Description:** not currently in use

### gen_aws_role

**Type:** String

**Description:** Holds the ARN of the role selected from the Roles dropdown. Auto filled via the `enableAfterPopulateRolesOnChange.js` OnChange event

### gen_AwsAccountInfo

**Type:** Multi Line Text

**Description:** Used to hold a JSON object of AWS account info. Details on how this information is populated are not currently documented. More information to follow in a later release.

### gen_module_version

**Type:** String

**Description:** The version of the terraform module as provided in the Gitlab repo tag event.

### gen_region

**Type:** String

**Description:** The target region in which AWS resources will be provisioned. Populated via the `enableAfterPopulateRolesOnChange.js` OnChange event.

### gen_org_name

**Type:** String

**Description:** The name of the Terraform Enterprise Organization. Currently populated from the TerraSnow configuration file.

### gen_repo_url

**Type:** String

**Description:** SSH URI to the gitlab repo

## Client Scripts

This project contains several ServiceNow client scripts contained within the `/sn_javascript` directory that support ease of use when ordering a terraform resource catalog item.

### createDiaplyToggleOnChange.js

**Type:** OnChange

**Associated Variable:** adv_toggle

**Description:** Used to show or hide 'advanced'/default terraform module options (those variables included in the the terraform module that were provided with default values.)

### hideGenericVariablesOnLoad.js

**Type:** OnLoad

**Description:** Hides variables prefixed with `gen_` on the catalog item load event.

### populateAWSRoleInfoOnLoad.js

**Type:** OnLoad

**Description:** invokes the `populateAWSRoleInfoScriptInclude` to populate the roles variable dropdown. This variable's selection value is then passed to TerraSnow via the `/aws-assume-role-webhook` endpoint.

### enableAfterPopulateRolesOnChange.js

**Type:** OnChange

**Associated Variable:** Roles

**Description**: popluates the gen_aws_role, gen_region variables on selection of the AWS role provided in the Roles variable dropdown

## Script Includes

### populateAWSRoleInfoScriptInclude.js

**Description:** Queries a custom table for the ServiceNow user's associated Active directory group, their default AWS region, and the AWS account ARN that has been associated with that Active Directory group. Returns a JSON object containing this information.
