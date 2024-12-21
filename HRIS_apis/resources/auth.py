import logging
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app import db
from resources.crypto_utils import encrypt
from datetime import timedelta  # Import timedelta
from models.models import (Campus,USERS, UserCampus, StaffInfo, Roles, LNK_USER_ROLE, FormDetails, 
                           FormDetailPermissions, Form, SchoolDetails, AcademicYear, UserType, 
                           StudentInfo, country, cities)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserLoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data or 'username' not in data or 'password' not in data:
                logger.warning("Missing username or password in request data")
                return {"data": {'status': 400, 'message': 'Username and password are required'}}, 400

            username = data.get('username').lower().strip()
            password = data.get('password').strip()

            try:
                encrypted_username = encrypt(username)
                encrypted_password = encrypt(password)
            except Exception as e:
                logger.error(f"Error encrypting username or password: {e}")
                return {"data": {'status': 400, 'message': 'Encryption error'}}, 500

            try:
                user = USERS.query.filter_by(Username=encrypted_username, Password=encrypted_password).first()
            except SQLAlchemyError as e:
                logger.error(f"Database query error: {e}")
                return {"data": {'status': 400, 'message': 'Database error'}}, 500

            if not user:
                logger.warning("Invalid username or password")
                return {"data": {'status': 400, 'message': 'Invalid username or password'}}, 401

            if not user.Status:
                logger.warning("User account is inactive")
                return {"data": {'status': 400, 'message': 'Account is inactive'}}, 403
            
            # staff_info_alias = db.aliased(StaffInfo)

            staffInfo = db.session.query(StaffInfo).join(UserCampus, UserCampus.StaffId == StaffInfo.Staff_ID).filter(UserCampus.UserId == user.User_Id).first()
            countryName = country.query.filter_by(country_id=staffInfo.CountryId).first().country
            cityName = cities.query.filter_by(cityId=staffInfo.CityId).first().city
            campus = db.session.query(Campus).join(USERS, USERS.CampusId == Campus.Id).filter(USERS.User_Id == user.User_Id).first()

            
            try:
                user_roles = Roles.query.join(LNK_USER_ROLE, Roles.Role_id == LNK_USER_ROLE.Role_Id)\
                    .filter(LNK_USER_ROLE.User_Id == user.User_Id).all()

                user_rights = db.session.query(FormDetails.Action, Form.Controller)\
                    .join(FormDetailPermissions, FormDetails.Id == FormDetailPermissions.FormDetailId)\
                    .join(Form, FormDetails.FormId == Form.FormId)\
                    .join(Roles, FormDetailPermissions.RoleId == Roles.Role_id)\
                    .join(LNK_USER_ROLE, Roles.Role_id == LNK_USER_ROLE.Role_Id)\
                    .filter(LNK_USER_ROLE.User_Id == user.User_Id, FormDetailPermissions.Status == True)\
                    .all()

                user_type = UserType.query.filter_by(UserTypeId=user.UserType_Id).first()
            except SQLAlchemyError as e:
                logger.error(f"Database query error: {e}")
                return {"data": {'status': 400, 'message': 'Database error'}}, 500

            try:
                access_token = create_access_token(identity=encrypted_username, expires_delta=timedelta(hours=2))
            except Exception as e:
                logger.error(f"Error creating access token: {e}")
                return {"data": {'status': 400, 'message': 'Token creation error'}}, 500

            firstName = user.Firstname if user.Firstname else ''
            lastName = user.Lastname if user.Lastname else ''
            
            user_details = {
                'accessToken': access_token,
                'user': {
                    'id': user.User_Id,
                    'Staff_ID':staffInfo.Staff_ID,
                    'displayName': firstName + " " + lastName,
                    'email': user.EMail,
                    'campusId': user.CampusId,
                    'Campus': campus.Name if campus else None,
                    'userType': user_type.UserTypeName if user_type else 'Unknown',
                    'IsPermanent': True if staffInfo.IsPermanent == 1 else False,
                    'S_Gender':staffInfo.S_Gender,
                    'roles': [role.RoleName for role in user_roles],
                    'city': cityName,
                    'country': countryName,
                    'isPublic': True,
                    'address': staffInfo.PresentAddress if staffInfo else None,
                    'phoneNumber': staffInfo.S_ContactNo,
                    "photoURL": staffInfo.PhotoPath if staffInfo else None,
                    'rights': [{'Controller': right.Controller, 'Action': right.Action} for right in user_rights],
                    "schoolDetails": [],
                    "currentAcademicYear": [],
                    "studentCount": 0
                }
            }

            try:
                school_info = SchoolDetails.query.filter_by(status=True).first()
                if school_info:
                    user_details["user"]["schoolDetails"].append({
                        "schoolName": school_info.SchoolName,
                        "mobileNo": school_info.MobileNo,
                        "miniLogo": school_info.MiniLogo,
                        "reportLogo": school_info.ReportLogo,
                        "address": school_info.Address
                    })

                academic_year = AcademicYear.query.filter_by(IsActive=True, status=True).first()
                print(academic_year)
                if academic_year:
                    user_details["user"]["currentAcademicYear"] = academic_year.to_dict()

                if user_type and user_type.UserTypeId == 7:
                    user_details["user"]["studentCount"] = StudentInfo.query.filter_by(UserId=user.User_Id, Stud_Active=True).count()
            except SQLAlchemyError as e:
                logger.error(f"Database query error: {e}")
                return {"data": {'status': 400, 'message': f'Database error: {e}'}}, 500

            return {"data": user_details, "status": 200}, 200
        except SQLAlchemyError as e:
            return {"data": {'status': 400, 'message': f"Database error occurred: {str(e)}"}}, 500
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return {"data": {'status': 400, 'message': f'Internal server error: {e}'}}, 500
