# TerraSnow Enterprise

Enables the deployment of AWS resources from ServiceNow via Terraform Enterprise

--------------

## Overview

TerraSnow Enterprise is part of a larger suite of tooling that enables the deployment of Terraform resources from a ServiceNow instance via Terraform Enterprise. It was designed to simply cloud resource consumption at the user level and to operate within a multi-tenant AWS environment.

More specifically: This project contains a terraform template to deploy a Ngnix reverse proxied, Flask based endpoint that handles Gitlab [Tag](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#tag-events) and [Push](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#push-events) events by creating a ServiceNow Terraform Module Catalog Item.

## Contents

.. toctree::
    :maxdepth: 1

    installation.md
    configuration.md
    usage.md

## Supported Versions of ServiceNow

*  Jakarta (tested working)
