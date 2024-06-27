from app import db
from datetime import datetime
import re
from exceptions import ValidationError
import json

class Users(db.Model):
    __tablename__ = 'USERS'

    user_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=True)
    lastModified = db.Column(db.DateTime, nullable=True)
    inactive = db.Column(db.Boolean, nullable=False)
    firstname = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=True)
    title = db.Column(db.String(30), nullable=True)
    initial = db.Column(db.String(3), nullable=True)
    email = db.Column(db.String(250), nullable=True)
    password = db.Column(db.String(50), nullable=True)
    status = db.Column(db.Boolean, nullable=False)
    userType_id = db.Column(db.Integer, nullable=True)
    mobileNo = db.Column(db.String(15), nullable=True)
    teacher_id = db.Column(db.Integer, nullable=True)
    updaterId = db.Column(db.BigInteger, nullable=True)
    updaterIP = db.Column(db.String(20), nullable=True)
    updaterTerminal = db.Column(db.String(255), nullable=True)
    updateDate = db.Column(db.DateTime, nullable=True)
    creatorId = db.Column(db.BigInteger, nullable=True)
    creatorIP = db.Column(db.String(20), nullable=True)
    creatorTerminal = db.Column(db.String(255), nullable=True)
    createDate = db.Column(db.DateTime, nullable=True)
    guardianCNIC = db.Column(db.String(15), nullable=True)
    campusId = db.Column(db.Integer, nullable=True)
    isClassAccess = db.Column(db.Boolean, nullable=True)
    groupId = db.Column(db.Integer, nullable=True)
    userToken = db.Column(db.String(200), nullable=True)
    notificationToken = db.Column(db.String(200), nullable=True)
    ispasswordchanged = db.Column(db.Boolean, nullable=False)
    isAEN = db.Column(db.Integer, nullable=True)

    # user_campus = db.relationship('UserCampus', back_populates='user')
    
    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            "user_Id": self.user_Id,
            "username": self.username,
            "lastModified": self.lastModified,
            "inactive": self.inactive,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "title": self.title,
            "initial": self.initial,
            "email": self.email,
            "password": self.password,
            "status": self.status,
            "userType_id": self.userType_id,
            "mobileNo": self.mobileNo,
            "teacher_id": self.teacher_id,
            "updaterId": self.updaterId,
            "updaterIP": self.updaterIP,
            "updaterTerminal": self.updaterTerminal,
            "updateDate": self.updateDate,
            "creatorId": self.creatorId,
            "creatorIP": self.creatorIP,
            "creatorTerminal": self.creatorTerminal,
            "createDate": self.createDate,
            "guardianCNIC": self.guardianCNIC,
            "campusId": self.campusId,
            "isClassAccess": self.isClassAccess,
            "groupId": self.groupId,
            "userToken": self.userToken,
            "notificationToken": self.notificationToken,
            "ispasswordchanged": self.ispasswordchanged,
            "isAEN": self.isAEN
        }

class UserType(db.Model):
    __tablename__ = 'UserType'
    userTypeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userTypeName = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    updaterId = db.Column(db.BigInteger)
    updaterIP = db.Column(db.String(20))
    updaterTerminal = db.Column(db.String(255))
    updateDate = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creatorId = db.Column(db.BigInteger)
    creatorIP = db.Column(db.String(20))
    creatorTerminal = db.Column(db.String(255))
    createDate = db.Column(db.DateTime, default=datetime.utcnow)
    campusId = db.Column(db.Integer, db.ForeignKey('UserCampus.id'))

    # campus = db.relationship('UserCampus', back_populates='user_types')

    def __repr__(self):
        return f"<UserType {self.userTypeName}>"

class UserCampus(db.Model):
    __tablename__ = 'UserCampus'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('USERS.user_Id'))
    campusId = db.Column(db.Integer, nullable=True)
    staffId = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    updaterId = db.Column(db.BigInteger, nullable=True)
    updaterIP = db.Column(db.String(20), nullable=True)
    updaterTerminal = db.Column(db.String(255), nullable=True)
    updateDate = db.Column(db.DateTime, nullable=True)
    creatorId = db.Column(db.BigInteger, nullable=True)
    creatorIP = db.Column(db.String(20), nullable=True)
    creatorTerminal = db.Column(db.String(255), nullable=True)
    createDate = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Boolean, nullable=False)

    # user = db.relationship('Users', back_populates='user_campus')
    # roles = db.relationship('Role', back_populates='campus')
    
    def __repr__(self):
        return {"Campus": self.campus_id}
    
    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "campusId": self.campusId,
            "staffId": self.staffId,
            "date": self.date,
            "updaterId": self.updaterId,
            "updaterIP": self.updaterIP,
            "updaterTerminal": self.updaterTerminal,
            "updateDate": self.updateDate,
            "creatorId": self.creatorId,
            "creatorIP": self.creatorIP,
            "creatorTerminal": self.creatorTerminal,
            "createDate": self.createDate.isoformat() if self.createDate else None,
            "status": self.status
        }

class Role(db.Model):
    __tablename__ = 'ROLES'

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roleName = db.Column(db.String(150), nullable=False)
    roleDescription = db.Column(db.String(250), nullable=True)
    isSysAdmin = db.Column(db.Boolean, nullable=False)
    lastModified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Boolean, nullable=False)
    statisticWidget = db.Column(db.Boolean, nullable=True)
    studentInfoWidget = db.Column(db.Boolean, nullable=True)
    studentProgressWidget = db.Column(db.Boolean, nullable=True)
    studentFeeWidget = db.Column(db.Boolean, nullable=True)
    recentActivityWidget = db.Column(db.Boolean, nullable=True)
    calenderWidget = db.Column(db.Boolean, nullable=True)
    studentAttendanceWidget = db.Column(db.Boolean, nullable=True)
    financeWidget = db.Column(db.Boolean, nullable=True)
    bestStudentWidget = db.Column(db.Boolean, nullable=True)
    bestTeacherWidget = db.Column(db.Boolean, nullable=True)
    toDoListWidget = db.Column(db.Boolean, nullable=True)
    updaterId = db.Column(db.BigInteger, nullable=True)
    updaterIP = db.Column(db.String(20), nullable=True)
    updaterTerminal = db.Column(db.String(255), nullable=True)
    updateDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    creatorId = db.Column(db.BigInteger, nullable=True)
    creatorIP = db.Column(db.String(20), nullable=True)
    creatorTerminal = db.Column(db.String(255), nullable=True)
    createDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    probationPeriodWidget = db.Column(db.Boolean, nullable=True)
    campusId = db.Column(db.Integer, db.ForeignKey('UserCampus.id'), nullable=True)
    roomBunkAndAbsent = db.Column(db.Boolean, nullable=True)
    booksDueWidget = db.Column(db.Boolean, nullable=True)

    # campus = db.relationship('UserCampus', back_populates='roles')
    
    def __repr__(self):
        return f'<Role {self.roleName}>'

    def to_dict(self):
        return {
            "role_id": self.role_id,
            "roleName": self.roleName,
            "roleDescription": self.roleDescription,
            "isSysAdmin": self.isSysAdmin,
            "lastModified": self.lastModified,
            "status": self.status,
            "statisticWidget": self.statisticWidget,
            "studentInfoWidget": self.studentInfoWidget,
            "studentProgressWidget": self.studentProgressWidget,
            "studentFeeWidget": self.studentFeeWidget,
            "recentActivityWidget": self.recentActivityWidget,
            "calenderWidget": self.calenderWidget,
            "studentAttendanceWidget": self.studentAttendanceWidget,
            "financeWidget": self.financeWidget,
            "bestStudentWidget": self.bestStudentWidget,
            "bestTeacherWidget": self.bestTeacherWidget,
            "toDoListWidget": self.toDoListWidget,
            "updaterId": self.updaterId,
            "updaterIP": self.updaterIP,
            "updaterTerminal": self.updaterTerminal,
            "updateDate": self.updateDate,
            "creatorId": self.creatorId,
            "creatorIP": self.creatorIP,
            "creatorTerminal": self.creatorTerminal,
            "createDate": self.createDate,
            "probationPeriodWidget": self.probationPeriodWidget,
            "campusId": self.campusId,
            "roomBunkAndAbsent": self.roomBunkAndAbsent,
            "booksDueWidget": self.booksDueWidget
        }

class JobApplicationForm(db.Model):
    __tablename__ = 'JobApplicationForms'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    initial_id = db.Column(db.String(80), nullable=False)

    # Personal Information
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    father_name = db.Column(db.String(80), nullable=False)
    cnic = db.Column(db.String(13), nullable=False)
    passport_number = db.Column(db.String(13), nullable=True)
    dob = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    cell_phone = db.Column(db.String(11), nullable=False)
    alternate_number = db.Column(db.String(11), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    residence = db.Column(db.String(200), nullable=False)

    # Qualification and Experience
    education_level = db.Column(db.String(80), nullable=True)
    education_level_others = db.Column(db.String(80))
    degree = db.Column(db.String(80), nullable=False)
    specialization = db.Column(db.String(80), nullable=False)
    institute = db.Column(db.String(80), nullable=False)

    # Employment History
    fresh = db.Column(db.Boolean)
    experienced = db.Column(db.Boolean)
    total_years_of_experience = db.Column(db.String(50), nullable=True)
    name_of_last_employer = db.Column(db.String(80), nullable=True)
    employment_duration_from = db.Column(db.Date, nullable=True)
    employment_duration_to = db.Column(db.Date, nullable=True)
    designation = db.Column(db.String(80), nullable=True)
    reason_for_leaving = db.Column(db.String(200), nullable=True)
    last_drawn_gross_salary = db.Column(db.String(50), nullable=True)
    benefits_if_any = db.Column(db.String(200), nullable=True)

    # Preference
    preferred_campus = db.Column(db.String(80), nullable=True)
    preferred_location = db.Column(db.String(80), nullable=True)
    preferred_job_type = db.Column(db.String(80), nullable=True)
    section = db.Column(db.String(80), nullable=True)
    subject = db.Column(db.String(80), nullable=True)
    expected_salary = db.Column(db.String(50))
    cv_path = db.Column(db.String(100))
    coverLetter_Path = db.Column(db.String(100), nullable=True)

    createDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<JobApplicationForm {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'initial_id': self.initial_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'father_name': self.father_name,
            'cnic': self.cnic,
            'passport_number': self.passport_number,
            'dob': self.dob.isoformat() if self.dob else None,
            'age': self.age,
            'gender': self.gender,
            'cell_phone': self.cell_phone,
            'alternate_number': self.alternate_number,
            'email': self.email,
            'residence': self.residence,
            'education_level': self.education_level,
            'education_level_others': self.education_level_others,
            'degree': self.degree,
            'specialization': self.specialization,
            'institute': self.institute,
            'fresh': self.fresh,
            'experienced': self.experienced,
            'total_years_of_experience': self.total_years_of_experience,
            'name_of_last_employer': self.name_of_last_employer,
            'employment_duration_from': self.employment_duration_from.isoformat() if self.employment_duration_from else None,
            'employment_duration_to': self.employment_duration_to.isoformat() if self.employment_duration_to else None,
            'designation': self.designation,
            'reason_for_leaving': self.reason_for_leaving,
            'last_drawn_gross_salary': self.last_drawn_gross_salary,
            'benefits_if_any': self.benefits_if_any,
            'preferred_campus': self.preferred_campus,
            'preferred_location': self.preferred_location,
            'preferred_job_type': self.preferred_job_type,
            'section': self.section,
            'subject': self.subject,
            'expected_salary': self.expected_salary,
            'cv_path': self.cv_path,
            'coverLetter_Path': self.coverLetter_Path,
            'createDate': self.createDate.isoformat(),
            'status': self.status,
        }
    
    @staticmethod
    def validate_phone_number(phone_number):
        if not re.match(r"^(?!0+$)\d{11}$", phone_number):
            raise ValidationError("Invalid phone number format.")

    @staticmethod
    def validate_cnic(cnic):
        if not re.match(r'^(?!0{13})\d{13}$', cnic):
            raise ValidationError("Invalid CNIC format.")

    @staticmethod
    def validate_email(email):
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValidationError("Invalid email format.")

class NewJoinerApproval(db.Model):
    __tablename__ = 'NewJoinerApproval'

    newJoinerApproval_Id = db.Column(db.Integer, primary_key=True)
    newJoinerApproval_StaffId = db.Column(db.Integer, nullable=False)
    newJoinerApproval_Salary = db.Column(db.Float, nullable=False)
    newJoinerApproval_HiringApprovedBy = db.Column(db.Integer, nullable=False)
    newJoinerApproval_Remarks = db.Column(db.String(200))
    newJoinerApproval_FileVerified = db.Column(db.Boolean, nullable=False)
    newJoinerApproval_EmpDetailsVerified = db.Column(db.Boolean, nullable=False)
    newJoinerApproval_AddToPayrollMonth = db.Column(db.String(20), nullable=False)
    createdDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    createdBy = db.Column(db.Integer, nullable=False)
    updatedBy = db.Column(db.Integer)
    updatedDate = db.Column(db.DateTime)
    inActive = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<NewJoinerApproval {self.newJoinerApproval_Id}>'
    
    def to_dict(self):
        return {
            "newJoinerApproval_Id": self.newJoinerApproval_Id,
            "newJoinerApproval_StaffId": self.newJoinerApproval_StaffId,
            "newJoinerApproval_Salary" : self.newJoinerApproval_Salary,
            "newJoinerApproval_HiringApprovedBy" : self.newJoinerApproval_HiringApprovedBy,
            "newJoinerApproval_Remarks" : self.newJoinerApproval_Remarks,
            "newJoinerApproval_FileVerified" : self.newJoinerApproval_FileVerified,
            "newJoinerApproval_EmpDetailsVerified" : self.newJoinerApproval_EmpDetailsVerified,
            "newJoinerApproval_AddToPayrollMonth" : self.newJoinerApproval_AddToPayrollMonth,
            "createdDate" : self.createdDate.isoformat(),
            "createdBy" : self.createdBy,
            "updatedBy" : self.updatedBy,
            "updatedDate" : self.updatedDate.isoformat() if self.updatedDate else None,
            "inActive" : self.inActive
        }

class InterviewSchedules(db.Model):
    __tablename__ = 'InterviewSchedules'
    
    id = db.Column(db.Integer, primary_key=True)
    interviewTypeId = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    time = db.Column(db.Time, nullable=True)
    venue = db.Column(db.String(500), nullable=True)
    jobApplicationFormId = db.Column(db.Integer, nullable=True)
    interviewConductorId = db.Column(db.String(300), nullable=True)
    demoTopic = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(250), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    createdBy = db.Column(db.Integer, nullable=True)
    createDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    campusId = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<InterviewSchedule {self.id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "interviewTypeId": self.interviewTypeId,
            "date": self.date.isoformat() if self.date else None,
            "time": self.time.isoformat() if self.time else None,
            "venue": self.venue,
            "jobApplicationFormId": self.jobApplicationFormId,
            "interviewConductorId": self.interviewConductorId,
            "demoTopic": self.demoTopic,
            "position": self.position,
            "location": self.location,
            "createdBy": self.createdBy,
            "createDate": self.createDate.isoformat() if self.createDate else None,
            "campusId": self.campusId
            
        }

class DeductionHead(db.Model):
    __tablename__ = 'DeductionHead'
    deductionHead_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deductionHead_Name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<DeductionHead {self.deductionHead_Id}>'
    
    def to_dict(self):
        return {
            "deductionHead_Id": self.deductionHead_Id,
            "deductionHead_Name": self.deductionHead_Name
        }

class OneTimeDeduction(db.Model):
    __tablename__ = 'OneTimeDeduction'
    oneTimeDeduction_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oneTimeDeduction_StaffId = db.Column(db.Integer, nullable=False)
    oneTimeDeduction_DeductionHeadId = db.Column(db.Integer, db.ForeignKey('DeductionHead.deductionHead_Id'), nullable=False)
    oneTimeDeduction_Amount = db.Column(db.Float, nullable=False)
    oneTimeDeduction_DeductionMonth = db.Column(db.String(15), nullable=False)
    oneTimeDeduction_ApprovedBy = db.Column(db.Integer, nullable=False)
    creatorId = db.Column(db.Integer, nullable=False)
    createDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatorId = db.Column(db.Integer, nullable=True)
    updateDate = db.Column(db.DateTime, nullable=True)
    inActive = db.Column(db.Boolean, nullable=False)

    deduction_head = db.relationship('DeductionHead', backref=db.backref('oneTimeDeduction', lazy=True))
    
    def __repr__(self):
        return f'<DeductionHead {self.oneTimeDeduction_Id}>'
    
    def to_dict(self):
        return {
            "oneTimeDeduction_Id": self.oneTimeDeduction_Id,
            "oneTimeDeduction_StaffId": self.oneTimeDeduction_StaffId,
            "oneTimeDeduction_DeductionHeadId": self.oneTimeDeduction_DeductionHeadId,
            "oneTimeDeduction_Amount": self.oneTimeDeduction_Amount,
            "oneTimeDeduction_DeductionMonth": self.oneTimeDeduction_DeductionMonth,
            "oneTimeDeduction_ApprovedBy": self.oneTimeDeduction_ApprovedBy,
            "creatorId": self.creatorId,
            "createDate": self.createDate.isoformat(),
            "updatorId": self.updatorId,
            "updateDate": self.updateDate.isoformat() if self.updateDate else None,
            "inActive": self.inActive
        }

class ScheduledDeduction(db.Model):
    __tablename__ = 'ScheduledDeduction'
    scheduledDeduction_Id = db.Column(db.Integer, primary_key=True)
    scheduledDeduction_StaffId = db.Column(db.Integer, nullable=False)
    scheduledDeduction_DeductionHeadId = db.Column(db.Integer, db.ForeignKey('DeductionHead.deductionHead_Id'), nullable=False)
    scheduledDeduction_AmountPerMonth = db.Column(db.Float, nullable=False)
    scheduledDeduction_StartDate = db.Column(db.DateTime, nullable=False)
    scheduledDeduction_EndDate = db.Column(db.DateTime, nullable=False)
    scheduledDeduction_ApprovedBy = db.Column(db.Integer, nullable=False)
    creatorId = db.Column(db.Integer, nullable=False)
    createDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatorId = db.Column(db.Integer)
    updateDate = db.Column(db.DateTime)
    inActive = db.Column(db.Boolean, nullable=False)
    
    deduction_head = db.relationship('DeductionHead', backref=db.backref('scheduledDeduction', lazy=True))
    
    def __repr__(self):
        return f'<DeductionHead {self.deductionHead_Id}>'
    
    def to_dict(self):
        return {
            "scheduledDeduction_Id": self.scheduledDeduction_Id,
            "scheduledDeduction_StaffId": self.scheduledDeduction_StaffId,
            "scheduledDeduction_DeductionHeadId": self.scheduledDeduction_DeductionHeadId,
            "scheduledDeduction_AmountPerMonth": self.scheduledDeduction_AmountPerMonth,
            "scheduledDeduction_StartDate": self.scheduledDeduction_StartDate.isoformat(),
            "scheduledDeduction_EndDate": self.scheduledDeduction_EndDate.isoformat(),
            "scheduledDeduction_ApprovedBy": self.scheduledDeduction_ApprovedBy,
            "creatorId": self.creatorId,
            "createDate": self.createDate.isoformat(),
            "updatorId": self.updatorId,
            "updateDate": self.updateDate.isoformat() if self.updateDate else None,
            "inActive": self.inActive
        }

class IAR(db.Model):
    __tablename__ = 'IAR'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    form_Id = db.Column(db.Integer, nullable=False)
    IAR_Type_Id = db.Column(db.Integer, db.ForeignKey('IAR_Types.id'), nullable=False)
    status_Check = db.Column(db.Boolean, nullable=False)
    remarks = db.Column(db.String(150), nullable=False)
    creatorId = db.Column(db.Integer, nullable=True)
    createdDate = db.Column(db.DateTime, nullable=True)

    iar_type = db.relationship('IAR_Types', backref=db.backref('iars', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'form_Id': self.form_Id,
            'IAR_Type_Id': self.IAR_Type_Id,
            'status_Check': self.status_Check,
            'remarks': self.remarks,
            'creatorId': self.creatorId,
            'createdDate': self.createdDate.isoformat() if self.createdDate else None
        }

class IAR_Remarks(db.Model):
    __tablename__ = 'IAR_Remarks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    IAR_Id = db.Column(db.Integer, db.ForeignKey('IAR.id'), nullable=False)
    remarks = db.Column(db.String(150), nullable=True)
    status = db.Column(db.Boolean, nullable=True)
    creatorId = db.Column(db.Integer, nullable=True)
    createDate = db.Column(db.DateTime, nullable=True)

    iar = db.relationship('IAR', backref=db.backref('IAR_Id', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'IAR_Id': self.IAR_Id,
            'remarks': self.remarks,
            'status': self.status,
            'creatorId': self.creatorId,
            'createDate': self.createDate.isoformat() if self.createDate else None
        }

class IAR_Types(db.Model):
    __tablename__ = 'IAR_Types'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class EmailTypes(db.Model):
    __tablename__ = 'EmailTypes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class EmailStorageSystem(db.Model):
    __tablename__ = 'EmailStorageSystem'
    email_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_Title = db.Column(db.String(100), nullable=True)
    email_Subject = db.Column(db.String(250), nullable=True)
    email_Body = db.Column(db.Text, nullable=True)
    status = db.Column(db.Boolean, nullable=True)
    creatorId = db.Column(db.Integer, nullable=True)
    createdDate = db.Column(db.DateTime, nullable=True)
    updatorId = db.Column(db.Integer, nullable=True)
    updatedDate = db.Column(db.DateTime, nullable=True)
    emailType = db.Column(db.Integer, db.ForeignKey('EmailTypes.id'), nullable=True)

    email_type = db.relationship('EmailTypes', backref=db.backref('emails', lazy=True))

    def to_dict(self):
        return {
            'email_Id': self.email_Id,
            'email_Title': self.email_Title,
            'email_Subject': self.email_Subject,
            'email_Body': self.email_Body,
            'status': self.status,
            'creatorId': self.creatorId,
            'createdDate': self.createdDate.isoformat() if self.createdDate else None,
            'updatorId': self.updatorId,
            'updatedDate': self.updatedDate.isoformat() if self.updatedDate else None,
            'emailType': self.emailType
        }

class AvailableJobs(db.Model):
    __tablename__ = 'AvailableJobs'
    job_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_Title = db.Column(db.String(100), nullable=False)
    job_Level = db.Column(db.String(100), nullable=False)
    job_PostedBy = db.Column(db.Integer, nullable=True)
    job_Status = db.Column(db.Boolean, nullable=True)
    creatorId = db.Column(db.Integer, nullable=True)
    createdDate = db.Column(db.DateTime, nullable=True)
    updatorId = db.Column(db.Integer, nullable=True)
    updatedDate = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'job_Id': self.job_Id,
            'job_Title': self.job_Title,
            'job_Level': self.job_Level,
            'job_PostedBy': self.job_PostedBy,
            'job_Status': self.job_Status,
            'creatorId': self.creatorId,
            'createdDate': self.createdDate.isoformat() if self.createdDate else None,
            'updatorId': self.updatorId,
            'updatedDate': self.updatedDate.isoformat() if self.updatedDate else None
        }

class StaffInfo(db.Model):
    __tablename__ = 'StaffInfo'
    Staff_ID = db.Column(db.Integer, primary_key=True)
    Personal_ID = db.Column(db.String(100))
    S_Name = db.Column(db.String(50), nullable=False)
    S_FName = db.Column(db.String(100))
    S_Gender = db.Column(db.Integer, nullable=False)
    S_CNIC = db.Column(db.String(50))
    S_Email = db.Column(db.String(250))
    S_ContactNo = db.Column(db.String(50))
    S_DoB = db.Column(db.DateTime, nullable=False)
    S_JoiningDate = db.Column(db.DateTime, nullable=False)
    S_firstJOrderNo = db.Column(db.String(50))
    S_JoiningDesg = db.Column(db.Integer)
    S_JoiningGrade = db.Column(db.Integer)
    S_firstJPlace = db.Column(db.String(50))
    S_PresentDesignation = db.Column(db.Integer)
    S_PresentGrade = db.Column(db.Integer)
    S_SchoolName = db.Column(db.String(100))
    S_District = db.Column(db.String(50))
    S_Union = db.Column(db.String(50))
    S_WardNo = db.Column(db.String(50))
    S_Village = db.Column(db.String(50))
    Designation_ID = db.Column(db.Integer, nullable=False)
    Grade_ID = db.Column(db.Integer)
    IsActive = db.Column(db.Boolean, nullable=False)
    IsNonTeacher = db.Column(db.Boolean, nullable=False)
    S_Salary = db.Column(db.Float)
    UpdaterId = db.Column(db.BigInteger)
    UpdaterIP = db.Column(db.String(20))
    UpdaterTerminal = db.Column(db.String(255))
    UpdateDate = db.Column(db.DateTime)
    CreatorId = db.Column(db.BigInteger)
    CreatorIP = db.Column(db.String(20))
    CreatorTerminal = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime)
    PhotoPath = db.Column(db.String(500))
    IsDisable = db.Column(db.Boolean, nullable=False)
    disableDetail = db.Column(db.String(255))
    EOBI = db.Column(db.String(50))
    ProbationPeriod = db.Column(db.Float)
    ProbationEndDate = db.Column(db.DateTime)
    IsPermanent = db.Column(db.Boolean, nullable=False)
    IsTerminate = db.Column(db.Boolean)
    DepartmentId = db.Column(db.Integer)
    HouseNo = db.Column(db.String(255))
    Street_Sector_BlockNo = db.Column(db.String(255))
    AreaId = db.Column(db.BigInteger)
    CityId = db.Column(db.BigInteger)
    District = db.Column(db.String(50))
    Province = db.Column(db.String(50))
    CountryId = db.Column(db.BigInteger)
    PresentAddress = db.Column(db.String(500))
    TempAddress = db.Column(db.String(500))
    Whatsapp = db.Column(db.String(20))
    EmergencyContactName = db.Column(db.String(50))
    EmergencyContactNo = db.Column(db.String(50))
    HomeNo = db.Column(db.String(20))
    Rent_Personal = db.Column(db.String(20))
    MaritalStatus = db.Column(db.String(50))
    AccountTitle = db.Column(db.String(50))
    AccountNo = db.Column(db.String(50))
    BankName = db.Column(db.String(50))
    Branch = db.Column(db.String(50))
    IsFatherName = db.Column(db.Boolean)
    FHWName = db.Column(db.String(50))
    FHWCNIC = db.Column(db.String(20))
    FWHDOB = db.Column(db.DateTime)
    CampusId = db.Column(db.Integer)
    BarcodeId = db.Column(db.String(50), nullable=False)
    IsAppearLive = db.Column(db.Boolean, nullable=False)
    Category = db.Column(db.Integer)
    FId = db.Column(db.Integer)
    Initials = db.Column(db.String(50))
    IsSalaryOn = db.Column(db.Boolean)
    EmpId = db.Column(db.Integer)
    IsAEN = db.Column(db.Integer)
    ReportingOfficerId = db.Column(db.Integer)
    FileNumber = db.Column(db.Integer)
    FileLocation = db.Column(db.String(255))
    IsExit = db.Column(db.Boolean)
    Grace_In = db.Column(db.Integer)
    Grace_Out = db.Column(db.Integer)
    ShiftType = db.Column(db.Integer)

    def to_dict(self):
        return {
            'Staff_ID': self.Staff_ID,
            'Personal_ID': self.Personal_ID,
            'S_Name': self.S_Name,
            'S_FName': self.S_FName,
            'S_Gender': self.S_Gender,
            'S_CNIC': self.S_CNIC,
            'S_Email': self.S_Email,
            'S_ContactNo': self.S_ContactNo,
            'S_DoB': self.S_DoB.isoformat() if self.S_DoB else None,
            'S_JoiningDate': self.S_JoiningDate.isoformat() if self.S_JoiningDate else None,
            'S_firstJOrderNo': self.S_firstJOrderNo,
            'S_JoiningDesg': self.S_JoiningDesg,
            'S_JoiningGrade': self.S_JoiningGrade,
            'S_firstJPlace': self.S_firstJPlace,
            'S_PresentDesignation': self.S_PresentDesignation,
            'S_PresentGrade': self.S_PresentGrade,
            'S_SchoolName': self.S_SchoolName,
            'S_District': self.S_District,
            'S_Union': self.S_Union,
            'S_WardNo': self.S_WardNo,
            'S_Village': self.S_Village,
            'Designation_ID': self.Designation_ID,
            'Grade_ID': self.Grade_ID,
            'IsActive': self.IsActive,
            'IsNonTeacher': self.IsNonTeacher,
            'S_Salary': self.S_Salary,
            'UpdaterId': self.UpdaterId,
            'UpdaterIP': self.UpdaterIP,
            'UpdaterTerminal': self.UpdaterTerminal,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'CreatorId': self.CreatorId,
            'CreatorIP': self.CreatorIP,
            'CreatorTerminal': self.CreatorTerminal,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None,
            'PhotoPath': self.PhotoPath,
            'IsDisable': self.IsDisable,
            'disableDetail': self.disableDetail,
            'EOBI': self.EOBI,
            'ProbationPeriod': self.ProbationPeriod,
            'ProbationEndDate': self.ProbationEndDate.isoformat() if self.ProbationEndDate else None,
            'IsPermanent': self.IsPermanent,
            'IsTerminate': self.IsTerminate,
            'DepartmentId': self.DepartmentId,
            'HouseNo': self.HouseNo,
            'Street_Sector_BlockNo': self.Street_Sector_BlockNo,
            'AreaId': self.AreaId,
            'CityId': self.CityId,
            'District': self.District,
            'Province': self.Province,
            'CountryId': self.CountryId,
            'PresentAddress': self.PresentAddress,
            'TempAddress': self.TempAddress,
            'Whatsapp': self.Whatsapp,
            'EmergencyContactName': self.EmergencyContactName,
            'EmergencyContactNo': self.EmergencyContactNo,
            'HomeNo': self.HomeNo,
            'Rent_Personal': self.Rent_Personal,
            'MaritalStatus': self.MaritalStatus,
            'AccountTitle': self.AccountTitle,
            'AccountNo': self.AccountNo,
            'BankName': self.BankName,
            'Branch': self.Branch,
            'IsFatherName': self.IsFatherName,
            'FHWName': self.FHWName,
            'FHWCNIC': self.FHWCNIC,
            'FWHDOB': self.FWHDOB.isoformat() if self.FWHDOB else None,
            'CampusId': self.CampusId,
            'BarcodeId': self.BarcodeId,
            'IsAppearLive': self.IsAppearLive,
            'Category': self.Category,
            'FId': self.FId,
            'Initials': self.Initials,
            'IsSalaryOn': self.IsSalaryOn,
            'EmpId': self.EmpId,
            'IsAEN': self.IsAEN,
            'ReportingOfficerId': self.ReportingOfficerId,
            'FileNumber': self.FileNumber,
            'FileLocation': self.FileLocation,
            'IsExit': self.IsExit,
            'Grace_In': self.Grace_In,
            'Grace_Out': self.Grace_Out,
            'ShiftType': self.ShiftType
        }

class StaffDepartment(db.Model):
    __tablename__ = 'StaffDepartments'

    Id = db.Column(db.Integer, primary_key=True)
    DepartmentName = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Boolean, nullable=True)
    UpdaterId = db.Column(db.BigInteger, nullable=True)
    UpdaterIP = db.Column(db.String(20), nullable=True)
    UpdaterTerminal = db.Column(db.String(255), nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)
    CreatorId = db.Column(db.BigInteger, nullable=True)
    CreatorIP = db.Column(db.String(20), nullable=True)
    CreatorTerminal = db.Column(db.String(255), nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True)
    CampusId = db.Column(db.Integer, nullable=True)
    ManagerId = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'Id': self.Id,
            'DepartmentName': self.DepartmentName,
            'status': self.status,
            'UpdaterId': self.UpdaterId,
            'UpdaterIP': self.UpdaterIP,
            'UpdaterTerminal': self.UpdaterTerminal,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'CreatorId': self.CreatorId,
            'CreatorIP': self.CreatorIP,
            'CreatorTerminal': self.CreatorTerminal,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None,
            'CampusId': self.CampusId,
            'ManagerId': self.ManagerId,
        }

class StaffTransfer(db.Model):
    __tablename__ = 'StaffTransfer'

    Id = db.Column(db.Integer, primary_key=True)
    StaffId = db.Column(db.Integer, nullable=False)
    Transfer_Type = db.Column(db.String(50), nullable=True)
    Transfer_Date = db.Column(db.DateTime, nullable=True)
    Reason_for_Transfer = db.Column(db.String(100), nullable=True)
    Transfer_from_Campus = db.Column(db.Integer, nullable=True)
    Transfer_To_Campus = db.Column(db.Integer, nullable=True)
    DepartmentId = db.Column(db.Integer, nullable=True)
    DesignationId = db.Column(db.Integer, nullable=True)
    ReportingOfficerId = db.Column(db.Integer, nullable=True)
    Transfer_initiated_by = db.Column(db.Integer, nullable=True)
    Transfer_approval = db.Column(db.Integer, nullable=True)
    Remarks = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Boolean, nullable=True)
    CampusId = db.Column(db.Integer, nullable=True)
    CreatorId = db.Column(db.Integer, nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    UpdaterId = db.Column(db.Integer, nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'Id': self.Id,
            'StaffId': self.StaffId,
            'Transfer_Type': self.Transfer_Type,
            'Transfer_Date': self.Transfer_Date.isoformat() if self.Transfer_Date else None,
            'Reason_for_Transfer': self.Reason_for_Transfer,
            'Transfer_from_Campus': self.Transfer_from_Campus,
            'Transfer_To_Campus': self.Transfer_To_Campus,
            'DepartmentId': self.DepartmentId,
            'DesignationId': self.DesignationId,
            'ReportingOfficerId': self.ReportingOfficerId,
            'Transfer_initiated_by': self.Transfer_initiated_by,
            'Transfer_approval': self.Transfer_approval,
            'Remarks': self.Remarks,
            'status': self.status,
            'CampusId': self.CampusId,
            'CreatorId': self.CreatorId,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None,
            'UpdaterId': self.UpdaterId,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None
        }

class StaffShift(db.Model):
    __tablename__ = 'StaffShifts'
    StaffId = db.Column(db.Integer, primary_key=True)
    ShiftId = db.Column(db.Integer, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedOn = db.Column(db.DateTime)
    CreatedByUserId = db.Column(db.Integer, nullable=False)
    UpdatedByUserId = db.Column(db.Integer)
    CampusId = db.Column(db.Integer)

    def to_dict(self):
        return {
            'StaffId': self.StaffId,
            'ShiftId': self.ShiftId,
            'CreatedOn': self.CreatedOn.isoformat() if self.CreatedOn else None,
            'UpdatedOn': self.UpdatedOn.isoformat() if self.UpdatedOn else None,
            'CreatedByUserId': self.CreatedByUserId,
            'UpdatedByUserId': self.UpdatedByUserId,
            'CampusId': self.CampusId
        }