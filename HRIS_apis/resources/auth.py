import logging
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app import db
from resources.crypto_utils import encrypt
from models.models import Users, Role, LNK_USER_ROLE, FormDetails, FormDetailPermissions, Form, SchoolDetails, AcademicYear, UserType, StudentInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserLoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data or 'username' not in data or 'password' not in data:
                logger.warning("Missing username or password in request data")
                return {"data": {'status':'error', 'message': 'Username and password are required'}}, 400

            username = data.get('username').lower().strip()
            password = data.get('password').strip()

            try:
                encrypted_username = encrypt(username)
                encrypted_password = encrypt(password)
            except Exception as e:
                logger.error(f"Error encrypting username or password: {e}")
                return {"data": {'status':'error', 'message': 'Encryption error'}}, 500

            try:
                user = Users.query.filter_by(Username=encrypted_username, Password=encrypted_password).first()
            except SQLAlchemyError as e:
                logger.error(f"Database query error: {e}")
                return {"data": {'status':'error', 'message': 'Database error'}}, 500

            if not user:
                logger.warning("Invalid username or password")
                return {"data": {'status':'error', 'message': 'Invalid username or password'}}, 401

            if not user.Status:
                logger.warning("User account is inactive")
                return {"data": {'status':'error', 'message': 'Account is inactive'}}, 403

            try:
                user_roles = Role.query.join(LNK_USER_ROLE, Role.Role_id == LNK_USER_ROLE.Role_Id)\
                    .filter(LNK_USER_ROLE.User_Id == user.User_Id).all()

                user_rights = db.session.query(FormDetails.Action, Form.Controller)\
                    .join(FormDetailPermissions, FormDetails.Id == FormDetailPermissions.FormDetailId)\
                    .join(Form, FormDetails.FormId == Form.FormId)\
                    .join(Role, FormDetailPermissions.RoleId == Role.Role_id)\
                    .join(LNK_USER_ROLE, Role.Role_id == LNK_USER_ROLE.Role_Id)\
                    .filter(LNK_USER_ROLE.User_Id == user.User_Id, FormDetailPermissions.Status == True)\
                    .all()

                user_type = UserType.query.filter_by(UserTypeId=user.UserType_id).first()
            except SQLAlchemyError as e:
                logger.error(f"Database query error: {e}")
                return {"data": {'status':'error', 'message': 'Database error'}}, 500

            try:
                access_token = create_access_token(identity=encrypted_username)
            except Exception as e:
                logger.error(f"Error creating access token: {e}")
                return {"data": {'status':'error', 'message': 'Token creation error'}}, 500

            user_details = {
                'status': 'success',
                'message': {
                    'access_token': access_token,
                    'user': {
                        'User_Id': user.User_Id,
                        'Firstname': user.Firstname,
                        'CampusId': user.CampusId,
                        'UserType': user_type.UserTypeName if user_type else 'Unknown',
                        'Roles': [role.RoleName for role in user_roles],
                        'Rights': [{'Controller': right.Controller, 'Action': right.Action} for right in user_rights],
                        "SchoolDetails": [],
                        "CurrentAcademicYear": [],
                        "StudentCount": 0
                    }
                }
            }

            try:
                school_info = SchoolDetails.query.filter_by(status=True).first()
                if school_info:
                    user_details["message"]["user"]["SchoolDetails"].append({
                        "SchoolName": school_info.SchoolName,
                        "MobileNo": school_info.MobileNo,
                        "MiniLogo": school_info.MiniLogo,
                        "ReportLogo": school_info.ReportLogo,
                        "Address": school_info.Address
                    })

                academic_year = AcademicYear.query.filter_by(IsActive=True, status=True).first()
                if academic_year:
                    user_details["message"]["user"]["CurrentAcademicYear"] = academic_year.to_dict()

                if user_type and user_type.UserTypeId == 7:
                    user_details["message"]["user"]["StudentCount"] = StudentInfo.query.filter_by(UserId=user.User_Id, Stud_Active=True).count()
            except SQLAlchemyError as e:
                logger.error(f"Database query error: {e}")
                return {"data": {'status':'error', 'message': f'Database error: {e}'}}, 500

            return {"data": user_details}, 200
        except SQLAlchemyError as e:
            return {"data": {'status':'error', 'message': f"Database error occurred: {str(e)}"}}, 500
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return {"data": {'status':'error', 'message': f'Internal server error: {e}'}}, 500
