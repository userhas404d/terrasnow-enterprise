"""TFE and SN broker."""

import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, abort

application = Flask(__name__)


def file_write():
    """Create a file."""
    f = open("test.txt", "w+")
    f.write("THIS IS JUST A TEST")
    f.close()


@application.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Create webhook."""
    if request.method == 'GET':
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        return request.get_data(), 200

    elif request.method == 'POST':
        # log.info(request.json)
        data = request.get_data().decode("utf-8", "ignore")
        application.logger.error(data)
        return data, 200
    else:
        abort(400)


if __name__ == '__main__':
    handler = RotatingFileHandler('terrasnow_enterprise.log', maxBytes=10000,
                                  backupCount=1)
    handler.setLevel(logging.INFO)
    application.logger.addHandler(handler)
    application.run(debug=True)
