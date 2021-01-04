import os
from flask import Flask, render_template, url_for
from . import db
from flaskr.views import product, product_movement, report, location


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app) # initializing the flask app
    #registering all the created  blueprints in thr flask app
    app.register_blueprint(product.bp)
    app.register_blueprint(location.bp)  
    app.register_blueprint(product_movement.bp)
    app.register_blueprint(report.bp)
    
    # The main page of the website
    @app.route("/")
    @app.route("/home")
    def home():
       data = [{'name':"samrah"}]
       return render_template('main/home.html', data = data)
    
     # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    return app


