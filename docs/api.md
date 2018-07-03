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

Listens for AWS assume role data, creates the required TFE credential env variables

**Request Syntax**

```
{
  "data": [
    {
     "role": "arn:aws:iam::0123456789123:role/target_role",
     "duration": "900"
    }
   ]
}
```

**Parameters**

- role *(string)* -- **[REQUIRED]** -- The target AWS role to assume. This role requires the necessary permissions to deploy the source terraform template in the target account.
- duration *(string)* -- **[REQUIRED]** -- maps to the `DurationSections` option in boto3's `assume_role` and is subject to the same limitations. Set to 15 minutes by default.

**Returns**

place_holder

### Gitlab

**Request Syntax**

Expects the standard [gitlab tag update](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#tag-events) request body

**Returns**

### TFE run

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

place_holder

### Workflow

Listens for TFE workspace events, creates an empty workspace and points it to your source repo

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
- repo_id *(string)* -- **[REQUIRED]** -- the id of your terrform module's repo
- repo_version *(string)* -- **[REQUIRED]** -- the target version tag of your module's repo
- action *(string)* -- **[REQUIRED]** -- the desired action on your target workspace

**Returns**

place_holder
