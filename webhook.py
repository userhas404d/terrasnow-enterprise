"""TFE and SN broker."""

# ToDo:
# take actions based on request headers
# get request header request.headers['X-Gitlab-Event'] should = "Tag Push Hook"

import json
import logging
from logging.handlers import RotatingFileHandler

import aws_account_info_listener
import sn_workflow_listener
import terrasnow_enterprise
from flask import abort, Flask, render_template, request

application = Flask(__name__)


# Root of webhook listener. Returns success by default.
@application.route('/', methods=['GET', 'POST'])
def root_listener():
    """Create webhook."""
    if request.method == 'GET':
        return "SUCCESS", 200

    elif request.method == 'POST':
        return "SUCCESS", 200
    else:
        abort(400)


@application.route('/aws-assume-role-webhook', methods=['POST'])
def assume_role_target():
    """Return assumed role credentials."""
    if request.method == 'POST':
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        return json.dumps(sn_workflow_listener.assume_role_listener(
                          json.loads(data))), 200


# listens for tag update event sent from gitlab and creates the associated
# SN catalog item
@application.route('/gitlab-webhook', methods=['GET', 'POST'])
def gitlab_target():
    """Create gitlab webhook."""
    if request.method == 'GET':
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        return json.dumps(
                  terrasnow_enterprise.process_response(
                     json.loads(data))), 200

    elif request.method == 'POST':
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        return json.dumps(
                  terrasnow_enterprise.process_response(
                     json.loads(data))), 200
    else:
        abort(400)


@application.route('/tfe-run-webhook', methods=['POST'])
def tfe_run_target():
    """TFE run event listener."""
    if request.method == 'POST':
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        return json.dumps(
                  sn_workflow_listener.TFE_run_listener(
                     json.loads(data))), 200


# Listens for catalog item variables object sent from SN catalog item order
# request
@application.route('/variables-webhook', methods=['POST'])
def variables_target():
    """TFE variable creation event listener."""
    if request.method == 'POST':
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        return json.dumps(
                  sn_workflow_listener.variables_event_listener(
                     json.loads(data))), 200


# Creates/Deletes a TFE workspace using the SN Cat item base module's source
# repo as provided from SN catalog item order request
@application.route('/workflow-webhook', methods=['POST'])
def workflow_target():
    """Workflow event listener."""
    if request.method == 'POST':
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        return json.dumps(
                  sn_workflow_listener.workspace_event_listener(
                     json.loads(data))), 200


# Returns JSON object of AWS account information
@application.route('/aws-account-info', methods=['POST'])
def aws_account_info():
    """Return aws account info."""
    if request.method == 'POST':
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        response = json.dumps(aws_account_info_listener.event_listener(
                          json.loads(data)))
        if "ERROR" in response:
            return response, 400
        else:
            return response, 200


if __name__ == '__main__':
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler("terrasnow_enterprise.log",
                                  maxBytes=10000000,
                                  backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    application.run(debug=True)
