//send create TFE workspace request

var request  = new sn_ws.RESTMessageV2();
    request.setHttpMethod('post');

    //endpoint - ServiceNow REST Attachment API
    request.setEndpoint('https://YOUR_WEBHOOK_URL/workflow-webhook');
    //DNS name of the mid server you've configured to use SSH
    request.setMIDServer('YOUR_MIDSEVER_DNS_NAME');
    request.setRequestBody(workflow.scratchpad.workspaceData);

    response = request.execute();
    workflow.scratchpad.workspaceResponseStatus = response.getStatusCode();
    workflow.scratchpad.workspacesponseBody = response.getBody();

//get workspace id
var json_obj = JSON.parse(response.getBody());
workflow.scratchpad.tfeRunData['data'][0]["workspace_id"] = json_obj['data']['id'];
workflow.scratchpad.tfeRunData = JSON.stringify(workflow.scratchpad.tfeRunData);
