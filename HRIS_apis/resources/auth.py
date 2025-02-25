import logging
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app import db
from resources.crypto_utils import encrypt
from datetime import timedelta  # Import timedelta
from models.models import (Campus,USERS, UserCampus, StaffInfo, Roles, LNK_USER_ROLE, FormDetails, 
                           FormDetailPermissions, Form, SchoolDetails, AcademicYear, UserType, 
                           StudentInfo, country, cities,StaffDesignation,StaffEducation,StaffExperience,StaffOther,StaffCnic)

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
            
            staffInfo = db.session.query(StaffInfo) \
                .join(UserCampus, UserCampus.StaffId == StaffInfo.Staff_ID) \
                .filter(UserCampus.UserId == user.User_Id) \
                .first()

            if staffInfo is None:
                staffInfo = db.session.query(StaffInfo).filter(StaffInfo.Staff_ID == 16787).first()

            country_info = db.session.query(country).filter_by(country_id=staffInfo.CountryId).first()
            city_info = db.session.query(cities).filter_by(cityId=staffInfo.CityId).first()

            countryName = country_info.country if country_info else "Unknown"
            cityName = city_info.city if city_info else "Unknown"

            campus = db.session.query(Campus) \
                .join(USERS, USERS.CampusId == Campus.Id) \
                .filter(USERS.User_Id == user.User_Id).first()
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
            
            # Fetch StaffEducation data
            education_info = db.session.query(StaffEducation) \
                .filter(StaffEducation.StaffId == staffInfo.Staff_ID) \
                .order_by(StaffEducation.Year.desc())
                
            # Fetch the record with the maximum year
            max_year_record = education_info.first()  

            # If the maximum year is NULL, handle it and set the result as "Unknown"
            if max_year_record and max_year_record.Year is not None:
                # If the year is available, fetch the FieldName
                field_name = max_year_record.FieldName if max_year_record.FieldName not in (None, 0) else None
            else:
                field_name = "Unknown"

            # If the field name is None (0 or null), select the first available record with valid FieldName
            if field_name is None:
                # If no valid field name exists, find the first valid field name with a non-zero, non-null value
                valid_education_record = education_info.filter(StaffEducation.FieldName.notin_([None, 0])).first()
                field_name = valid_education_record.FieldName if valid_education_record else "Unknown"
                
            designation_info = db.session.query(StaffDesignation) \
                .filter(StaffDesignation.Designation_ID == staffInfo.Designation_ID) \
                .first()

            # Fetch the Designation_Name from the result
            designation_name = designation_info.Designation_Name if designation_info else "Unknown"
            dob = staffInfo.S_DoB
            if dob:
                today = datetime.today()

                # Check if the birth year is in the future, and handle accordingly
                if dob > today:
                    age = 0  # If the birthday is in the future, the person has not been born yet
                else:
                    # Calculate the age normally
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            staff_experience = db.session.query(StaffExperience) \
                .filter(StaffExperience.StaffId == staffInfo.Staff_ID,StaffExperience.RequestStatus.in_([1, 0])).all()
            
                        # Fetch StaffEducation data
            staff_education = db.session.query(StaffEducation) \
                .filter(StaffEducation.StaffId == staffInfo.Staff_ID, StaffEducation.RequestStatus.in_([1, 0])).all()
            # Fetch StaffOther data
            staff_other = db.session.query(StaffOther) \
                .filter(StaffOther.StaffId == staffInfo.Staff_ID,StaffOther.RequestStatus.in_([1, 0])).all()

            # Fetch StaffCnic data
            staff_cnic = db.session.query(StaffCnic) \
                .filter(StaffCnic.StaffId == staffInfo.Staff_ID,StaffCnic.RequestStatusBack.in_([1, 0]),StaffCnic.RequestStatus.in_([1, 0])).first()

                        # Format the results
            staff_cnic_data = {
                'FrontCNICDocumentPath': staff_cnic.FrontCNICDocumentPath if staff_cnic else None,
                'BackCNICDocumentPath': staff_cnic.BackCNICDocumentPath if staff_cnic else None,
            }

            education_data = [
                {
                    'FieldName': edu.FieldName,
                    'Institution': edu.Institution,
                    'Year': edu.Year,
                    'Grade': edu.Grade,
                    'EducationDocumentPath': edu.EducationDocumentPath
                } for edu in staff_education
            ]

            experience_data = [
                {
                    'CompanyName': exp.CompanyName,
                    'Position': exp.Position,
                    'StartDate': exp.StartDate.strftime('%Y-%m-%d %H:%M:%S') if exp.StartDate else None,
                    'EndDate': exp.EndDate.strftime('%Y-%m-%d %H:%M:%S') if exp.EndDate else None,
                    'Salary': exp.Salary,
                    'ExperienceDocumentPath':exp.ExperienceDocumentPath
                } for exp in staff_experience
            ]

            other_data = [
                {
                    'Title': other.Title,
                    'Description': other.Description,
                    'OtherDocumentPath': other.OtherDocumentPath
                } for other in staff_other
            ]
            
            
            user_details = {
                'accessToken': access_token,
                'user': {
                    'id': user.User_Id,
                    'username':username,
                    'Staff_ID':staffInfo.Staff_ID,
                    'displayName': firstName + " " + lastName,
                    'CNIC':staffInfo.S_CNIC,
                    'email': user.EMail,
                    'Designation': designation_name,
                    'Qualification': field_name,
                    'PersonalEmail':staffInfo.S_Email,
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
                    'Age': age,
                    'phoneNumber': staffInfo.S_ContactNo,
                    "photoURL": staffInfo.PhotoPath if staffInfo else None,
                    'rights': [{'Controller': right.Controller, 'Action': right.Action} for right in user_rights],
                    "schoolDetails": [],
                    "currentAcademicYear": [],
                    "studentCount": 0,
                    'cnicInfo': staff_cnic_data,
                    'educationInfo': education_data,
                    'experienceInfo': experience_data,
                    'otherInfo': other_data
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
