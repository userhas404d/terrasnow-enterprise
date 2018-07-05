# Usage

## Requirements

The Installation procedures have been completed successfully.

Note:

- Module repositories must meet the same requirements as those outlined for addition to the [Terraform Module Private Registry](https://www.terraform.io/docs/enterprise/registry/publish.html)

- This project was successfully tested against the watchmaker [lx-instance](https://github.com/plus3it/terraform-aws-watchmaker/tree/master/modules/lx-instance) module.

- Your source terraform module has a separate `main.tf` and `variables.tf` file. Variables not defined in `variables.tf` will not be included in the resulting ServiceNow catalog item.

## ServiceNow TF catalog item creation

Note: This procedure requires that the TerraSnow installation steps have been completed successfully

1. Create a Gitlab repo with the `terraform-<PROVIDER>-<MODULE_NAME>` name format
2. Add the TerraSnow instance public key to the repo (available at the `https://YOUR_TERRASNOW_INSTANCE/pub-key/key.txt`) and grant the TerraSnow instance read access to the repo.
3. Add a version tag to your project before commit that follows the [PEP 440](https://www.python.org/dev/peps/pep-0440/) standard (ex: 1.0.2)
4. Add the TerraSnow instance url as a webhook under `Repo > Settings > Integrations`
    - Select `Tag push events` and `Enable SSL verification`
    - Paste in your TerraSnow instance gitlab webhook url: `http://YOUR_TERRASNOW_INSTANCE/gitlab-webhook`
    - Click the `Add Webhook` button to complete
5. Kick off the ServiceNow catalog item build process by either manually triggering the webhook or incrementing your project's version tag:
`git tag -a v0.0.1 -m 'test' && git push origin --tags`
6. Your Terraform resource catalog item should now be available for order via your ServiceNow instance.

Note: There is an issue with the ServiceNow catalog item OnLoad client scripts associating with their target variables (see the comments in the embedded client scripts for more details). Unfortunately, this is a manual step for now.

## Deploying TF resources from ServiceNow

Navigate to the ServiceNow Catalog you created in the installation steps and complete the catalog item request. On order your workflow should be triggered and a workspace will be created on your Terraform Enterprise instance.

Current workspace naming convention is the ServiceNow REQ sys_id but this may be updated in a future release
