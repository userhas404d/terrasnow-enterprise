var TerraformAWSAccountQuery = Class.create();
TerraformAWSAccountQuery.prototype = Object.extendsObject(AbstractAjaxProcessor, {

	 /*
	 * method available to client scripts call using:
	 * var awsAccountValues = new GlideAjax("TerraformAWSAccountQuery");
	 * awsAccountValues.addParam("sysparm_name","getAWSAccountInfo");
	 */
getAWSAccountInfo: function() {
	    //starts AWS account information retrieval workflow and returns its sysid
	    var result = '';
			var wf = new Workflow();
			var wfId = wf.getWorkflowFromName("tfsnow - get aws account info");
			gs.log('TerraformAWSAccountQuery - workflow sysId: ' + wfId);
			var context = wf.startFlow(wfId, null, "tfsnow - get aws account info", null);
			var sysId = context.sys_id;
			gs.log('TerraformAWSAccountQuery - workflow context sysId: ' + sysId);
			this._waitForElement(sysId);
			return sysId;
},


getResults: function() {
	     //returns aws account info from workflow scratchpad given the wf sysid
			 sysId = this.getParameter('wf_sys_id');
			 gs.log('running from the results function.');
			 var gr = this._getWorkflowGlideRecord(sysId);
			 var awsDetails = gr.scratchpad; //object
			 //convert scratchpad string result to json obj
			 var test = JSON.parse(awsDetails); //still an object
			 //extract 'aws account info' as json string from scratchpad json obj
			 var json_str = test['json_obj']; //string
			 //convert 'aws account info' json string into json obj});
			 return json_str;
	},


_waitForElement: function(sysId) {
	    //runs in loop until workflow is complete
			var gr = this._getWorkflowGlideRecord(sysId);
			var workflowState = gr.state;
			if(typeof workflowState == "undefined" || workflowState == null || workflowState == 'executing'){
					gs.log('TerraformAWSAccountQuery - _waitForElement: workflow state is executing..');
					//wait for 5 seconds and then try again..
					gs.sleep(5000);
					this._waitForElement(sysId);
			}
			else if(workflowState == 'finished'){
					gs.log('TerraformAWSAccountQuery - _waitForElement: workflow state: '+ gr.state);
					gs.log('TerraformAWSAccountQuery - _waitForElement: WORKFLOW COMPLETE!');
				  }else{
							gs.sleep(5000);
							this._waitForElement(sysId);
				  }
	},


_getWorkflowGlideRecord: function(sysId) {
	     //returns a workflow glide record provided it's sysid
			 var gr = new GlideRecord('wf_context');
 			 gr.addQuery('sys_id', sysId);
 			 gr.query();
 			    while(gr.next()){
 					    return gr;
 				   }
},

      type : "TerraformAWSAccountQuery"
   });
