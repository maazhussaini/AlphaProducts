from flask_restful import Api
from flask import Blueprint
from flask_cors import CORS, cross_origin
from resources.resources import *
from resources.customApi import (
    DynamicGetResource, CallProcedureResource, DynamicPostResource,
    DynamicUpdateResource, DynamicDeleteResource, DynamicInsertOrUpdateResource, UploadFileResource,CallProcedureResourceLeave,DynamicPostResource_With_PKReturn
    ,Get_JotForms
)
from resources.auth import UserLoginResource

def register_routes(app):
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app, resources={
        # r"/api/*": {"origins": ["http://192.168.4.115:5000", "*"]}
        r"/api/*": {"origins": ["http://192.168.4.115:8200", "*"]}
    })
    
    api.add_resource(UserLoginResource, '/login')  # Register the authentication resource
    api.add_resource(UserDetails, '/userDetails/<int:id>')
    
    ## Dynamic APIs
    api.add_resource(CallProcedureResource, '/callProcedure')
    api.add_resource(CallProcedureResourceLeave, '/callProcedureleave')
    api.add_resource(DynamicGetResource, '/dynamicGet', '/dynamicGet/<int:id>')
    api.add_resource(DynamicPostResource, '/dynamicPost')
    api.add_resource(DynamicPostResource_With_PKReturn, '/dynamicPost_W_PK')
    api.add_resource(DynamicUpdateResource, '/dynamicUpdate')
    api.add_resource(DynamicDeleteResource, '/dynamicDelete')
    api.add_resource(DynamicInsertOrUpdateResource, '/dynamicInsertOrUpdate')
    api.add_resource(UploadFileResource, '/uploadFile', '/uploadFile/<int:id>')
    api.add_resource(Get_JotForms, '/get_jotform_submissions')
    
    api.add_resource(JobApplicationFormResource, '/jobApplicationForm', '/jobApplicationForm/<int:id>')
    api.add_resource(NewJoinerApprovalResource, '/newJoinerApproval', '/newJoinerApproval/<int:id>')
    api.add_resource(InterviewSchedulesResource, '/interviewSchedules', '/interviewSchedules/<int:id>')
    
    api.add_resource(DeductionHeadResource, '/deductionHead', '/deductionHead/<int:id>')
    api.add_resource(OneTimeDeductionResource, '/oneTimeDeduction', '/oneTimeDeduction/<int:id>')
    api.add_resource(ScheduledDeductionResource, '/scheduledDeduction', '/scheduledDeduction/<int:id>')
    
    api.add_resource(IARResource, '/iar', '/iar/<int:id>')
    api.add_resource(IARRemarksResource, '/iar_remarks', '/iar_remarks/<int:id>')
    api.add_resource(IARTypesResource, '/iar_types', '/iar_types/<int:id>')
    
    api.add_resource(EmailStorageSystemResource, '/emailStorageSystem', '/emailStorageSystem/<int:id>')
    api.add_resource(EmailTypesResource, '/emailTypes', '/emailTypes/<int:id>')
    api.add_resource(EmailSendingResource, '/emailSending', '/emailSending/<int:id>')
    
    api.add_resource(AvailableJobsResource, '/availableJobs', '/availableJobs/<int:id>')

    api.add_resource(StaffInfoResource, '/staffInfo', '/staffInfo/<int:id>')
    api.add_resource(StaffDepartmentResource, '/staffDepartment', '/staffDepartment/<int:id>')
    api.add_resource(StaffTransferResource, '/staffTransfer', '/staffTransfer/<int:id>')
    api.add_resource(StaffIncrementResource, '/staffIncrement', '/staffIncrement/<int:id>')
    api.add_resource(StaffLeaveRequestTempResource, '/staffLeaveRequestTemp')
    
    api.add_resource(StaffShiftResource, '/staffShift/<int:staff_id>/<int:shift_id>')
    
    api.add_resource(MarkDayOffDepsResource, '/markDayOffDeps', '/markDayOffDeps/<int:id>')
    api.add_resource(MarkDayOffHRsResource, '/MarkDayOffHRs', '/MarkDayOffHRs/<int:id>')
    
    api.add_resource(AllowanceHeadResource, '/allowanceHead', '/allowanceHead/<int:id>')
    api.add_resource(OneTimeAllowanceResource, '/oneTimeAllowance', '/oneTimeAllowance/<int:id>')
    api.add_resource(ScheduledAllowanceResource, '/scheduledAllowance', '/scheduledAllowance/<int:id>')
    
    api.add_resource(EmployeeCreationResource, '/employeeCreation')

    api.add_resource(TrainingPostResource, '/training')  
    api.add_resource(CampusWiseUser, '/getCampuswiseUser')
    
    api.add_resource(DocumentsUploader, '/upload')
    api.add_resource(ChangePasswordPostResource, '/ChangePassword')
    api.add_resource(ForgotPasswordResource, '/ForgotPassword')
    api.add_resource(ResetPasswordPostResource, '/ResetPassword')

    api.add_resource(StudentSubmissions_JotForms, '/submit_student_data')
    
    api.add_resource(User_Signup, '/signup')
    
    api.add_resource(Jot_FormUpdate, '/Jot_FormUpdate')

    