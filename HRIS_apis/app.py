from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv 
from datetime import datetime, date
import json
from flask_cors import CORS, cross_origin

load_dotenv() 

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    
    jwt = JWTManager(app)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    
    from routes.routes import register_routes
    
    register_routes(app)
    
    return app
