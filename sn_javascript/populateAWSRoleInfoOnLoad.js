// invokes _insert_name_ with current user's sys_id.
// _insert_name_ searches the AWS account info table for the associated role and default region
// once found that information is passed to the aws_role dropdown
function onLoad() {
   g_form.setVariablesReadOnly(true);
   g_form.setDisabled('roles', false);
   var UserSysId =  g_user.userID;

   var ga = new GlideAjax('x_terraform_snow.AWSRoles');
   ga.addParam('sysparm_name', 'getRoles');
   ga.addParam('sysparm_UserID', UserSysId);
   ga.getXML(getAnswer);

 //processe the results from the script include
 function getAnswer(response){
  //set the first option on the roles dropdown to null so the onChange event works
  g_form.addOption('Roles', "", "--Select your target AWS account--");
	var result = response.responseXML.documentElement.getAttribute("answer");
	result = JSON.parse(result);
	for(var role in result){
    //populate the Roles dropdown with the script inclde results
		 g_form.addOption('Roles',JSON.stringify(result[role][0]), role);
	}
  //re-enable fields once Roles is populated
  g_form.setDisabled('Roles', false);
  g_form.setDisabled('adv_toggle', false);
 }
}
