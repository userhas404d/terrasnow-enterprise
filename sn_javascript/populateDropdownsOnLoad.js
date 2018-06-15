function onLoad() {
 function getAWSAccountInfo(){
  //call the account query script include and start the getAWSAccountInfo wf
	var ga = new GlideAjax("TerraformAWSAccountQuery");
	ga.addParam("sysparm_name", "getAWSAccountInfo");
	ga.getXMLWait();
	var wfSysId = ga.getAnswer();
  // Get the getAWSAccountInfo wf sysid and send it back to the script include to get the workflow results
  // doing this b/c I couldn't get callbacks to work with GlideAjax..
	var wfga = new GlideAjax("TerraformAWSAccountQuery");
	wfga.addParam("sysparm_name", "getResults");
	wfga.addParam("wf_sys_id", wfSysId);
	wfga.getXMLWait();
  //Expects a json object containing the AWS account info.
	result = JSON.parse(wfga.getAnswer());
	setValues(result);
 }


function setValues(json_obj){
   // add none as a first option so all values are actually selectable.
   g_form.addOption('tfv_AmiId', '-- None --');
   g_form.addOption('tfv_AmiDistro', '-- None --');
   g_form.addOption('tfv_KeyPairName', '-- None --');
   g_form.addOption('tfv_SecurityGroupIds', '-- None --');
   g_form.addOption('tfv_SubnetId', '-- None --');
   for (var list in json_obj['amis']){
   //gs.log(list);
     for (var key in json_obj['amis'][list]){
  	   if (json_obj['amis'][list][key]['ImageId']){
  	   g_form.addOption('tfv_AmiId', json_obj['amis'][list][key]['ImageId'],json_obj['amis'][list][key]['Name']);
  	   g_form.addOption('tfv_AmiDistro', json_obj['amis'][list][key]['OSType'], json_obj['amis'][list][key]['OSType'] );
  	       }
       }
  }

  for (var key0 in json_obj['key_pairs']){
  	if(json_obj['key_pairs'][key0]['KeyName']){
  	   g_form.addOption('tfv_KeyPairName',json_obj['key_pairs'][key0]['KeyName'], json_obj['key_pairs'][key0]['KeyName']);
  	}
  }

  for (var key1 in json_obj['subnets']){
  	if(json_obj['subnets'][key1]['Name']){
  		g_form.addOption('tfv_SubnetId',json_obj['subnets'][key1]['SubnetId'], json_obj['subnets'][key1]['Name']);
  	}
  }

  for (var key2 in json_obj['security_groups']){
  		if(json_obj['security_groups'][key2]['Name']){
  		    g_form.addOption('tfv_SecurityGroupIds', json_obj['security_groups'][key2]['GroupId'], json_obj['security_groups'][key2]['Name']);
  	  }
  }
// disable subnet feild to only allow access on change of security group selection
g_form.setDisabled('tfv_SubnetId', true);
// add json object to vairable for later reference
g_form.setValue('gen_AwsAccountInfo', JSON.stringify(json_obj));

}

function showLoadingOverlay(){
	showLoadingDialog();
	setTimeout(function() {
		//setValues(getAWSAccountInfo());
		getAWSAccountInfo();
		hideLoadingDialog();
	}, 20000);
}

//Show the loading dialog as soon as the form loads
showLoadingOverlay();
// var json_str = waitForElement(sys_id);

}
