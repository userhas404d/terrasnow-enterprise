"""TFE and SN broker."""

# ToDo:
# take actions based on request headers
# get request header request.headers['X-Gitlab-Event'] should = "Tag Push Hook"

import json
import logging
from logging.handlers import RotatingFileHandler

import sn_workflow_listener
from flask import Flask, request, abort

application = Flask(__name__)


@application.route('/workflow-webhook', methods=['POST'])
def workflow_target():
    """Workflow event listener."""
    if request.method == 'POST':
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        return json.dumps(
                  sn_workflow_listener.workspace_event_listener(
                     json.loads(data))), 200


@application.route('/variables-webhook', methods=['POST'])
def variables_target():
    """TFE variable creation event listener."""
    if request.method == 'POST':
        print(request.get_data())
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        return json.dumps(
                  sn_workflow_listener.variables_event_listener(
                     json.loads(data))), 200


@application.route('/gitlab-webhook', methods=['GET', 'POST'])
def webhook():
    """Create webhook."""
    if request.method == 'GET':
        data = request.get_json().decode("utf-8", "ignore")
        application.logger.error(data)
        return request.get_data(), 200

    elif request.method == 'POST':
        # log.info(request.json)
        data = request.get_json().decode("utf-8", "ignore")
        application.logger.error(data)
        return data, 200
    else:
        abort(400)


if __name__ == '__main__':
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler("terrasnow_enterprise.log",
                                  maxBytes=10000000,
                                  backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    application.run(debug=True)
