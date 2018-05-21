## Terrasnow-Enterprise Client Scripts

Collection of ServiceNow Catalog item client scripts

`createDisplayToggleOnload.js` - hides all catalog item variables with the `gen_` prefix as well as the terraform template variables that do not have default values

`filterSubnetsOnChange.js` - filters list of available subnets on change of security group selection

`populateDropdownsOnLoad.js` - calls `TerraformAWSAccountQueryScriptInclude.js` and uses result to populate terraform catalog item with AWS account specific details

`runTFDeleteWorkflowBusinessRule.js` - triggers the `terraform delete` workflow on the ServiceNow instance

`securityGroupsOnChange.js` - enables the `tfv_SubnetId` catalog item variable once a security group has been selected

`TerraformAWSAccountQueryScriptInclude.js` - ServiceNow script include that triggers the ServiceNow `getAWSAccountInfo` workflow
