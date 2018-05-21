function onChange(control, oldValue, newValue, isLoading) {
   if (isLoading || newValue == '') {
      return;
   }
   var json_obj = JSON.parse(g_form.getValue('gen_AwsAccountInfo'));
   g_form.clearOptions('tfv_SubnetId');
   //alert("oldValue: " + oldValue + "newValue: " + newValue);
   for (var sg in json_obj['security_groups']){
		   if(json_obj['security_groups'][sg]['GroupId'] == newValue){
			   vpcId = json_obj['security_groups'][sg]['VpcId'];
			   //alert('found vpc: ' + vpcId);
		   }
	   }
   for (var subnet in json_obj['subnets']){
    if(json_obj['subnets'][subnet]['VpcId'] == vpcId){
        g_form.addOption('tfv_SubnetId',json_obj['subnets'][subnet]['SubnetId'], json_obj['subnets'][subnet]['Name']);
		    g_form.setDisabled('tfv_SubnetId', false);
      }
    }
}
