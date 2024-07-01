from app import db
from datetime import datetime
import re
from exceptions import ValidationError
import json

class Users(db.Model):
    __tablename__ = 'USERS'

    User_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username = db.Column(db.String(100), nullable=True)
    LastModified = db.Column(db.DateTime, nullable=True)
    Inactive = db.Column(db.Boolean, nullable=False)
    Firstname = db.Column(db.String(50), nullable=True)
    Lastname = db.Column(db.String(50), nullable=True)
    Title = db.Column(db.String(30), nullable=True)
    Initial = db.Column(db.String(3), nullable=True)
    Email = db.Column(db.String(250), nullable=True)
    Password = db.Column(db.String(50), nullable=True)
    Status = db.Column(db.Boolean, nullable=False)
    UserType_id = db.Column(db.Integer, nullable=True)
    MobileNo = db.Column(db.String(15), nullable=True)
    Teacher_id = db.Column(db.Integer, nullable=True)
    UpdaterId = db.Column(db.BigInteger, nullable=True)
    UpdaterIP = db.Column(db.String(20), nullable=True)
    UpdaterTerminal = db.Column(db.String(255), nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)
    CreatorId = db.Column(db.BigInteger, nullable=True)
    CreatorIP = db.Column(db.String(20), nullable=True)
    CreatorTerminal = db.Column(db.String(255), nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True)
    GuardianCNIC = db.Column(db.String(15), nullable=True)
    CampusId = db.Column(db.Integer, nullable=True)
    IsClassAccess = db.Column(db.Boolean, nullable=True)
    GroupId = db.Column(db.Integer, nullable=True)
    UserToken = db.Column(db.String(200), nullable=True)
    NotificationToken = db.Column(db.String(200), nullable=True)
    Ispasswordchanged = db.Column(db.Boolean, nullable=False)
    IsAEN = db.Column(db.Integer, nullable=True)

    # user_campus = db.relationship('UserCampus', back_populates='user')
    
    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            "User_Id": self.User_Id,
            "Username": self.Username,
            "LastModified": self.LastModified,
            "Inactive": self.Inactive,
            "Firstname": self.Firstname,
            "Lastname": self.Lastname,
            "Title": self.Title,
            "Initial": self.Initial,
            "Email": self.Email,
            "Password": self.Password,
            "Status": self.Status,
            "UserType_id": self.UserType_id,
            "MobileNo": self.MobileNo,
            "Teacher_id": self.Teacher_id,
            "UpdaterId": self.UpdaterId,
            "UpdaterIP": self.UpdaterIP,
            "UpdaterTerminal": self.UpdaterTerminal,
            "UpdateDate": self.UpdateDate,
            "CreatorId": self.CreatorId,
            "CreatorIP": self.CreatorIP,
            "CreatorTerminal": self.CreatorTerminal,
            "CreateDate": self.CreateDate,
            "GuardianCNIC": self.GuardianCNIC,
            "CampusId": self.CampusId,
            "IsClassAccess": self.IsClassAccess,
            "GroupId": self.GroupId,
            "UserToken": self.UserToken,
            "NotificationToken": self.NotificationToken,
            "Ispasswordchanged": self.Ispasswordchanged,
            "IsAEN": self.IsAEN
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

class Form(db.Model):
    __tablename__ = 'Forms'
    FormId = db.Column(db.Integer, primary_key=True)
    FormName = db.Column(db.String(100), nullable=False)
    Controller = db.Column(db.String(450))
    UpdaterId = db.Column(db.BigInteger)
    UpdaterIP = db.Column(db.String(20))
    UpdaterTerminal = db.Column(db.String(255))
    UpdateDate = db.Column(db.DateTime)
    CreatorId = db.Column(db.BigInteger)
    CreatorIP = db.Column(db.String(20))
    CreatorTerminal = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow)
    CampusId = db.Column(db.Integer)

    def to_dict(self):
        return {
            'FormId': self.FormId,
            'FormName': self.FormName,
            'Controller': self.Controller,
            'UpdaterId': self.UpdaterId,
            'UpdaterIP': self.UpdaterIP,
            'UpdaterTerminal': self.UpdaterTerminal,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'CreatorId': self.CreatorId,
            'CreatorIP': self.CreatorIP,
            'CreatorTerminal': self.CreatorTerminal,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None,
            'CampusId': self.CampusId
        }

class FormDetails(db.Model):
    __tablename__ = 'FormDetails'
    Id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    FormId = db.Column(db.Integer, nullable=False)
    Action = db.Column(db.String(450), nullable=False)
    ActionName = db.Column(db.String(1000), nullable=False)
    IsReport = db.Column(db.Boolean, nullable=False)
    UserTypeId = db.Column(db.Integer)
    Status = db.Column(db.Boolean, nullable=False)
    UpdaterId = db.Column(db.BigInteger)
    UpdaterIP = db.Column(db.String(20))
    UpdaterTerminal = db.Column(db.String(255))
    UpdateDate = db.Column(db.DateTime)
    CreatorId = db.Column(db.BigInteger)
    CreatorIP = db.Column(db.String(20))
    CreatorTerminal = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow)
    CampusId = db.Column(db.Integer)

    def to_dict(self):
        return {
            'Id': self.Id,
            'FormId': self.FormId,
            'Action': self.Action,
            'ActionName': self.ActionName,
            'IsReport': self.IsReport,
            'UserTypeId': self.UserTypeId,
            'Status': self.Status,
            'UpdaterId': self.UpdaterId,
            'UpdaterIP': self.UpdaterIP,
            'UpdaterTerminal': self.UpdaterTerminal,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'CreatorId': self.CreatorId,
            'CreatorIP': self.CreatorIP,
            'CreatorTerminal': self.CreatorTerminal,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None,
            'CampusId': self.CampusId
        }

class FormDetailPermissions(db.Model):
    __tablename__ = 'FormDetailPermissions'
    Id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    FormDetailId = db.Column(db.BigInteger)
    RoleId = db.Column(db.Integer)
    Status = db.Column(db.Boolean, nullable=False)
    UpdaterId = db.Column(db.BigInteger)
    UpdaterIP = db.Column(db.String(20))
    UpdaterTerminal = db.Column(db.String(255))
    UpdateDate = db.Column(db.DateTime)
    CreatorId = db.Column(db.BigInteger)
    CreatorIP = db.Column(db.String(20))
    CreatorTerminal = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow)
    CampusId = db.Column(db.Integer)

    def to_dict(self):
        return {
            'Id': self.Id,
            'FormDetailId': self.FormDetailId,
            'RoleId': self.RoleId,
            'Status': self.Status,
            'UpdaterId': self.UpdaterId,
            'UpdaterIP': self.UpdaterIP,
            'UpdaterTerminal': self.UpdaterTerminal,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'CreatorId': self.CreatorId,
            'CreatorIP': self.CreatorIP,
            'CreatorTerminal': self.CreatorTerminal,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None,
            'CampusId': self.CampusId
        }

class LNK_USER_ROLE(db.Model):
    __tablename__ = 'LNK_USER_ROLE'
    User_Id = db.Column(db.Integer, primary_key=True)
    Role_Id = db.Column(db.Integer, primary_key=True)
    UpdaterId = db.Column(db.BigInteger)
    UpdaterIP = db.Column(db.String(20))
    UpdaterTerminal = db.Column(db.String(255))
    UpdateDate = db.Column(db.DateTime)
    CreatorId = db.Column(db.BigInteger)
    CreatorIP = db.Column(db.String(20))
    CreatorTerminal = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow)
    CampusId = db.Column(db.Integer)

    def to_dict(self):
        return {
            'User_Id': self.User_Id,
            'Role_Id': self.Role_Id,
            'UpdaterId': self.UpdaterId,
            'UpdaterIP': self.UpdaterIP,
            'UpdaterTerminal': self.UpdaterTerminal,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'CreatorId': self.CreatorId,
            'CreatorIP': self.CreatorIP,
            'CreatorTerminal': self.CreatorTerminal,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None,
            'CampusId': self.CampusId
        }

class JobApplicationForm(db.Model):
    __tablename__ = 'JobApplicationForms'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Initial_id = db.Column(db.String(80), nullable=False)

    # Personal Information
    First_name = db.Column(db.String(80), nullable=False)
    Last_name = db.Column(db.String(80), nullable=False)
    Father_name = db.Column(db.String(80), nullable=False)
    Cnic = db.Column(db.String(13), nullable=False)
    Passport_number = db.Column(db.String(13), nullable=True)
    Dob = db.Column(db.Date, nullable=False)
    Age = db.Column(db.Integer, nullable=False)
    Gender = db.Column(db.String(10), nullable=False)
    Cell_phone = db.Column(db.String(11), nullable=False)
    Alternate_number = db.Column(db.String(11), nullable=True)
    Email = db.Column(db.String(120), nullable=False)
    Residence = db.Column(db.String(200), nullable=False)

    # Qualification and Experience
    Education_level = db.Column(db.String(80), nullable=True)
    Education_level_others = db.Column(db.String(80))
    Degree = db.Column(db.String(80), nullable=False)
    Specialization = db.Column(db.String(80), nullable=False)
    Institute = db.Column(db.String(80), nullable=False)

    # Employment History
    Fresh = db.Column(db.Boolean)
    Experienced = db.Column(db.Boolean)
    Total_years_of_experience = db.Column(db.String(50), nullable=True)
    Name_of_last_employer = db.Column(db.String(80), nullable=True)
    Employment_duration_from = db.Column(db.Date, nullable=True)
    Employment_duration_to = db.Column(db.Date, nullable=True)
    Designation = db.Column(db.String(80), nullable=True)
    Reason_for_leaving = db.Column(db.String(200), nullable=True)
    Last_drawn_gross_salary = db.Column(db.String(50), nullable=True)
    Benefits_if_any = db.Column(db.String(200), nullable=True)

    # Preference
    Preferred_campus = db.Column(db.String(80), nullable=True)
    Preferred_location = db.Column(db.String(80), nullable=True)
    Preferred_job_type = db.Column(db.String(80), nullable=True)
    Section = db.Column(db.String(80), nullable=True)
    Subject = db.Column(db.String(80), nullable=True)
    Expected_salary = db.Column(db.String(50))
    Cv_path = db.Column(db.String(100))
    CoverLetter_Path = db.Column(db.String(100), nullable=True)

    CreateDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    Status = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<JobApplicationForm {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'Id': self.Id,
            'Initial_id': self.Initial_id,
            'First_name': self.First_name,
            'Last_name': self.Last_name,
            'Father_name': self.Father_name,
            'Cnic': self.Cnic,
            'Passport_number': self.Passport_number,
            'Dob': self.Dob.isoformat() if self.Dob else None,
            'Age': self.Age,
            'Gender': self.Gender,
            'Cell_phone': self.Cell_phone,
            'Alternate_number': self.Alternate_number,
            'Email': self.Email,
            'Residence': self.Residence,
            'Education_level': self.Education_level,
            'Education_level_others': self.Education_level_others,
            'Degree': self.Degree,
            'Specialization': self.Specialization,
            'Institute': self.Institute,
            'Fresh': self.Fresh,
            'Experienced': self.Experienced,
            'Total_years_of_experience': self.Total_years_of_experience,
            'Name_of_last_employer': self.Name_of_last_employer,
            'Employment_duration_from': self.Employment_duration_from.isoformat() if self.Employment_duration_from else None,
            'Employment_duration_to': self.Employment_duration_to.isoformat() if self.Employment_duration_to else None,
            'Designation': self.Designation,
            'Reason_for_leaving': self.Reason_for_leaving,
            'Last_drawn_gross_salary': self.Last_drawn_gross_salary,
            'Benefits_if_any': self.Benefits_if_any,
            'Preferred_campus': self.Preferred_campus,
            'Preferred_location': self.Preferred_location,
            'Preferred_job_type': self.Preferred_job_type,
            'Section': self.Section,
            'Subject': self.Subject,
            'Expected_salary': self.Expected_salary,
            'Cv_path': self.Cv_path,
            'CoverLetter_Path': self.CoverLetter_Path,
            'CreateDate': self.CreateDate.isoformat(),
            'Status': self.Status,
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

    NewJoinerApproval_Id = db.Column(db.Integer, primary_key=True)
    NewJoinerApproval_StaffId = db.Column(db.Integer, nullable=False)
    NewJoinerApproval_Salary = db.Column(db.Float, nullable=False)
    NewJoinerApproval_HiringApprovedBy = db.Column(db.Integer, nullable=False)
    NewJoinerApproval_Remarks = db.Column(db.String(200))
    NewJoinerApproval_FileVerified = db.Column(db.Boolean, nullable=False)
    NewJoinerApproval_EmpDetailsVerified = db.Column(db.Boolean, nullable=False)
    NewJoinerApproval_AddToPayrollMonth = db.Column(db.String(20), nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    CreatedBy = db.Column(db.Integer, nullable=False)
    UpdatedBy = db.Column(db.Integer)
    UpdatedDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<NewJoinerApproval {self.NewJoinerApproval_Id}>'
    
    def to_dict(self):
        return {
            "NewJoinerApproval_Id": self.NewJoinerApproval_Id,
            "NewJoinerApproval_StaffId": self.NewJoinerApproval_StaffId,
            "NewJoinerApproval_Salary" : self.NewJoinerApproval_Salary,
            "NewJoinerApproval_HiringApprovedBy" : self.NewJoinerApproval_HiringApprovedBy,
            "NewJoinerApproval_Remarks" : self.NewJoinerApproval_Remarks,
            "NewJoinerApproval_FileVerified" : self.NewJoinerApproval_FileVerified,
            "NewJoinerApproval_EmpDetailsVerified" : self.NewJoinerApproval_EmpDetailsVerified,
            "NewJoinerApproval_AddToPayrollMonth" : self.NewJoinerApproval_AddToPayrollMonth,
            "CreatedDate" : self.CreatedDate.isoformat(),
            "CreatedBy" : self.CreatedBy,
            "UpdatedBy" : self.UpdatedBy,
            "UpdatedDate" : self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            "InActive" : self.InActive
        }

class InterviewSchedules(db.Model):
    __tablename__ = 'InterviewSchedules'
    
    Id = db.Column(db.Integer, primary_key=True)
    InterviewTypeId = db.Column(db.Integer, nullable=False)
    Date = db.Column(db.DateTime, nullable=True)
    Time = db.Column(db.Time, nullable=True)
    Venue = db.Column(db.String(500), nullable=True)
    JobApplicationFormId = db.Column(db.Integer, nullable=True)
    InterviewConductorId = db.Column(db.String(300), nullable=True)
    DemoTopic = db.Column(db.String(100), nullable=True)
    Position = db.Column(db.String(250), nullable=True)
    Location = db.Column(db.String(100), nullable=True)
    CreatedBy = db.Column(db.Integer, nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    CampusId = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<InterviewSchedule {self.Id}>'
    
    def to_dict(self):
        return {
            "Id": self.Id,
            "InterviewTypeId": self.InterviewTypeId,
            "Date": self.Date.isoformat() if self.Date else None,
            "Time": self.Time.isoformat() if self.Time else None,
            "Venue": self.Venue,
            "JobApplicationFormId": self.JobApplicationFormId,
            "InterviewConductorId": self.InterviewConductorId,
            "DemoTopic": self.DemoTopic,
            "Position": self.Position,
            "Location": self.Location,
            "CreatedBy": self.CreatedBy,
            "CreateDate": self.CreateDate.isoformat() if self.CreateDate else None,
            "CampusId": self.CampusId
        }

class DeductionHead(db.Model):
    __tablename__ = 'DeductionHead'
    DeductionHead_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DeductionHead_Name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<DeductionHead {self.DeductionHead_Id}>'
    
    def to_dict(self):
        return {
            "DeductionHead_Id": self.DeductionHead_Id,
            "DeductionHead_Name": self.DeductionHead_Name
        }

class OneTimeDeduction(db.Model):
    __tablename__ = 'OneTimeDeduction'
    OneTimeDeduction_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OneTimeDeduction_StaffId = db.Column(db.Integer, nullable=False)
    OneTimeDeduction_DeductionHeadId = db.Column(db.Integer, db.ForeignKey('DeductionHead.DeductionHead_Id'), nullable=False)
    OneTimeDeduction_Amount = db.Column(db.Float, nullable=False)
    OneTimeDeduction_DeductionMonth = db.Column(db.String(15), nullable=False)
    OneTimeDeduction_ApprovedBy = db.Column(db.Integer, nullable=False)
    CreatorId = db.Column(db.Integer, nullable=False)
    CreateDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatorId = db.Column(db.Integer, nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)
    InActive = db.Column(db.Boolean, nullable=False)

    deduction_head = db.relationship('DeductionHead', backref=db.backref('oneTimeDeduction', lazy=True))
    
    def __repr__(self):
        return f'<DeductionHead {self.OneTimeDeduction_Id}>'
    
    def to_dict(self):
        return {
            "OneTimeDeduction_Id": self.OneTimeDeduction_Id,
            "OneTimeDeduction_StaffId": self.OneTimeDeduction_StaffId,
            "OneTimeDeduction_DeductionHeadId": self.OneTimeDeduction_DeductionHeadId,
            "OneTimeDeduction_Amount": self.OneTimeDeduction_Amount,
            "OneTimeDeduction_DeductionMonth": self.OneTimeDeduction_DeductionMonth,
            "OneTimeDeduction_ApprovedBy": self.OneTimeDeduction_ApprovedBy,
            "CreatorId": self.CreatorId,
            "CreateDate": self.CreateDate.isoformat(),
            "UpdatorId": self.UpdatorId,
            "UpdateDate": self.UpdateDate.isoformat() if self.UpdateDate else None,
            "InActive": self.InActive
        }

class ScheduledDeduction(db.Model):
    __tablename__ = 'ScheduledDeduction'
    ScheduledDeduction_Id = db.Column(db.Integer, primary_key=True)
    ScheduledDeduction_StaffId = db.Column(db.Integer, nullable=False)
    ScheduledDeduction_DeductionHeadId = db.Column(db.Integer, db.ForeignKey('DeductionHead.DeductionHead_Id'), nullable=False)
    ScheduledDeduction_AmountPerMonth = db.Column(db.Float, nullable=False)
    ScheduledDeduction_StartDate = db.Column(db.DateTime, nullable=False)
    ScheduledDeduction_EndDate = db.Column(db.DateTime, nullable=False)
    ScheduledDeduction_ApprovedBy = db.Column(db.Integer, nullable=False)
    CreatorId = db.Column(db.Integer, nullable=False)
    CreateDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatorId = db.Column(db.Integer)
    UpdateDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)
    
    deduction_head = db.relationship('DeductionHead', backref=db.backref('scheduledDeduction', lazy=True))
    
    def __repr__(self):
        return f'<ScheduledDeduction_Id {self.ScheduledDeduction_Id}>'
    
    def to_dict(self):
        return {
            "ScheduledDeduction_Id": self.ScheduledDeduction_Id,
            "ScheduledDeduction_StaffId": self.ScheduledDeduction_StaffId,
            "ScheduledDeduction_DeductionHeadId": self.ScheduledDeduction_DeductionHeadId,
            "ScheduledDeduction_AmountPerMonth": self.ScheduledDeduction_AmountPerMonth,
            "ScheduledDeduction_StartDate": self.ScheduledDeduction_StartDate.isoformat(),
            "ScheduledDeduction_EndDate": self.ScheduledDeduction_EndDate.isoformat(),
            "ScheduledDeduction_ApprovedBy": self.ScheduledDeduction_ApprovedBy,
            "CreatorId": self.CreatorId,
            "CreateDate": self.CreateDate.isoformat(),
            "UpdatorId": self.UpdatorId,
            "UpdateDate": self.UpdateDate.isoformat() if self.UpdateDate else None,
            "InActive": self.InActive
        }

class IAR(db.Model):
    __tablename__ = 'IAR'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Form_Id = db.Column(db.Integer, nullable=False)
    IAR_Type_Id = db.Column(db.Integer, db.ForeignKey('IAR_Types.Id'), nullable=False)
    Status_Check = db.Column(db.Boolean, nullable=False)
    Remarks = db.Column(db.String(150), nullable=False)
    CreatorId = db.Column(db.Integer, nullable=True)
    CreatedDate = db.Column(db.DateTime, nullable=True)

    iar_type = db.relationship('IAR_Types', backref=db.backref('iars', lazy=True))

    def to_dict(self):
        return {
            'Id': self.Id,
            'Form_Id': self.Form_Id,
            'IAR_Type_Id': self.IAR_Type_Id,
            'Status_Check': self.Status_Check,
            'Remarks': self.Remarks,
            'CreatorId': self.CreatorId,
            'CreatedDate': self.CreatedDate.isoformat() if self.CreatedDate else None
        }

class IAR_Remarks(db.Model):
    __tablename__ = 'IAR_Remarks'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    IAR_Id = db.Column(db.Integer, db.ForeignKey('IAR.Id'), nullable=False)
    Remarks = db.Column(db.String(150), nullable=True)
    Status = db.Column(db.Boolean, nullable=True)
    CreatorId = db.Column(db.Integer, nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True)

    iar = db.relationship('IAR', backref=db.backref('IAR_Id', lazy=True))

    def to_dict(self):
        return {
            'Id': self.Id,
            'IAR_Id': self.IAR_Id,
            'Remarks': self.Remarks,
            'Status': self.Status,
            'CreatorId': self.CreatorId,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None
        }

class IAR_Types(db.Model):
    __tablename__ = 'IAR_Types'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'Id': self.id,
            'Name': self.name
        }

class EmailTypes(db.Model):
    __tablename__ = 'EmailTypes'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'Id': self.Id,
            'Name': self.Name
        }

class EmailStorageSystem(db.Model):
    __tablename__ = 'EmailStorageSystem'
    Email_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Email_Title = db.Column(db.String(100), nullable=True)
    Email_Subject = db.Column(db.String(250), nullable=True)
    Email_Body = db.Column(db.Text, nullable=True)
    Status = db.Column(db.Boolean, nullable=True)
    CreatorId = db.Column(db.Integer, nullable=True)
    CreatedDate = db.Column(db.DateTime, nullable=True)
    UpdatorId = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True)
    EmailType = db.Column(db.Integer, db.ForeignKey('EmailTypes.Id'), nullable=True)

    email_type = db.relationship('EmailTypes', backref=db.backref('emails', lazy=True))

    def to_dict(self):
        return {
            'Email_Id': self.Email_Id,
            'Email_Title': self.Email_Title,
            'Email_Subject': self.Email_Subject,
            'Email_Body': self.Email_Body,
            'Status': self.Status,
            'CreatorId': self.CreatorId,
            'CreatedDate': self.CreatedDate.isoformat() if self.CreatedDate else None,
            'UpdatorId': self.UpdatorId,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'EmailType': self.EmailType
        }

class AvailableJobs(db.Model):
    __tablename__ = 'AvailableJobs'
    Job_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Job_Title = db.Column(db.String(100), nullable=False)
    Job_Level = db.Column(db.String(100), nullable=False)
    Job_PostedBy = db.Column(db.Integer, nullable=True)
    Job_Status = db.Column(db.Boolean, nullable=True)
    CreatorId = db.Column(db.Integer, nullable=True)
    CreatedDate = db.Column(db.DateTime, nullable=True)
    UpdatorId = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'Job_Id': self.Job_Id,
            'Job_Title': self.Job_Title,
            'Job_Level': self.Job_Level,
            'Job_PostedBy': self.Job_PostedBy,
            'Job_Status': self.Job_Status,
            'CreatorId': self.CreatorId,
            'CreatedDate': self.CreatedDate.isoformat() if self.CreatedDate else None,
            'UpdatorId': self.UpdatorId,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None
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

    def __repr__(self):
        return f'<Id {self.Id}>'
    
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

    def __repr__(self):
        return f'<StaffId {self.StaffId}>'
    
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

class Salaries(db.Model):
    __tablename__ = 'Salaries'
    Id = db.Column(db.Integer, primary_key=True)
    BasicAmount = db.Column(db.Float, nullable=False)
    AllowancesAmount = db.Column(db.Float, nullable=False)
    TotalAmount = db.Column(db.Float, nullable=False)
    AnnualLeaves = db.Column(db.Integer, nullable=False)
    RemainingAnnualLeaves = db.Column(db.Integer, nullable=False)
    DailyHours = db.Column(db.Integer, nullable=False)
    PFAmount = db.Column(db.Float, nullable=False)
    EOBIAmount = db.Column(db.Float, nullable=False)
    SESSIAmount = db.Column(db.Float, nullable=False)
    SalaryMode = db.Column(db.Integer, nullable=False)
    IsProbationPeriod = db.Column(db.Boolean, nullable=False)
    From = db.Column(db.DateTime, nullable=False)
    To = db.Column(db.DateTime, nullable=False)
    EmployeeId = db.Column(db.Integer, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedOn = db.Column(db.DateTime)
    InActiveOn = db.Column(db.DateTime)
    IsActive = db.Column(db.Boolean, nullable=False)
    CreatedByUserId = db.Column(db.Integer, nullable=False)
    UpdatedByUserId = db.Column(db.Integer)
    InActiveByUserId = db.Column(db.Integer)
    HouseRent = db.Column(db.Float)
    MedicalAllowance = db.Column(db.Float)
    UtilityAllowance = db.Column(db.Float)
    IncomeTax = db.Column(db.Float)
    Toil = db.Column(db.Float)
    ConveyanceAllowance = db.Column(db.Float)
    StaffLunch = db.Column(db.Float)
    CasualLeaves = db.Column(db.Integer)
    SickLeaves = db.Column(db.Integer)
    RemainingCasualLeaves = db.Column(db.Integer, nullable=False)
    RemainingSickLeaves = db.Column(db.Integer, nullable=False)
    StudyLeaves = db.Column(db.Integer)
    RemainingStudyLeaves = db.Column(db.Integer, nullable=False)
    Loan = db.Column(db.Integer, nullable=False)
    Arrears = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<id {self.Id}>'
    
    def to_dict(self):
        """
        Serializes the Salaries object to a dictionary.
        """
        return {
            'Id': self.Id,
            'BasicAmount': self.BasicAmount,
            'AllowancesAmount': self.AllowancesAmount,
            'TotalAmount': self.TotalAmount,
            'AnnualLeaves': self.AnnualLeaves,
            'RemainingAnnualLeaves': self.RemainingAnnualLeaves,
            'DailyHours': self.DailyHours,
            'PFAmount': self.PFAmount,
            'EOBIAmount': self.EOBIAmount,
            'SESSIAmount': self.SESSIAmount,
            'SalaryMode': self.SalaryMode,
            'IsProbationPeriod': self.IsProbationPeriod,
            'From': self.From.isoformat() if self.From else None,
            'To': self.To.isoformat() if self.To else None,
            'EmployeeId': self.EmployeeId,
            'CreatedOn': self.CreatedOn.isoformat() if self.CreatedOn else None,
            'UpdatedOn': self.UpdatedOn.isoformat() if self.UpdatedOn else None,
            'InActiveOn': self.InActiveOn.isoformat() if self.InActiveOn else None,
            'IsActive': self.IsActive,
            'CreatedByUserId': self.CreatedByUserId,
            'UpdatedByUserId': self.UpdatedByUserId,
            'InActiveByUserId': self.InActiveByUserId,
            'HouseRent': self.HouseRent,
            'MedicalAllowance': self.MedicalAllowance,
            'UtilityAllowance': self.UtilityAllowance,
            'IncomeTax': self.IncomeTax,
            'Toil': self.Toil,
            'ConveyanceAllowance': self.ConveyanceAllowance,
            'StaffLunch': self.StaffLunch,
            'CasualLeaves': self.CasualLeaves,
            'SickLeaves': self.SickLeaves,
            'RemainingCasualLeaves': self.RemainingCasualLeaves,
            'RemainingSickLeaves': self.RemainingSickLeaves,
            'StudyLeaves': self.StudyLeaves,
            'RemainingStudyLeaves': self.RemainingStudyLeaves,
            'Loan': self.Loan,
            'Arrears': self.Arrears
        }

class MarkDayOffDeps(db.Model):
    __tablename__ = 'MarkDayOffDeps'

    Id = db.Column(db.Integer, primary_key=True)
    Date = db.Column(db.DateTime, nullable=False)
    Staff_Id = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(250))
    CreatorId = db.Column(db.Integer)
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatorId = db.Column(db.Integer)
    UpdateDate = db.Column(db.DateTime)
    status = db.Column(db.Boolean)
    CampusId = db.Column(db.Integer)
    AcademicYearId = db.Column(db.Integer)

    def __repr__(self):
        return f'<id {self.Id}>'
    
    def to_dict(self):
        """
        Serializes the MarkDayOffDeps object to a dictionary.
        """
        return {
            'Id': self.Id,
            'Date': self.Date.isoformat() if self.Date else None,
            'Staff_Id': self.Staff_Id,
            'Description': self.Description,
            'CreatorId': self.CreatorId,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None,
            'UpdatorId': self.UpdatorId,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'status': self.status,
            'CampusId': self.CampusId,
            'AcademicYearId': self.AcademicYearId
        }

class MarkDayOffHRs(db.Model):
    __tablename__ = 'MarkDayOffHRs'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Date = db.Column(db.DateTime, nullable=False)
    CampusIds = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(250))
    CreatorId = db.Column(db.Integer)
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatorId = db.Column(db.Integer)
    UpdateDate = db.Column(db.DateTime)
    Status = db.Column(db.Boolean)
    AcademicYearId = db.Column(db.Integer)

    def __repr__(self):
        return f'<id {self.Id}>'
    
    def to_dict(self):
        return {
            "Id": self.Id,
            "Date": self.Date.isoformat() if self.Date else None,
            "CampusIds": self.CampusIds,
            "Description": self.Description,
            "CreatorId": self.CreatorId,
            "CreateDate": self.CreateDate.isoformat() if self.CreateDate else None,
            "UpdatorId": self.UpdatorId,
            "UpdateDate": self.UpdateDate.isoformat() if self.UpdateDate else None,
            "Status": self.Status,
            "AcademicYearId": self.AcademicYearId
        }

class AllowanceHead(db.Model):
    __tablename__ = 'AllowanceHead'
    AllowanceHead_Id = db.Column(db.Integer, primary_key=True)
    AllowanceHead_Name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "AllowanceHead_Id": self.AllowanceHead_Id,
            "AllowanceHead_Name": self.AllowanceHead_Name
        }

class OneTimeAllowance(db.Model):
    __tablename__ = 'OneTimeAllowance'
    OneTimeAllowance_Id = db.Column(db.Integer, primary_key=True)
    OneTimeAllowance_StaffId = db.Column(db.Integer, nullable=False)
    OneTimeAllowance_AllowanceHeadId = db.Column(db.Integer, db.ForeignKey('AllowanceHead.AllowanceHead_Id'), nullable=True)
    OneTimeAllowance_Amount = db.Column(db.Float, nullable=False)
    OneTimeAllowance_PamentMonth = db.Column(db.String(15), nullable=False)
    OneTimeAllowance_ApprovedBy = db.Column(db.Integer, nullable=False)
    OneTimeAllowance_Taxable = db.Column(db.Boolean, nullable=False)
    CreatorId = db.Column(db.Integer, nullable=False)
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    UpdatorId = db.Column(db.Integer)
    UpdateDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)
    
    oneTimeAllowance_AllowanceHeadId = db.relationship('AllowanceHead', backref=db.backref('allowanceHead_Id', lazy=True))

    def to_dict(self):
        return {
            "OneTimeAllowance_Id": self.OneTimeAllowance_Id,
            "OneTimeAllowance_StaffId": self.OneTimeAllowance_StaffId,
            "OneTimeAllowance_AllowanceHeadId": self.OneTimeAllowance_AllowanceHeadId,
            "OneTimeAllowance_Amount": self.OneTimeAllowance_Amount,
            "OneTimeAllowance_PamentMonth": self.OneTimeAllowance_PamentMonth,
            "OneTimeAllowance_ApprovedBy": self.OneTimeAllowance_ApprovedBy,
            "OneTimeAllowance_Taxable": self.OneTimeAllowance_Taxable,
            "CreatorId": self.CreatorId,
            "CreateDate": self.CreateDate.isoformat() if self.CreateDate else None,
            "UpdatorId": self.UpdatorId,
            "UpdateDate": self.UpdateDate.isoformat() if self.UpdateDate else None,
            "InActive": self.InActive
        }

class ScheduledAllowance(db.Model):
    __tablename__ = 'ScheduledAllowance'
    ScheduledAllowance_Id = db.Column(db.Integer, primary_key=True)
    ScheduledAllowance_StaffId = db.Column(db.Integer, nullable=False)
    ScheduledAllowance_AllowanceHeadId = db.Column(db.Integer, db.ForeignKey('AllowanceHead.AllowanceHead_Id'), nullable=False)
    ScheduledAllowance_AmountPerMonth = db.Column(db.Float, nullable=False)
    ScheduledAllowance_StartDate = db.Column(db.DateTime, nullable=False)
    ScheduledAllowance_EndDate = db.Column(db.DateTime, nullable=False)
    ScheduledAllowance_ApprovedBy = db.Column(db.Integer, nullable=False)
    CreatorId = db.Column(db.Integer, nullable=False)
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    UpdatorId = db.Column(db.Integer)
    UpdateDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)
    ScheduledAllowance_Taxable = db.Column(db.Boolean, nullable=False)
    
    scheduledAllowance_AllowanceHeadId = db.relationship('AllowanceHead', backref=db.backref('scheduledAllowance_allowanceHead_Id', lazy=True))

    def to_dict(self):
        return {
            "ScheduledAllowance_Id": self.ScheduledAllowance_Id,
            "ScheduledAllowance_StaffId": self.ScheduledAllowance_StaffId,
            "ScheduledAllowance_AllowanceHeadId": self.ScheduledAllowance_AllowanceHeadId,
            "ScheduledAllowance_AmountPerMonth": self.ScheduledAllowance_AmountPerMonth,
            "ScheduledAllowance_StartDate": self.ScheduledAllowance_StartDate.isoformat() if self.ScheduledAllowance_StartDate else None,
            "ScheduledAllowance_EndDate": self.ScheduledAllowance_EndDate.isoformat() if self.ScheduledAllowance_EndDate else None,
            "ScheduledAllowance_ApprovedBy": self.ScheduledAllowance_ApprovedBy,
            "CreatorId": self.CreatorId,
            "CreateDate": self.CreateDate.isoformat() if self.CreateDate else None,
            "UpdatorId": self.UpdatorId,
            "UpdateDate": self.UpdateDate.isoformat() if self.UpdateDate else None,
            "InActive": self.InActive,
            "ScheduledAllowance_Taxable": self.ScheduledAllowance_Taxable
        }

class StaffIncrement(db.Model):
    __tablename__ = 'StaffIncrement'
    StaffIncrement_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StaffIncrement_StaffId = db.Column(db.Integer, nullable=False)
    StaffIncrement_CurrentSalary = db.Column(db.Float, nullable=False)
    StaffIncrement_Date = db.Column(db.DateTime, nullable=False)
    StaffIncrement_Reason = db.Column(db.String(20), nullable=False)
    StaffIncrement_Others = db.Column(db.String(200))
    StaffIncrement_NewSalary = db.Column(db.Float, nullable=False)
    StaffIncrement_PercentageIncrease = db.Column(db.Integer, nullable=False)
    StaffIncrement_InitiatedBy = db.Column(db.Integer, nullable=False)
    StaffIncrement_Approval = db.Column(db.Integer, nullable=False)
    StaffIncrement_Remarks = db.Column(db.String(200), nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer)
    UpdatedDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'StaffIncrement_Id': self.StaffIncrement_Id,
            'StaffIncrement_StaffId': self.StaffIncrement_StaffId,
            'StaffIncrement_CurrentSalary': self.StaffIncrement_CurrentSalary,
            'StaffIncrement_Date': self.StaffIncrement_Date.isoformat(),
            'StaffIncrement_Reason': self.StaffIncrement_Reason,
            'StaffIncrement_Others': self.StaffIncrement_Others,
            'StaffIncrement_NewSalary': self.StaffIncrement_NewSalary,
            'StaffIncrement_PercentageIncrease': self.StaffIncrement_PercentageIncrease,
            'StaffIncrement_InitiatedBy': self.StaffIncrement_InitiatedBy,
            'StaffIncrement_Approval': self.StaffIncrement_Approval,
            'StaffIncrement_Remarks': self.StaffIncrement_Remarks,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat(),
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class StaffPromotions(db.Model):
    __tablename__ = 'StaffPromotions'
    StaffPromotion_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StaffPromotion_StaffId = db.Column(db.Integer, nullable=False)
    StaffPromotion_SalaryHold = db.Column(db.Boolean, nullable=False)
    StaffPromotion_NewDesignationId = db.Column(db.Integer, nullable=False)
    StaffPromotion_NewDepartmentId = db.Column(db.Integer, nullable=False)
    StaffPromotion_Date = db.Column(db.DateTime, nullable=False)
    StaffPromotion_Reason = db.Column(db.String(100), nullable=False)
    StaffPromotion_InitiatedBy = db.Column(db.Integer, nullable=False)
    StaffPromotion_ApprovedBy = db.Column(db.Integer, nullable=False)
    StaffPromotion_NewSalary = db.Column(db.Float, nullable=False)
    StaffPromotion_NewSalaryEffectiveDate = db.Column(db.DateTime, nullable=False)
    StaffPromotion_Remarks = db.Column(db.String(200), nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer)
    UpdatedDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'StaffPromotion_Id': self.StaffPromotion_Id,
            'StaffPromotion_StaffId': self.StaffPromotion_StaffId,
            'StaffPromotion_SalaryHold': self.StaffPromotion_SalaryHold,
            'StaffPromotion_NewDesignationId': self.StaffPromotion_NewDesignationId,
            'StaffPromotion_NewDepartmentId': self.StaffPromotion_NewDepartmentId,
            'StaffPromotion_Date': self.StaffPromotion_Date.isoformat() if self.StaffPromotion_Date else None,
            'StaffPromotion_Reason': self.StaffPromotion_Reason,
            'StaffPromotion_InitiatedBy': self.StaffPromotion_InitiatedBy,
            'StaffPromotion_ApprovedBy': self.StaffPromotion_ApprovedBy,
            'StaffPromotion_NewSalary': self.StaffPromotion_NewSalary,
            'StaffPromotion_NewSalaryEffectiveDate': self.StaffPromotion_NewSalaryEffectiveDate.isoformat() if self.StaffPromotion_NewSalaryEffectiveDate else None,
            'StaffPromotion_Remarks': self.StaffPromotion_Remarks,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat() if self.CreatedDate else None,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class StaffSeparation(db.Model):
    __tablename__ = 'StaffSeparation'
    StaffSeparation_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StaffSeparation_StaffId = db.Column(db.Integer, nullable=False)
    StaffSeparation_Type = db.Column(db.String(50), nullable=False)
    StaffSeparation_Reason = db.Column(db.String(20), nullable=False)
    StaffSeparation_Details = db.Column(db.String(200), nullable=False)
    StaffSeparation_ReleventDocumentReceived = db.Column(db.Boolean, nullable=False)
    StaffSeparation_ResignationDate = db.Column(db.DateTime, nullable=False)
    StaffSeparation_LastWorkingDate = db.Column(db.DateTime, nullable=False)
    StaffSeparation_NoticePeriod = db.Column(db.Boolean, nullable=False)
    StaffSeparation_ResignationApproved = db.Column(db.Boolean, nullable=False)
    StaffSeparation_SalaryHoldMonth = db.Column(db.String(20), nullable=False)
    StaffSeparation_ClearanceDone = db.Column(db.Boolean, nullable=False)
    StaffSeparation_ClearanceDate = db.Column(db.DateTime)
    StaffSeparation_ExitInterview = db.Column(db.Boolean, nullable=False)
    StaffSeparation_ExitInterviewDate = db.Column(db.DateTime)
    StaffSeparation_FinalSettlementDone = db.Column(db.Boolean, nullable=False)
    StaffSeparation_FinalSettlementDate = db.Column(db.DateTime)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer)
    UpdatedDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'StaffSeparation_Id': self.StaffSeparation_Id,
            'StaffSeparation_StaffId': self.StaffSeparation_StaffId,
            'StaffSeparation_Type': self.StaffSeparation_Type,
            'StaffSeparation_Reason': self.StaffSeparation_Reason,
            'StaffSeparation_Details': self.StaffSeparation_Details,
            'StaffSeparation_ReleventDocumentReceived': self.StaffSeparation_ReleventDocumentReceived,
            'StaffSeparation_ResignationDate': self.StaffSeparation_ResignationDate.isoformat() if self.StaffSeparation_ResignationDate else None,
            'StaffSeparation_LastWorkingDate': self.StaffSeparation_LastWorkingDate.isoformat() if self.StaffSeparation_LastWorkingDate else None,
            'StaffSeparation_NoticePeriod': self.StaffSeparation_NoticePeriod,
            'StaffSeparation_ResignationApproved': self.StaffSeparation_ResignationApproved,
            'StaffSeparation_SalaryHoldMonth': self.StaffSeparation_SalaryHoldMonth,
            'StaffSeparation_ClearanceDone': self.StaffSeparation_ClearanceDone,
            'StaffSeparation_ClearanceDate': self.StaffSeparation_ClearanceDate.isoformat() if self.StaffSeparation_ClearanceDate else None,
            'StaffSeparation_ExitInterview': self.StaffSeparation_ExitInterview,
            'StaffSeparation_ExitInterviewDate': self.StaffSeparation_ExitInterviewDate.isoformat() if self.StaffSeparation_ExitInterviewDate else None,
            'StaffSeparation_FinalSettlementDone': self.StaffSeparation_FinalSettlementDone,
            'StaffSeparation_FinalSettlementDate': self.StaffSeparation_FinalSettlementDate.isoformat() if self.StaffSeparation_FinalSettlementDate else None,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat() if self.CreatedDate else None,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class SalaryTransferDetails(db.Model):
    __tablename__ = 'SalaryTransferDetails'
    SalaryTransferDetails_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SalaryTransferDetails_StaffId = db.Column(db.Integer, nullable=False)
    SalaryTransferDetails_TransferMethod = db.Column(db.String(20), nullable=False)
    SalaryTransferDetails_BankName = db.Column(db.String(200))
    SalaryTransferDetails_BankAccountNumber = db.Column(db.String(200))
    SalaryTransferDetails_BankBranch = db.Column(db.String(200))
    SalaryTransferDetails_BankOrChequeTitle = db.Column(db.String(200), nullable=False)
    SalaryTransferDetails_ReasonForChequeIssuance = db.Column(db.String(200))
    SalaryTransferDetails_EffectiveDate = db.Column(db.DateTime, nullable=False)
    SalaryTransferDetails_Remarks = db.Column(db.String(200), nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer)
    UpdatedDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'SalaryTransferDetails_Id': self.SalaryTransferDetails_Id,
            'SalaryTransferDetails_StaffId': self.SalaryTransferDetails_StaffId,
            'SalaryTransferDetails_TransferMethod': self.SalaryTransferDetails_TransferMethod,
            'SalaryTransferDetails_BankName': self.SalaryTransferDetails_BankName,
            'SalaryTransferDetails_BankAccountNumber': self.SalaryTransferDetails_BankAccountNumber,
            'SalaryTransferDetails_BankBranch': self.SalaryTransferDetails_BankBranch,
            'SalaryTransferDetails_BankOrChequeTitle': self.SalaryTransferDetails_BankOrChequeTitle,
            'SalaryTransferDetails_ReasonForChequeIssuance': self.SalaryTransferDetails_ReasonForChequeIssuance,
            'SalaryTransferDetails_EffectiveDate': self.SalaryTransferDetails_EffectiveDate.isoformat() if self.SalaryTransferDetails_EffectiveDate else None,
            'SalaryTransferDetails_Remarks': self.SalaryTransferDetails_Remarks,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat() if self.CreatedDate else None,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class PayrollClose(db.Model):
    __tablename__ = 'PayrollClose'
    PayrollClose_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PayrollClose_StaffId = db.Column(db.Integer, nullable=False)
    PayrollClose_Period = db.Column(db.String(100), nullable=False)
    PayrollClose_CloseDate = db.Column(db.DateTime, nullable=False)
    PayrollClose_ProcessedBy = db.Column(db.Integer, nullable=False)
    PayrollClose_ReceivedBy = db.Column(db.Integer, nullable=False)
    PayrollClose_ApprovedBy = db.Column(db.Integer, nullable=False)
    PayrollClose_Remarks = db.Column(db.String(200), nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer)
    UpdatedDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'PayrollClose_Id': self.PayrollClose_Id,
            'PayrollClose_StaffId': self.PayrollClose_StaffId,
            'PayrollClose_Period': self.PayrollClose_Period,
            'PayrollClose_CloseDate': self.PayrollClose_CloseDate.isoformat() if self.PayrollClose_CloseDate else None,
            'PayrollClose_ProcessedBy': self.PayrollClose_ProcessedBy,
            'PayrollClose_ReceivedBy': self.PayrollClose_ReceivedBy,
            'PayrollClose_ApprovedBy': self.PayrollClose_ApprovedBy,
            'PayrollClose_Remarks': self.PayrollClose_Remarks,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat() if self.CreatedDate else None,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class SchoolDetails(db.Model):
    __tablename__ = 'SchoolDetails'
    id = db.Column(db.Integer, primary_key=True)
    SchoolName = db.Column(db.String(100))
    SchoolRegirtrationNo = db.Column(db.String(50))
    SchoolNTN = db.Column(db.String(50))
    Description = db.Column(db.String(250))
    PhoneNo = db.Column(db.String(50))
    MobileNo = db.Column(db.String(50))
    Address = db.Column(db.String(500))
    SchoolLogo = db.Column(db.String(50))
    MiniLogo = db.Column(db.String(50))
    ReportLogo = db.Column(db.String(50))
    IsSaturdayOff = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    FridayStaffTimeOut = db.Column(db.DateTime)
    FridayStaffTimeIn = db.Column(db.DateTime)
    FridayStudentTimeOut = db.Column(db.DateTime)
    FridayStudentTimeIn = db.Column(db.DateTime)
    NormalStaffTimeOut = db.Column(db.DateTime)
    NormalStaffTimeIn = db.Column(db.DateTime)
    NormalStudentTimeOut = db.Column(db.DateTime)
    NormalStudentTimeIn = db.Column(db.DateTime)
    NetVerification = db.Column(db.String(100))
    BaseURL = db.Column(db.String(250))
    LoginDetailSendThrough = db.Column(db.String(5))
    LoginDetailTempleteSMS = db.Column(db.String(130))
    LoginDetailTempleteEmail = db.Column(db.Text)
    ReSendPasswordThrough = db.Column(db.String(5))
    ReSendPasswordTemplateSMS = db.Column(db.String(130))
    ReSendPasswordTemplateEmail = db.Column(db.Text)
    NotificationsSendThrough = db.Column(db.String(5))
    NotificationTemplateEmail = db.Column(db.Text)
    Email = db.Column(db.String(250))
    Password = db.Column(db.String(250))
    SmtpPort = db.Column(db.Integer)
    SmtpHost = db.Column(db.String(250))
    UpdaterId = db.Column(db.BigInteger)
    UpdaterIP = db.Column(db.String(20))
    UpdaterTerminal = db.Column(db.String(255))
    UpdateDate = db.Column(db.DateTime)
    CreatorId = db.Column(db.BigInteger)
    CreatorIP = db.Column(db.String(20))
    CreatorTerminal = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime)
    CampusId = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'SchoolName': self.SchoolName,
            'SchoolRegirtrationNo': self.SchoolRegirtrationNo,
            'SchoolNTN': self.SchoolNTN,
            'Description': self.Description,
            'PhoneNo': self.PhoneNo,
            'MobileNo': self.MobileNo,
            'Address': self.Address,
            'SchoolLogo': self.SchoolLogo,
            'MiniLogo': self.MiniLogo,
            'ReportLogo': self.ReportLogo,
            'IsSaturdayOff': self.IsSaturdayOff,
            'status': self.status,
            'FridayStaffTimeOut': self.FridayStaffTimeOut,
            'FridayStaffTimeIn': self.FridayStaffTimeIn,
            'FridayStudentTimeOut': self.FridayStudentTimeOut,
            'FridayStudentTimeIn': self.FridayStudentTimeIn,
            'NormalStaffTimeOut': self.NormalStaffTimeOut,
            'NormalStaffTimeIn': self.NormalStaffTimeIn,
            'NormalStudentTimeOut': self.NormalStudentTimeOut,
            'NormalStudentTimeIn': self.NormalStudentTimeIn,
            'NetVerification': self.NetVerification,
            'BaseURL': self.BaseURL,
            'LoginDetailSendThrough': self.LoginDetailSendThrough,
            'LoginDetailTempleteSMS': self.LoginDetailTempleteSMS,
            'LoginDetailTempleteEmail': self.LoginDetailTempleteEmail,
            'ReSendPasswordThrough': self.ReSendPasswordThrough,
            'ReSendPasswordTemplateSMS': self.ReSendPasswordTemplateSMS,
            'ReSendPasswordTemplateEmail': self.ReSendPasswordTemplateEmail,
            'NotificationsSendThrough': self.NotificationsSendThrough,
            'NotificationTemplateEmail': self.NotificationTemplateEmail,
            'Email': self.Email,
            'Password': self.Password,
            'SmtpPort': self.SmtpPort,
            'SmtpHost': self.SmtpHost,
            'UpdaterId': self.UpdaterId,
            'UpdaterIP': self.UpdaterIP,
            'UpdaterTerminal': self.UpdaterTerminal,
            'UpdateDate': self.UpdateDate,
            'CreatorId': self.CreatorId,
            'CreatorIP': self.CreatorIP,
            'CreatorTerminal': self.CreatorTerminal,
            'CreateDate': self.CreateDate,
            'CampusId': self.CampusId
        }

class StudentInfo(db.Model):
    __tablename__ = 'StudentInfo'
    Student_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Registration_ID = db.Column(db.Integer)
    Stu_AdmissionNo = db.Column(db.String(50), nullable=False)
    Stu_Name = db.Column(db.String(50), nullable=False)
    Stu_FName = db.Column(db.String(50), nullable=False)
    Stu_FCNIC = db.Column(db.String(20))
    Stu_AdmissionDate = db.Column(db.DateTime, nullable=False)
    Stu_Gender = db.Column(db.Integer, nullable=False)
    Stu_DoB = db.Column(db.DateTime, nullable=False)
    Stu_DoBWords = db.Column(db.String(50))
    Stu_BirthPlace = db.Column(db.String(50))
    Stu_GRNo = db.Column(db.Integer)
    Stu_ClassId = db.Column(db.Integer)
    Stu_Religion = db.Column(db.String(50))
    Stu_Cast = db.Column(db.String(50))
    Stu_Tribe = db.Column(db.String(50))
    Stu_FatherGuardianName = db.Column(db.String(50))
    Stu_FGCNIC = db.Column(db.String(20))
    Stu_ParentEmail = db.Column(db.String(250))
    Stu_FGOccupation = db.Column(db.String(50))
    Stu_Relation = db.Column(db.String(50))
    Stu_PreSchool = db.Column(db.String(100))
    Stu_PerAddress = db.Column(db.String(500), nullable=False)
    Stu_TempAddress = db.Column(db.String(500))
    Stu_Mobile = db.Column(db.String(20))
    Stu_OfficeNo = db.Column(db.String(20))
    Stu_ResidentNo = db.Column(db.String(20))
    Stud_Active = db.Column(db.Boolean, nullable=False)
    IsSpecialDiscount = db.Column(db.Boolean, nullable=False)
    SpecialDiscountAmount = db.Column(db.Float)
    IsSiblingDiscount = db.Column(db.Boolean, nullable=False)
    SiblingDiscountPercentage = db.Column(db.Integer, nullable=False)
    AcademicYear = db.Column(db.Integer, nullable=False)
    IsPassed = db.Column(db.Boolean, nullable=False)
    IsLeave = db.Column(db.Boolean, nullable=False)
    Stu_EnrollmentNo = db.Column(db.String(50))
    Stu_RollNo = db.Column(db.String(50))
    LeavingReasons = db.Column(db.String(255))
    LeavingRemarks = db.Column(db.String(255))
    UpdaterId = db.Column(db.BigInteger)
    UpdaterIP = db.Column(db.String(20))
    UpdaterTerminal = db.Column(db.String(255))
    UpdateDate = db.Column(db.DateTime)
    CreatorId = db.Column(db.BigInteger)
    CreatorIP = db.Column(db.String(20))
    CreatorTerminal = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime)
    IsDisable = db.Column(db.Boolean)
    disableDetail = db.Column(db.String(255))
    PhotoPath = db.Column(db.String(500))
    CampusId = db.Column(db.Integer)
    SpecialDiscountPercentage = db.Column(db.Float)
    FinancialAssistanceId = db.Column(db.Integer)
    Area = db.Column(db.String(300))
    TelePhoneNo1 = db.Column(db.String(20))
    TelePhoneNo2 = db.Column(db.String(20))
    SMSServiceNo = db.Column(db.String(20))
    Organization = db.Column(db.String(150))
    OrganizationAddress = db.Column(db.String(250))
    CompanyNo = db.Column(db.String(20))
    MotherName = db.Column(db.String(150))
    MotherCnic = db.Column(db.String(20))
    MotherProfession = db.Column(db.String(100))
    MotherOrganization = db.Column(db.String(100))
    EmergencyContactNo = db.Column(db.String(200))
    EmerContactPerson = db.Column(db.String(100))
    Allergies = db.Column(db.String(200))
    Food = db.Column(db.String(200))
    Medical = db.Column(db.String(100))
    BloodGroupId = db.Column(db.Integer)
    ConveyenceType = db.Column(db.String(50))
    VanDriverName = db.Column(db.String(100))
    VanNumber = db.Column(db.String(100))
    VanDriverContactNo = db.Column(db.String(100))
    LeavingDate = db.Column(db.DateTime)
    LeavingConduct = db.Column(db.String(1000))
    LeavingAcademicRecord = db.Column(db.String(1000))
    WhatsApp = db.Column(db.String(20))
    FatherCellNo = db.Column(db.String(20))
    MotherCellNo = db.Column(db.String(20))
    MotherOrganizationAddress = db.Column(db.String(500))
    MotherOrganizationNo = db.Column(db.String(20))
    Stu_AdmissionClassId = db.Column(db.Integer)
    HouseNo = db.Column(db.String(255))
    Street_Sector_BlockNo = db.Column(db.String(255))
    AreaId = db.Column(db.BigInteger)
    CityId = db.Column(db.BigInteger)
    District = db.Column(db.String(50))
    CountryId = db.Column(db.BigInteger)
    Province = db.Column(db.String(50))
    GroupId = db.Column(db.Integer)
    BarcodeId = db.Column(db.String(50))
    AcademicStatus = db.Column(db.Integer)
    EduEmail = db.Column(db.String(100))
    EduPassword = db.Column(db.String(100))
    HouseId = db.Column(db.Integer, nullable=False)
    AlphaId = db.Column(db.Text)
    BFormId = db.Column(db.String(20))
    GuardianName = db.Column(db.String(100))
    GuardianCNIC = db.Column(db.String(20))
    GuardianOccupation = db.Column(db.String(100))
    GuardianOrganization = db.Column(db.String(250))
    GuardianOrganizationAddress = db.Column(db.String(250))
    GuardianOrganizationNo = db.Column(db.String(20))
    GuardianCellNo = db.Column(db.String(20))
    CounselorId = db.Column(db.Integer)
    StuPersonalEmail = db.Column(db.String(100))
    Stu_FatherEmail = db.Column(db.String(100))
    Stu_MotherEmail = db.Column(db.String(100))
    Stu_FileNo = db.Column(db.String(50))
    ToPromote = db.Column(db.String(1))
    UserId = db.Column(db.Integer)
    ParentUserId = db.Column(db.Integer)
    Student_IdNew = db.Column(db.Integer)

    def to_dict(self):
        return {
            "Student_ID": self.Student_ID,
            "Registration_ID": self.Registration_ID,
            "Stu_AdmissionNo": self.Stu_AdmissionNo,
            "Stu_Name": self.Stu_Name,
            "Stu_FName": self.Stu_FName,
            "Stu_FCNIC": self.Stu_FCNIC,
            "Stu_AdmissionDate": self.Stu_AdmissionDate,
            "Stu_Gender": self.Stu_Gender,
            "Stu_DoB": self.Stu_DoB,
            "Stu_DoBWords": self.Stu_DoBWords,
            "Stu_BirthPlace": self.Stu_BirthPlace,
            "Stu_GRNo": self.Stu_GRNo,
            "Stu_ClassId": self.Stu_ClassId,
            "Stu_Religion": self.Stu_Religion,
            "Stu_Cast": self.Stu_Cast,
            "Stu_Tribe": self.Stu_Tribe,
            "Stu_FatherGuardianName": self.Stu_FatherGuardianName,
            "Stu_FGCNIC": self.Stu_FGCNIC,
            "Stu_ParentEmail": self.Stu_ParentEmail,
            "Stu_FGOccupation": self.Stu_FGOccupation,
            "Stu_Relation": self.Stu_Relation,
            "Stu_PreSchool": self.Stu_PreSchool,
            "Stu_PerAddress": self.Stu_PerAddress,
            "Stu_TempAddress": self.Stu_TempAddress,
            "Stu_Mobile": self.Stu_Mobile,
            "Stu_OfficeNo": self.Stu_OfficeNo,
            "Stu_ResidentNo": self.Stu_ResidentNo,
            "Stud_Active": self.Stud_Active,
            "IsSpecialDiscount": self.IsSpecialDiscount,
            "SpecialDiscountAmount": self.SpecialDiscountAmount,
            "IsSiblingDiscount": self.IsSiblingDiscount,
            "SiblingDiscountPercentage": self.SiblingDiscountPercentage,
            "AcademicYear": self.AcademicYear,
            "IsPassed": self.IsPassed,
            "IsLeave": self.IsLeave,
            "Stu_EnrollmentNo": self.Stu_EnrollmentNo,
            "Stu_RollNo": self.Stu_RollNo,
            "LeavingReasons": self.LeavingReasons,
            "LeavingRemarks": self.LeavingRemarks,
            "UpdaterId": self.UpdaterId,
            "UpdaterIP": self.UpdaterIP,
            "UpdaterTerminal": self.UpdaterTerminal,
            "UpdateDate": self.UpdateDate,
            "CreatorId": self.CreatorId,
            "CreatorIP": self.CreatorIP,
            "CreatorTerminal": self.CreatorTerminal,
            "CreateDate": self.CreateDate,
            "IsDisable": self.IsDisable,
            "disableDetail": self.disableDetail,
            "PhotoPath": self.PhotoPath,
            "CampusId": self.CampusId,
            "SpecialDiscountPercentage": self.SpecialDiscountPercentage,
            "FinancialAssistanceId": self.FinancialAssistanceId,
            "Area": self.Area,
            "TelePhoneNo1": self.TelePhoneNo1,
            "TelePhoneNo2": self.TelePhoneNo2,
            "SMSServiceNo": self.SMSServiceNo,
            "Organization": self.Organization,
            "OrganizationAddress": self.OrganizationAddress,
            "CompanyNo": self.CompanyNo,
            "MotherName": self.MotherName,
            "MotherCnic": self.MotherCnic,
            "MotherProfession": self.MotherProfession,
            "MotherOrganization": self.MotherOrganization,
            "EmergencyContactNo": self.EmergencyContactNo,
            "EmerContactPerson": self.EmerContactPerson,
            "Allergies": self.Allergies,
            "Food": self.Food,
            "Medical": self.Medical,
            "BloodGroupId": self.BloodGroupId,
            "ConveyenceType": self.ConveyenceType,
            "VanDriverName": self.VanDriverName,
            "VanNumber": self.VanNumber,
            "VanDriverContactNo": self.VanDriverContactNo,
            "LeavingDate": self.LeavingDate,
            "LeavingConduct": self.LeavingConduct,
            "LeavingAcademicRecord": self.LeavingAcademicRecord,
            "WhatsApp": self.WhatsApp,
            "FatherCellNo": self.FatherCellNo,
            "MotherCellNo": self.MotherCellNo,
            "MotherOrganizationAddress": self.MotherOrganizationAddress,
            "MotherOrganizationNo": self.MotherOrganizationNo,
            "Stu_AdmissionClassId": self.Stu_AdmissionClassId,
            "HouseNo": self.HouseNo,
            "Street_Sector_BlockNo": self.Street_Sector_BlockNo,
            "AreaId": self.AreaId,
            "CityId": self.CityId,
            "District": self.District,
            "CountryId": self.CountryId,
            "Province": self.Province,
            "GroupId": self.GroupId,
            "BarcodeId": self.BarcodeId,
            "AcademicStatus": self.AcademicStatus,
            "EduEmail": self.EduEmail,
            "EduPassword": self.EduPassword,
            "HouseId": self.HouseId,
            "AlphaId": self.AlphaId,
            "BFormId": self.BFormId,
            "GuardianName": self.GuardianName,
            "GuardianCNIC": self.GuardianCNIC,
            "GuardianOccupation": self.GuardianOccupation,
            "GuardianOrganization": self.GuardianOrganization,
            "GuardianOrganizationAddress": self.GuardianOrganizationAddress,
            "GuardianOrganizationNo": self.GuardianOrganizationNo,
            "GuardianCellNo": self.GuardianCellNo,
            "CounselorId": self.CounselorId,
            "StuPersonalEmail": self.StuPersonalEmail,
            "Stu_FatherEmail": self.Stu_FatherEmail,
            "Stu_MotherEmail": self.Stu_MotherEmail,
            "Stu_FileNo": self.Stu_FileNo,
            "ToPromote": self.ToPromote,
            "UserId": self.UserId,
            "ParentUserId": self.ParentUserId,
            "Student_IdNew": self.Student_IdNew
        }

class AcademicYear(db.Model):
    __tablename__ = 'AcademicYear'
    academic_year_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    academic_year = db.Column(db.String(10))
    status = db.Column(db.Boolean, nullable=False)
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    IsActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            "academic_year_Id": self.academic_year_Id,
            "academic_year": self.academic_year,
            "status": self.status,
            "startDate": self.startDate.isoformat() if self.startDate else None,
            "endDate": self.endDate.isoformat() if self.endDate else None,
            "IsActive": self.IsActive
        }

class EduGroupStudent(db.Model):
    __tablename__ = 'EduGroupStudent'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    GroupID = db.Column(db.Integer, nullable=False)
    StudentID = db.Column(db.Integer, nullable=False)
    CampusId = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "Id": self.Id,
            "GroupID": self.GroupID,
            "StudentID": self.StudentID,
            "CampusId": self.CampusId
        }



















