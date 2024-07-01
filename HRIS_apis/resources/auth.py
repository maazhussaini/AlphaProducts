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

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        encrypted_username = encrypt(username)
        encrypted_password = encrypt(password)

        user = Users.query.filter_by(Username=encrypted_username, Password=encrypted_password).first()

        if user and user.Status:
            response = {
                "User_Id": user.User_Id,
                "CampusId": user.CampusId,
                "UserType": user.UserType.to_dict() if user.UserType else None,
                "Firstname": user.Firstname,
                "Teacher_Id": user.Teacher_id,
                "Ispasswordchanged": user.Ispasswordchanged,
                "SchoolDetails": SchoolDetails.query.filter_by(status=True).first().to_dict()
            }

            if not user.Ispasswordchanged and user.UserType.userTypeId in [3, 7]:
                response['redirect'] = "reset_password"
            else:
                user_campus = UserCampus.query.filter_by(UserId=user.User_Id, status=True).first()
                if user_campus:
                    role_ids = [role.Role_Id for role in user.ROLES]
                    user_rights = FormDetailPermissions.query.filter(
                        FormDetailPermissions.RoleId.in_(role_ids),
                        FormDetailPermissions.Status == True
                    ).all()

                    response['UserRoles'] = [role.to_dict() for role in user.ROLES]
                    response['IsSysAdmin'] = any(role.isSysAdmin for role in user.ROLES)
                    response['Rights'] = [right.to_dict() for right in user_rights]
                    response['CurrentAcademicYear'] = AcademicYear.query.filter_by(IsActive=True, status=True).first().academic_year_Id
                    response['redirect'] = "home"
                else:
                    return jsonify({'error': 'Invalid username or password'}), 401

                return jsonify(response), 200
        else:
            return jsonify({'error': 'Invalid username or password or account is blocked'}), 401
