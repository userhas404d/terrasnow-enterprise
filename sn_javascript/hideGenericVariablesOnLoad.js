function onLoad() {
    for (var index = 0; index < g_form.nameMap.length; index++) {
        var hideme = g_form.nameMap[index].prettyName;
        if(hideme.startsWith('gen_') || (!(g_form.isMandatory(hideme)) && hideme != 'adv_toggle')){
            g_form.setDisplay(hideme,false);
            }
        }
    }
