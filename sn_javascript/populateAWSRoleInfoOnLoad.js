function onLoad() {
   g_form.setVariablesReadOnly(true);
   g_form.setDisabled('roles', false);
   var UserSysId =  g_user.userID;

   var ga = new GlideAjax('x_terraform_snow.AWSRoles');
   ga.addParam('sysparm_name', 'getRoles');
   ga.addParam('sysparm_UserID', UserSysId);
   ga.getXML(getAnswer);

 function getAnswer(response){
	var result = response.responseXML.documentElement.getAttribute("answer");
	result = JSON.parse(result);
	for(var role in result){
		 g_form.addOption('Role',JSON.stringify(result[role][0]), role);
	}

 }
}
