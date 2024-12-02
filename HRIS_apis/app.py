from flask import Flask,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask_mail import Mail

load_dotenv()

db = SQLAlchemy()

mail = ""
def create_app():
    
    global mail
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    
    UPLOAD_FOLDER = 'uploads/'  # Directory where you want to save uploaded files
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # # Using add_url_rule to dynamically serve files from subdirectories within 'uploads'
    # app.add_url_rule('/uploads/<foldername>/<filename>', 'uploaded_file',
    #                  lambda foldername, filename: send_from_directory(
    #                      os.path.join(app.config['UPLOAD_FOLDER'], foldername), filename))

    # Using add_url_rule to dynamically serve files from subdirectories within 'uploads'
    # The '<path:subpath>' captures any number of path segments after 'uploads/'
    app.add_url_rule('/uploads/<path:subpath>', 'uploaded_file',
                     lambda subpath: send_from_directory(app.config['UPLOAD_FOLDER'], subpath))

    
    jwt = JWTManager(app)
    
    CORS(app)
    
    # Configuration for Flask-Mail
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
    
    mail = Mail(app)
    db.init_app(app)
    
    from routes.routes import register_routes
    # CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app, resources={
        # r"/api/*": {"origins": ["http://192.168.4.115:5000", "*"]}
        r"/api/*": {"origins": ["http://192.168.4.115:8200", "*"]}

        
    })
    register_routes(app)
    
    return app
