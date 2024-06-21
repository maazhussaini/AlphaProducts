from flask_restful import Api
from flask import Blueprint
from resources.resources import JobApplicationFormResource, NewJoinerApprovalResource

def register_routes(app):
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    api.add_resource(JobApplicationFormResource, '/job_application_forms', '/job_application_forms/<int:id>')
    api.add_resource(NewJoinerApprovalResource, '/new_joiner_approvals', '/new_joiner_approvals/<int:id>')