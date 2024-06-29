from flask_restful import Api
from flask import Blueprint
from resources.resources import (
    JobApplicationFormResource, NewJoinerApprovalResource, InterviewSchedulesResource, DeductionHeadResource, 
    OneTimeDeductionResource, ScheduledDeductionResource, IARResource, IARRemarksResource , IARTypesResource, 
    EmailStorageSystemResource, EmailTypesResource, AvailableJobsResource, StaffInfoResource, StaffDepartmentResource,
    StaffTransferResource, MarkDayOffDepsResource, MarkDayOffHRsResource, AllowanceHeadResource, OneTimeAllowanceResource,
    ScheduledAllowanceResource, StaffIncrementResource, EmailSendingResource
)
from resources.customApi import (
    DynamicGetResource, CallProcedureResource, DynamicPostResource,
    DynamicUpdateResource, DynamicInsertOrUpdateResource
)
from resources.auth import UserLoginResource

def register_routes(app):
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    api.add_resource(UserLoginResource, '/login')  # Register the authentication resource
    
    ## Dynamic APIs
    api.add_resource(CallProcedureResource, '/callProcedure')
    api.add_resource(DynamicGetResource, '/dynamicGet', '/dynamicGet/<int:id>')
    api.add_resource(DynamicPostResource, '/dynamicPost')
    api.add_resource(DynamicUpdateResource, '/dynamicUpdate')
    api.add_resource(DynamicInsertOrUpdateResource, '/dynamicInsertOrUpdate')
    
    api.add_resource(JobApplicationFormResource, '/job_application_forms', '/job_application_forms/<int:id>')
    api.add_resource(NewJoinerApprovalResource, '/new_joiner_approvals', '/new_joiner_approvals/<int:id>')
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
    
    api.add_resource(MarkDayOffDepsResource, '/markDayOffDeps', '/markDayOffDeps/<int:id>')
    api.add_resource(MarkDayOffHRsResource, '/MarkDayOffHRs', '/MarkDayOffHRs/<int:id>')
    
    api.add_resource(AllowanceHeadResource, '/allowanceHead', '/allowanceHead/<int:id>')
    api.add_resource(OneTimeAllowanceResource, '/oneTimeAllowance', '/oneTimeAllowance/<int:id>')
    api.add_resource(ScheduledAllowanceResource, '/scheduledAllowance', '/scheduledAllowance/<int:id>')
    
    
    api.add_resource(StaffIncrementResource, '/staffIncrement', '/staffIncrement/<int:id>')
    
    