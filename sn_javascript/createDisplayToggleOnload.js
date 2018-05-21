function onChange(control, oldValue, newValue, isLoading) {
   if (isLoading || newValue == '') {
      return;
   }
   //Type appropriate comment here, and begin script below
   if(newValue == 'true'){
    for (var index = 0; index < g_form.nameMap.length; index++) {
        var unhideme = g_form.nameMap[index].prettyName;
        if(!(unhideme.startsWith('gen_')) && !(g_form.isMandatory(unhideme))){
            g_form.setDisplay(unhideme,true);
            }
        }
    }
    else{
        for (var i = 0; i < g_form.nameMap.length; i++) {
            var hideme = g_form.nameMap[i].prettyName;
            if(hideme.startsWith('gen_') || (!(g_form.isMandatory(hideme)) && hideme != 'adv_toggle')){
                g_form.setDisplay(hideme,false);
                }
            }
        }

}
