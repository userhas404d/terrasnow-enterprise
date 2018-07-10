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
workflow.scratchpad.workflow_req_response = JSON.stringify(json_obj);
var workflow_id = "";
workflow_id = json_obj['data']['id'];
workflow.scratchpad.test_variable = workflow_id;

var variables_json = JSON.parse(workflow.scratchpad.variablesData);
variables_json['data'][0]["workspace_id"] = workflow_id;
workflow.scratchpad.variablesData = JSON.stringify(variables_json);

var tfeRunData_json = JSON.parse(workflow.scratchpad.tfeRunData);
tfeRunData_json['data'][0]["workspace_id"] = workflow_id;
workflow.scratchpad.tfeRunData = JSON.stringify(tfeRunData_json);
