# API Reference

## TerraSnow API endpoints

| Endpoint                   | Description                                                                                                                  |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------|
| `/`                        | Sends `200` regardless of content, used for testing                                                                          |
| `/aws-assume-role-webhook` | Listens for AWS assume role data, creates the required TFE credential env vars                                               |
| `/gitlab-webhook`          | Listens for tag update events sent from gitlab and creates the associated SN catalog item                                    |
| `/tfe-run-webhook`         | Listens for workflow run events, uploads the source terraform module to the target workspace to trigger a TFE workflow event |
| `/variables-webhook`       | Listens for ServiceNow variables creation requests, sends associated API call to SN to create the variable                   |
| `/workflow-webhook`        | Listens for TFE workspace creation events, creates an empty workspace                                                        |


### Assume Role

Listens for AWS assume role data, and creates the following TFE workspace environment variables:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY (created with `is_senative=True`)
- AWS_DEFAULT_REGION
- AWS_SESSION_TOKEN

**Request Syntax**

```
{
  "data": [
    {
     "region": "us-east-1",
     "org_name": "MyTFEorg",
     "workspace_name": "ws-123456ASDFhjklmn",
     "role": "arn:aws:iam::0123456789123:role/target_role",
     "duration": "900"
    }
   ]
}
```

**Parameters**

- region *(string)* -- **[REQUIRED]** -- Target region for resource creation.
- org_name *(string)* -- **[REQUIRED]** -- Name of the target TFE region
- workspace_name *(string)* -- **[REQUIRED]** -- Id of the target TFE workspace
- role *(string)* -- **[REQUIRED]** -- The target AWS role to assume. This role requires the necessary permissions to deploy the source terraform template in the target account.
- duration *(string)* -- **[REQUIRED]** -- Maps to the `DurationSections` option in boto3's `assume_role` and is subject to the same limitations. Set to 15 minutes by default.

**Returns**

The response contains the TFE api responses for each environment variable that is created within the target TFE workspace.

```
{
  "access_key_id": "TFE VARIABLE CREATION RESPONSE",
  "secret_access_key": "TFE VARIABLE CREATION RESPONSE",
  "region": "TFE VARIABLE CREATION RESPONSE",
  "aws_session_token": "TFE VARIABLE CREATION RESPONSE"
}
```

### Gitlab

Designed to be triggered on Gitlab tag update events. This endpoint triggers a query against the target ServiceNow instance for a catalog item of the source terraform module. If a ServiceNow catalog item is found and its version is less than the current repo's version tag a new ServiceNow catalog item will be created and the previous version's catalog item will be disabled, otherwise no actions are taken.

**Request Syntax**

Expects the standard [gitlab tag update](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#tag-events) request body

**Returns**

```
{
  "Status": "200"
}
```

### TFE run

This endpoint will query the target workspace for the configuration upload url, `git clone` the target repo from Gitlab, and upload the resulting zip of your repo to the workspace. Currently workspace creation sets `Auto Apply` to true so any change in the configuration will trigger a Plan and Apply events.

**Request Syntax**

```
{
   "data" : [
    {
    "project_name": "terraform-aws-lx-instance",
    "repo_url": "git@your_gitlab_instance:gitlab.user/terraform-aws-lx-instance.git",
    "module_version": "vx.y.z",
    "workspace_id": "ws-123456ASDFhjklmn",
    "region": "us-east-1"
    }
   ]
  }
```

**Parameters**

- project_name *(string)* -- **[REQUIRED]** -- Name of your terraform module project.
- repo_url *(string)* -- **[REQUIRED]** -- SSH URI to the target gitlab repo containing your terraform module
- module_version *(string)* -- **[REQUIRED]** -- specific version tag of your repo that you want to associate the workspace with.
- workspace_id *(string)* -- **[REQUIRED]** -- target TFE workspace id
- region *(string)* -- **[REQUIRED]** -- target AWS region in which your terraform resources will be deployed.

**Returns**

If successful:
```
{
  "Status": "SUCCESS"
}
```

In the event of an error TerraSnow will return the response given by the TFE instance against it's call to
`PUT https://archivist.terraform.io/v1/object/<UNIQUE OBJECT ID>`


### Workflow

Listens for TFE workspace events, creates an empty TFE workspace and backs it with your source repo and version tag

**Request Syntax**

```
{
  "data" :
     [
       {
         "region": "us-east-1",
         "org_name": "your_tfe_org",
         "workspace_name": "your_tfe_workspace_name",
         "repo_id": "gitlab.user/tf_project",
         "repo_version": "x.y.z",
         "action": "CREATE"
      }
    ]
}
```

**Parameters**

- region *(string)* -- **[REQUIRED]** -- target AWS region in which your terraform resources will be deployed
- org_name *(string)* -- **[REQUIRED]** -- your TFE organization name
- workspace_name *(string)* -- **[REQUIRED]** -- your TFE workspace name
- repo_id *(string)* -- **[REQUIRED]** -- the id of your terraform module's repo
- repo_version *(string)* -- **[REQUIRED]** -- the target version tag of your module's repo
- action *(string)* -- **[REQUIRED]** -- the desired action on your target workspace, accepts CREATE or DELETE

**Returns**

TerraSnow simply passes back the response to the workspace creation api endpoint from the TFE instance.

From the official TFE [workspace api documentation](https://www.terraform.io/docs/enterprise/api/workspaces.html):

```
{
  "data": {
    "id": "ws-SihZTyXKfNXUWuUa",
    "type": "workspaces",
    "attributes": {
      "name": "workspace-2",
      "environment": "default",
      "auto-apply": false,
      "locked": false,
      "created-at": "2017-11-02T23:55:16.142Z",
      "working-directory": null,
      "terraform-version": "0.10.8",
      "can-queue-destroy-plan": true,
      "vcs-repo": {
        "identifier": "skierkowski/terraform-test-proj",
        "branch": "",
        "oauth-token-id": "ot-hmAyP66qk2AMVdbJ",
        "ingress-submodules": false
      },
      "permissions": {
        "can-update": true,
        "can-destroy": false,
        "can-queue-destroy": false,
        "can-queue-run": false,
        "can-update-variable": false,
        "can-lock": false,
        "can-read-settings": true
      }
    },
    "relationships": {
      "organization": {
        "data": {
          "id": "my-organization",
          "type": "organizations"
        }
      },
      "ssh-key": {
        "data": null
      },
      "latest-run": {
        "data": null
      }
    },
    "links": {
      "self": "/api/v2/organizations/my-organization/workspaces/workspace-2"
    }
  }
}
```
