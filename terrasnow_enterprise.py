"""TFE and SN broker."""

from flask import Flask, request, abort
import logging
import urllib.parse
import urllib.request
import urllib.response

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

logging.basicConfig(filename='terrasnow_enterprise.log', level=logging.INFO,
                    format=FORMAT)

application = Flask(__name__)


@application.route('/webhook', methods=['POST'])
def webhook():
    """Create webhook."""
    if request.method == 'POST':
        print(request.json)
        return '', 200
    else:
        abort(400)


if __name__ == '__main__':
    application.run(host='0.0.0.0')
