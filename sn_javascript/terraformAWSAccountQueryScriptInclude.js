var TerraformAWSAccountQuery = Class.create();
TerraformAWSAccountQuery.prototype = Object.extendsObject(AbstractAjaxProcessor, {

	 /*
	 * method available to client scripts call using:
	 * var awsAccountValues = new GlideAjax("TerraformAWSAccountQuery");
	 * awsAccountValues.addParam("sysparm_name","getAWSAccountInfo");
	 */
	getAWSAccountInfo: function() { // build new response xml element for result

		var wf = new Workflow();
		var wfId = wf.getWorkflowFromName("tfsnow - get aws account info");
		gs.log('TerraformAWSAccountQuery - workflow sysId: ' + wfId);
		var context = wf.startFlow(wfId, null, "tfsnow - get aws account info", null);
		var sysId = context.sys_id;
		gs.log('TerraformAWSAccountQuery - workflow context sysId: ' + sysId);
		this._waitForElement(sysId);
		return sysId;
      },

    _getWorkflowGlideRecord: function(sysId) {
			 // gs.log('TerraformAWSAccountQuery - _getWorkflowState: made it this far' );
 			 var gr = new GlideRecord('wf_context');
 			 gr.addQuery('sys_id', sysId);
 			 gr.query();
 			    while(gr.next()){
 					    return gr;
 				   }
				 },

    _waitForElement: function(sysId) {
	    var gr = this._getWorkflowGlideRecord(sysId);
		var workflowState = gr.state;
	    if(typeof workflowState == "undefined" || workflowState == null || workflowState == 'executing'){
	        gs.log('TerraformAWSAccountQuery - _waitForElement: workflow state is executing..');
			//wait for 5 seconds and then try again..
			gs.sleep(5000);
			this._waitForElement(sysId);
	    }
	    else{
			gs.log('TerraformAWSAccountQuery - _waitForElement: WORKFLOW COMPLETE!');
  			return sysId;
	    }
	  },

      type : "TerraformAWSAccountQuery"
   });
