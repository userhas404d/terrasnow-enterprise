function onChange(control, oldValue, newValue, isLoading) {
   if (isLoading || newValue == '') {
      return;
   }
//query for the matching aws account info when provided the aws role arn
  g_form.addOption('tfv_AmiId', '-- None --');
	g_form.addOption('tfv_AmiDistro', '-- None --');
	g_form.addOption('tfv_KeyPairName', '-- None --');
	g_form.addOption('tfv_SecurityGroupIds', '-- None --');
	g_form.addOption('tfv_SubnetId', '-- None --');
	g_form.setDisabled('tfv_SubnetId', true);

	function getAWSAccountInfo(newValue){
        //call the account query script include and start the getAWSAccountInfo wf
	    var ga = new GlideAjax("x_terraform_snow.AWSRoleQuery");
		ga.addParam("sysparm_name", "getRoles");
	    ga.addParam("RoleSysId", newValue);
		ga.getXML(function (response) { getAnswer (response, populateDropdowns); });
 }

	function getAnswer(response, callback){
	  var result = response.responseXML.documentElement.getAttribute("answer");
	  var result_JSON = JSON.parse(result);
	  callback(result_JSON);
 }

	function populateDropdowns(result){
		setAmis(result);
		setKeyPairs(result);
		setSubnets(result);
		setSecurityGroups(result);
	}

	function setAmis(x){
		var amis = JSON.parse(x['amis']);
		for (var lists in amis){
            for (var key in amis[lists]){
                if (amis[lists][key]['ImageId']){
                   g_form.addOption('tfv_AmiId', amis[lists][key]['ImageId'],amis[lists][key]['Name']);
                   g_form.addOption('tfv_AmiDistro', amis[lists][key]['OSType'],amis[lists][key]['OSType'] );
                }
             }
         }
	}

	function setKeyPairs(x){
		var key_pairs = JSON.parse(x['key_pairs']);
		for (var key0 in key_pairs){
			if(key_pairs[key0]['KeyName']){
				g_form.addOption('tfv_KeyPairName',key_pairs[key0]['KeyName'], key_pairs[key0]['KeyName']);
			}
		}
	}

	function setSubnets(x){
		var subnets = JSON.parse(x['subnets']);
		for (var key1 in subnets){
			if(subnets[key1]['Name']){
				g_form.addOption('tfv_SubnetId',subnets[key1]['SubnetId'], subnets[key1]['Name']);
			}
		}

	}

	function setSecurityGroups(x){
		var sgs = JSON.parse(x['security_groups']);
		for (var key2 in sgs){
			if(sgs[key2]['Name']){
				var label = sgs[key2]['Name'] + " -- " + sgs[key2]['GroupId'];
				g_form.addOption('tfv_SecurityGroupIds', sgs[key2]['GroupId'], label);
			}
		}

	}

   getAWSAccountInfo(newValue);
}
