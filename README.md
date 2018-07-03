# TerraSnow Enterprise

Enables the deployment of AWS resources from ServiceNow

## Overview

This project contains a terraform template to deploy a Ngnix reverse proxied, Flask based endpoint that handles Gitlab [`Tag`](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#tag-events) and [`Push`](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#push-events) events by creating a ServiceNow Terraform Module Catalog Item within your target ServieNow Catalog.

Additionally, this project enables ServiceNow to create a Terraform Enterprise workspace from the source terraform resource catalog item.

## Documentation

For more information on installing and using TerraSnow Enterprise, go to <https://terrasnow-enterprise.readthedocs.io>
