var AWSRoles = Class.create();

AWSRoles.prototype = Object.extendsObject(global.AbstractAjaxProcessor, {

     getRoles: function() {
		 var groupList = [];
         var myResponse = {};
         var UserSysId = this.getParameter('sysparm_UserID');
         var gr = new GlideRecord("sys_user_grmember");
         gr.addQuery("user.sys_id",UserSysId);
         gr.query();
         while(gr.next())
            {
				var groupName = gr.group.name;
                if(groupName.includes('T_'))
				   {
					  var tfgr = new GlideRecord("x_terraform_snow_cloud_account_details");
                      tfgr.addQuery("ad_group_name",groupName);
                      tfgr.query();
					  test = "made it to the if statement";
					  while(tfgr.next())
						 {
							var aws_region = tfgr.aws_region.getDisplayValue();
							var aws_role = tfgr.aws_role.getDisplayValue();
							var value = {};
							value["aws_region"] = aws_region;
							value["aws_role"] = aws_role;
							myResponse[groupName] = [];
							myResponse[groupName][0] = value;
						 }

				}
			}
        return JSON.stringify(myResponse);
     },



});
