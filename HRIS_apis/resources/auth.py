    # auth.py
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from resources.crypto_utils import encrypt, decrypt
from models.models import *
from flask import Flask, request, jsonify
from app import db

"""
    SELECT
        dbo.USERS.Firstname, dbo.ROLES.RoleName, dbo.Forms.FormName, dbo.Forms.Controller, 
        dbo.FormDetails.Action, dbo.FormDetails.ActionName, dbo.ROLES.Role_Id
    FROM
        dbo.FormDetailPermissions INNER JOIN
        dbo.FormDetails ON dbo.FormDetailPermissions.FormDetailId = dbo.FormDetails.Id INNER JOIN
        dbo.Forms ON dbo.FormDetails.FormId = dbo.Forms.FormId INNER JOIN
        dbo.ROLES ON dbo.FormDetailPermissions.RoleId = dbo.ROLES.Role_Id INNER JOIN
        dbo.LNK_USER_ROLE ON dbo.ROLES.Role_Id = dbo.LNK_USER_ROLE.Role_Id INNER JOIN
        dbo.USERS ON dbo.LNK_USER_ROLE.User_Id = dbo.USERS.User_Id
    WHERE
        (dbo.ROLES.Role_Id = 8)
"""


class UserLoginResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username').lower().strip()
        password = data.get('password').strip()

        # Encrypt the username and password
        encrypted_username = encrypt(username)
        encrypted_password = encrypt(password)

        user = Users.query.filter_by(Username=encrypted_username, Password=encrypted_password).first()

        if user and user.Status:
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
            
            access_token = create_access_token(identity=encrypted_username)
            user_details = {
                'access_token': access_token,
                'user': {
                    'User_Id': user.User_Id,
                    'Firstname': user.Firstname,
                    'CampusId': user.CampusId,
                    'UserType': user_type.UserTypeName,
                    'Roles': [role.RoleName for role in user_roles],
                    'Rights': [{'Controller': right.Controller, 'Action': right.Action} for right in user_rights],
                    "SchoolDetails": [],
                    "CurrentAcademicYear": [],
                    "StudentCount": 0
                }
            }
            
            school_info = SchoolDetails.query.filter_by(status=True).first()
            if school_info:
                user_details["user"]["SchoolDetails"].append({
                        "SchoolName": school_info.SchoolName,
                        "MobileNo": school_info.MobileNo,
                        "MiniLogo": school_info.MiniLogo,
                        "ReportLogo": school_info.ReportLogo,
                        "Address": school_info.Address
                    } if school_info else None)
            
            academic_year = AcademicYear.query.filter_by(IsActive=True, status=True).first()
            if academic_year:
                user_details["user"]["CurrentAcademicYear"] = academic_year.to_dict()
            
            if user_type.UserTypeId == 7:
                user_details["user"]["StudentCount"] = StudentInfo.query.filter_by(UserId=user.User_Id, Stud_Active=True).count()

            return {"data": [user_details]}, 200

        return jsonify({'error': 'Invalid username or password'}), 401