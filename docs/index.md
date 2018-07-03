# TerraSnow Enterprise

Enables the deployment of AWS resources from ServiceNow via Terraform Enterprise

--------------

## Overview

TerraSnow Enterprise is a collection of scripts that enable the deployment of Terraform resources from a ServiceNow instance via Terraform Enterprise. It was designed to simplify cloud resource consumption at the user level and to operate within a multi-tenant AWS environment.

This project contains a terraform template to deploy a Ngnix reverse proxied, Flask based endpoint that handles Gitlab [Tag](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#tag-events) and [Push](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#push-events) events by creating a ServiceNow Terraform Module Catalog Item.

## Contents

.. toctree::
    :maxdepth: 1

    installation.md
    configuration.md
    usage.md

## Project Flow Diagrams

### Terraform Module Creation Workflow

![alt text][module_creation_workflow]

[module_creation_workflow]: images/Terrasnow_Enterprise_Module_Creation_Workflow_diagram.svg "Terrasnow Enterprise module creation workflow diagram"

### ServiceNow Catalog Item Order

![alt text][sn_cat_item_creation]

[sn_cat_item_creation]: images/ServiceNow_Catalog_item_order_diagram.svg "ServiceNow Catalog Item creation diagram"

### ServiceNow Catalog Item Creation - Detailed

![alt text][sn_cat_item_creation_detailed]

[sn_cat_item_creation_detailed]: images/ServiceNow_Catalog_item_creation.svg "ServiceNow Catalog Item creation - detailed diagram"

## Supported Versions of ServiceNow

*  Jakarta (tested working)
