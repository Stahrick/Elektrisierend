from flask import Flask
from views.ServiceWorker import management
from views.RevProxy import revproxy

import logging


app = Flask(__name__)

app.register_blueprint(management, url_prefix="/service-worker")
app.register_blueprint(revproxy, url_prefix="/meter")


def start_server():
    logging.info("Start webserver")
    app.run(host="0.0.0.0", debug=True, port=80)


if __name__ == "__main__":
    import logging
    logging.basicConfig(filename="./log.txt", encoding="UTF-8", format='%(asctime)s %(levelname)s:%(message)s',filemode="w", level=logging.INFO)
    start_server()
