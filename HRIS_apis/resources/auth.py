# auth.py
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from resources.crypto_utils import encrypt, decrypt
from models.models import Users, UserCampus, Role, UserType

class UserLoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help="Username cannot be blank")
        parser.add_argument('password', required=True, help="Password cannot be blank")
        args = parser.parse_args()

        # Replace this with your actual user verification logic
        
        try:
            user = Users.query.filter_by(username=encrypt(args['username'])).first()
            if user:
                password= decrypt(user.password)
                
            # password = Users.query.filter_by(password=encrypted_identity['password']).first()
            
            if user and password:
                print(decrypt(user.username), decrypt(user.password))
                access_token = create_access_token(identity={'username': encrypt(args['username'])})
                
                # Fetch related UserCampus and Role information
                user_campus = UserCampus.query.filter_by(userId=user.user_Id).first()
                
                roles = Role.query.filter_by(campusId=user.campusId).first()
                userType = UserType.query.filter_by(campusId=user_campus.id).first()

                staff_id = user_campus.staffId if user_campus else None
                userType_id = userType.userType_id if userType else None
                userTypeName = userType.userTypeName if userType else None
                
                # roles = []
                is_sys_admin = False

                # for user_role in user_roles:
                #     role = Role.query.filter_by(role_id=user_role.role_id).first()
                #     if role:
                #         roles.append(role.role_name)
                #         if role.is_sys_admin:
                #             is_sys_admin = True
                
                return {
                    'authID': access_token,
                    "campusId": user.campusId,
                    "userName": user.username,
                    "userType": userTypeName,
                    "userTypeId": user.userType_id,
                    "userId": user.user_Id,
                    "userFirstName": user.firstname,
                    "staffId": staff_id,
                    "userRoles": "",
                    "isSysAdmin": is_sys_admin,
                    "connectionString": "",
                    "roles": roles.roleName
                }, 200
            else:
                return {'message': 'Invalid credentials'}, 401
                
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500