var sgDropdownValue = g_form.getValue('tfv_SecurityGroupIds')
for (var item in json_obj['subnets']){
    if(json_obj['subnets'][item]['VpcId'] == sgDropdownValue){
        g_form.addOption('tfv_SubnetId',json_obj['subnets'][item]['SubnetId'], json_obj['subnets'][item]['Name']);
      }
    }
g_form.setDisabled('tfv_SubnetId', false);
