//send create TFE variables request

var request  = new sn_ws.RESTMessageV2();
    request.setHttpMethod('post');

    //endpoint - ServiceNow REST Attachment API
    request.setEndpoint('https://YOUR_WEBHOOK_URL/variables-webhook');
    //DNS name of the mid server you've configured to use SSH
    request.setMIDServer('YOUR_MIDSEVER_DNS_NAME');
    request.setRequestBody(workflow.scratchpad.variablesData);

    response = request.execute();
    workflow.scratchpad.variablesResponseStatus = response.getStatusCode();
    workflow.scratchpad.variablesResponseBody = response.getBody();
