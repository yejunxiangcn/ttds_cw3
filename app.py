from flask import Flask
from flask_bootstrap import Bootstrap
from controller import controller
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.register_blueprint(controller)

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'

bootstrap = Bootstrap(app)


if __name__ == '__main__':
    app.run(threaded=True,debug=True)
