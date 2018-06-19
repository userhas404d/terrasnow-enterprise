// linked to the Role variable
// once the user selects their aws role, populate the other variables with the associated values
function onChange(control, oldValue, newValue, isLoading) {
   if (isLoading || newValue == '') {
      return;
   }
   var role_settings = g_form.getValue('Roles');
   role_settings = JSON.parse(role_settings);
   g_form.setValue('gen_region', role_settings['aws_region']);
   g_form.setValue('gen_aws_role', role_settings['aws_role']);
   g_form.setVariablesReadOnly(false);

}
