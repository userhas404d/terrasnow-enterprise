workflow.scratchpad.sys_id = current.sys_id;

workspaceBody = {};
variablesBody = {};
assumeRoleBody = {};
tfeRunBody = {};

var item = new GlideRecord("sc_req_item");
   item.addQuery("request",current.request);
   item.query();

   if (item.next()) {
// grab all variable sets from the parent request
     var var_own = new GlideRecord('sc_item_option_mtom');
     var_own.addQuery('request_item', item.sys_id);
     //var_own.addQuery('sc_item_option.item_option_new.u_approval_display', 'global');
     var_own.orderBy('sc_item_option.item_option_new.order');
     var_own.query();
     var catItemVars = {};
     while (var_own.next()){
       var columnName = var_own.sc_item_option.item_option_new.name;
       var columnData = item.variable_pool[columnName].getDisplayValue();
	   if(columnName.includes('tfv_')){
		  catItemVars[columnName] = columnData;
	    }
	   else if (columnName == 'gen_region'){
		   workspaceBody["region"] = columnData;
		   variablesBody["region"] = columnData;
		   tfeRunBody["region"] = columnData;
	   }
	   else if (columnName == 'gen_org_name'){
		   workspaceBody["org_name"] = columnData;
		   variablesBody["org_name"] = columnData;
	   }
	   else if (columnName == 'gen_repo_namespace'){
		   workspaceBody["repo_id"] = columnData;
		   variablesBody["repo_id"] = columnData;
		   tfeRunBody["project_name"] = columnData;
	   }
	   else if (columnName == 'gen_repo_url'){
		   tfeRunBody["repo_url"] = columnData;
	   }
	   else if (columnName == 'gen_module_version'){
		   workspaceBody["repo_version"] = columnData;
		   variablesBody["repo_version"] = columnData;
		   tfeRunBody["module_version"] = columnData;
	   }
	   else if (columnName == 'gen_aws_role'){
		   variablesBody["role"] = columnData;
	   }
     }
     }

workspaceBody["workspace_name"] = String(item.sys_id);
workspaceBody["action"] = "CREATE";
var workspaceData = {};
var workspaceDataList = [];
workspaceDataList[0] = workspaceBody;
workspaceData["data"] = workspaceDataList;


//define the terraform variables - targets the tfe terraform variables
variablesBody["workspace_id"] = "";
variablesBody["cat_vars"] = [];
variablesBody["cat_vars"][0] = catItemVars;
var variablesData = {};
var variablesDataList = [];
variablesDataList[0] = variablesBody;
variablesData["data"] = variablesDataList;


tfeRunBody["workspace_id"] = "";
var tfeRunData = {};
var tfeRunDataList = [];
tfeRunDataList[0] = tfeRunBody;
tfeRunData["data"] = tfeRunDataList;

//gs.info(JSON.stringify(variablesData));
//gs.info(JSON.stringify(workspaceData));

workflow.scratchpad.json_obj = JSON.stringify(catItemVars);
workflow.scratchpad.variablesData = JSON.stringify(variablesData);
workflow.scratchpad.workspaceData = JSON.stringify(workspaceData);
workflow.scratchpad.tfeRunData = JSON.stringify(tfeRunData);
//workflow.scratchpad.output_test = current.request;
