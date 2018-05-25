function onChange(control, oldValue, newValue, isLoading) {
   if (isLoading || newValue == '') {
      return;
   }
   var role_settings = g_form.getValue('role');
   role_settings = JSON.parse(role_settings);
   g_form.setValue('gen_region', role_settings['aws_region']);
   g_form.setValue('gen_aws_role', role_settings['aws_role']);
   g_form.setVariablesReadOnly(false);

}
