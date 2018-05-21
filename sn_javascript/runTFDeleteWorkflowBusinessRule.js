(function executeRule(current, previous /*null when async*/) {

	//workflow context sys_id

var wf = new Workflow();
var wfname = 'terraform template manager';
var wfId = wf.getWorkflowFromName(wfname);
var context = wf.startFlow(wfId, current, wfname, null);

})(current, previous);
