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

        user = Users.query.filter_by(Username=encrypted_username).first()

        if user and user.Status:
            if encrypted_password != user.Password:
                return {"error": "Password Incorrect"}, 401
            
            else:
                user_campus = UserCampus.query.filter_by(UserId=user.User_Id, Status=True).first()
                if user_campus:
                    user_types = UserType.query.filter_by(UserTypeId=user.UserType_id).first()
                    roles = Role.query.join(LNK_USER_ROLE, Role.Role_id == LNK_USER_ROLE.Role_Id).filter(LNK_USER_ROLE.User_Id == user.User_Id).all()
                    role_ids = [role.Role_id for role in roles]
                    
                    school_info = SchoolDetails.query.filter_by(status=True).first()

                    rights = FormDetailPermissions.query.filter(
                        FormDetailPermissions.RoleId.in_(role_ids),
                        FormDetailPermissions.Status == True
                    ).all()
                    
                    form_details = FormDetails.query.filter(
                        FormDetails.Id.in_([right.FormDetailId for right in rights]),
                        FormDetails.Status ==True
                    ).all()
                    
                    forms = Form.query.filter(
                        Form.FormId.in_([form_detail.FormId for form_detail in form_details])
                    ).all()

                    # user_data = {
                    #     "User_Id": user.User_Id,
                    #     "CampusId": user.CampusId,
                    #     "Firstname": user.Firstname,
                    #     "Teacher_Id": user.Teacher_id,
                    #     "Ispasswordchanged": user.Ispasswordchanged,
                    #     # "SchoolDetails": school_info.to_dict() if school_info else None,
                    #     'UserRoles': [role.to_dict() for role in roles],
                    #     'IsSysAdmin': any(role.IsSysAdmin for role in roles),
                    #     'Rights': [right.to_dict() for right in rights],
                    #     'CurrentAcademicYear': AcademicYear.query.filter_by(IsActive=True, status=True).first().academic_year_Id,
                    # }
                    
                    user_data = {
                        "User_Id": user.User_Id,
                        "CampusId": user.CampusId,
                        "UserType": {"Id": user_types.UserTypeId, "Name": user_types.UserTypeName} if user_types else None,
                        "Firstname": user.Firstname,
                        "Teacher_Id": user.Teacher_id,
                        "ispasswordchanged": user.Ispasswordchanged,
                        "SchoolDetails": {
                            "SchoolName": school_info.SchoolName,
                            "MobileNo": school_info.MobileNo,
                            "MiniLogo": school_info.MiniLogo,
                            "ReportLogo": school_info.ReportLogo,
                            "Address": school_info.Address
                        } if school_info else None,
                        'UserRoles': [{"Role_Id": role.Role_id, "RoleName": role.RoleName} for role in roles],
                        'IsSysAdmin': any(role.IsSysAdmin for role in roles),
                        # 'Rights': [
                        #     {
                        #         "Controller": forms.Controller, 
                        #         "Action": forms.FormDetail.Action
                        #     } for right in rights],
                        'CurrentAcademicYear': AcademicYear.query.filter_by(IsActive=True, status=True).first().academic_year_Id
                    }
                    
                    return jsonify({"data": [user_data]})

                    if user.UserType_id == 7:
                        user_data["StuCount"] = StudentInfo.query.filter_by(UserId=user.User_Id, Stud_Active=True).count()

                    if user.UserType_id != 3 and user.UserType_id != 7:
                        user_data["CampusId"] = user_campus.campusId

                    if user.CampusId:
                        if user.UserType_id == "Teacher":
                            user_data["TeacherId"] = user.UserCampus[0].StaffId
                        elif user.UserType_id == "Associate Teacher":
                            user_data["AssociateTeacherId"] = user.UserCampus[0].StaffId

                        staff_id = user.CampusId[0].StaffId
                        user_data["IsAEN"] = StaffInfo.query.get(staff_id).IsAEN if staff_id else 0

                    else:
                        user_data["IsAEN"] = 0

                    return jsonify(user_data), 200
                else:
                    return jsonify({'error': 'Invalid username or password'}), 401

        else:
            return jsonify({'error': 'Invalid username or password or account is blocked'}), 401

