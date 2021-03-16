from flask import Flask
from controller import controller
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.register_blueprint(controller)

if __name__ == '__main__':
    app.run(threaded=True,debug=True)
