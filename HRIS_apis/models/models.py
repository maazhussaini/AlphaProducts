from app import db
from datetime import datetime
import re
from exceptions import ValidationError
import json
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
    UserTypeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserTypeName = db.Column(db.String(50), nullable=False)
    Priority = db.Column(db.Integer, nullable=False)
    UpdaterId = db.Column(db.BigInteger)
    UpdaterIP = db.Column(db.String(20))
    UpdaterTerminal = db.Column(db.String(255))
    UpdateDate = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    CreatorId = db.Column(db.BigInteger)
    CreatorIP = db.Column(db.String(20))
    CreatorTerminal = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow)
    CampusId = db.Column(db.Integer, db.ForeignKey('UserCampus.Id'))

    # campus = db.relationship('UserCampus', back_populates='user_types')

    def __repr__(self):
        return f"<UserType {self.userTypeName}>"

class UserCampus(db.Model):
    __tablename__ = 'UserCampus'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserId = db.Column(db.Integer, db.ForeignKey('USERS.User_Id'))
    CampusId = db.Column(db.Integer, nullable=True)
    StaffId = db.Column(db.Integer, nullable=True)
    Date = db.Column(db.DateTime, nullable=True)
    UpdaterId = db.Column(db.BigInteger, nullable=True)
    UpdaterIP = db.Column(db.String(20), nullable=True)
    UpdaterTerminal = db.Column(db.String(255), nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)
    CreatorId = db.Column(db.BigInteger, nullable=True)
    CreatorIP = db.Column(db.String(20), nullable=True)
    CreatorTerminal = db.Column(db.String(255), nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True)
    Status = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return {"Campus": self.CampusId}
    
    def to_dict(self):
        return {
            "Id": self.Id,
            "UserId": self.UserId,
            "CampusId": self.CampusId,
            "StaffId": self.StaffId,
            "Date": self.Date.isoformat() if self.Date else None,
            "UpdaterId": self.UpdaterId,
            "UpdaterIP": self.UpdaterIP,
            "UpdaterTerminal": self.UpdaterTerminal,
            "UpdateDate": self.UpdateDate,
            "CreatorId": self.CreatorId,
            "CreatorIP": self.CreatorIP,
            "CreatorTerminal": self.CreatorTerminal,
            "CreateDate": self.CreateDate.isoformat() if self.CreateDate else None,
            "Status": self.Status
        }

class country(db.Model):
    __tablename__ = 'country'

    country_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    country_code = db.Column(db.String(3), nullable=True)
    country = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Country Id={self.country_id}, Code={self.country_code}, Name={self.country}>"

    def to_dict(self):
        return {
            'country_id': self.country_id,
            'country_code': self.country_code,
            'country': self.country
        }

class cities(db.Model):
    __tablename__ = 'cities'

    cityId = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    city = db.Column(db.String(100), nullable=True)
    country_id = db.Column(db.BigInteger, db.ForeignKey('country.country_id'), nullable=True)

    def __repr__(self):
        return f"<City Id={self.cityId}, Name={self.city}, CountryId={self.country_id}>"

    def to_dict(self):
        return {
            'cityId': self.cityId,
            'city': self.city,
            'country_id': self.country_id
        }

class Role(db.Model):
    __tablename__ = 'ROLES'

    Role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    RoleName = db.Column(db.String(150), nullable=False)
    RoleDescription = db.Column(db.String(250), nullable=True)
    IsSysAdmin = db.Column(db.Boolean, nullable=False)
    LastModified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    Status = db.Column(db.Boolean, nullable=False)
    StatisticWidget = db.Column(db.Boolean, nullable=True)
    StudentInfoWidget = db.Column(db.Boolean, nullable=True)
    StudentProgressWidget = db.Column(db.Boolean, nullable=True)
    StudentFeeWidget = db.Column(db.Boolean, nullable=True)
    RecentActivityWidget = db.Column(db.Boolean, nullable=True)
    CalenderWidget = db.Column(db.Boolean, nullable=True)
    StudentAttendanceWidget = db.Column(db.Boolean, nullable=True)
    FinanceWidget = db.Column(db.Boolean, nullable=True)
    BestStudentWidget = db.Column(db.Boolean, nullable=True)
    BestTeacherWidget = db.Column(db.Boolean, nullable=True)
    ToDoListWidget = db.Column(db.Boolean, nullable=True)
    UpdaterId = db.Column(db.BigInteger, nullable=True)
    UpdaterIP = db.Column(db.String(20), nullable=True)
    UpdaterTerminal = db.Column(db.String(255), nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    CreatorId = db.Column(db.BigInteger, nullable=True)
    CreatorIP = db.Column(db.String(20), nullable=True)
    CreatorTerminal = db.Column(db.String(255), nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    ProbationPeriodWidget = db.Column(db.Boolean, nullable=True)
    CampusId = db.Column(db.Integer, db.ForeignKey('UserCampus.Id'), nullable=True)
    RoomBunkAndAbsent = db.Column(db.Boolean, nullable=True)
    BooksDueWidget = db.Column(db.Boolean, nullable=True)

    # campus = db.relationship('UserCampus', back_populates='roles')
    
    def __repr__(self):
        return f'<Role {self.roleName}>'

    def to_dict(self):
        return {
            "Role_id": self.Role_id,
            "RoleName": self.RoleName,
            "RoleDescription": self.RoleDescription,
            "IsSysAdmin": self.IsSysAdmin,
            "LastModified": self.LastModified,
            "Status": self.Status,
            "StatisticWidget": self.StatisticWidget,
            "StudentInfoWidget": self.StudentInfoWidget,
            "StudentProgressWidget": self.StudentProgressWidget,
            "StudentFeeWidget": self.StudentFeeWidget,
            "RecentActivityWidget": self.RecentActivityWidget,
            "CalenderWidget": self.CalenderWidget,
            "StudentAttendanceWidget": self.StudentAttendanceWidget,
            "FinanceWidget": self.FinanceWidget,
            "BestStudentWidget": self.BestStudentWidget,
            "BestTeacherWidget": self.BestTeacherWidget,
            "ToDoListWidget": self.ToDoListWidget,
            "UpdaterId": self.UpdaterId,
            "UpdaterIP": self.UpdaterIP,
            "UpdaterTerminal": self.UpdaterTerminal,
            "UpdateDate": self.UpdateDate,
            "CreatorId": self.CreatorId,
            "CreatorIP": self.CreatorIP,
            "CreatorTerminal": self.CreatorTerminal,
            "CreateDate": self.CreateDate,
            "ProbationPeriodWidget": self.ProbationPeriodWidget,
            "CampusId": self.CampusId,
            "RoomBunkAndAbsent": self.RoomBunkAndAbsent,
            "BooksDueWidget": self.BooksDueWidget
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
    FormId = db.Column(db.Integer, db.ForeignKey('Forms.FormId'), nullable=False)
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
    FormDetailId = db.Column(db.BigInteger, db.ForeignKey('FormDetails.Id'))
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
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'CreatorId': self.CreatorId,
            'CreatorIP': self.CreatorIP,
            'CreatorTerminal': self.CreatorTerminal,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None,
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
            "UpdateDate": self.UpdateDate.isoformat() if self.UpdateDate else None,
            "CreatorId": self.CreatorId,
            "CreatorIP": self.CreatorIP,
            "CreatorTerminal": self.CreatorTerminal,
            "CreateDate": self.CreateDate.isoformat() if self.CreateDate else None,
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

# --------------------------------------------------------------

class JobApplicationForms(db.Model):
    __tablename__ = 'JobApplicationForms'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Initial_ID = db.Column(db.String(250), nullable=True)
    First_Name = db.Column(db.String(250), nullable=False)
    Last_Name = db.Column(db.String(250), nullable=False)
    Father_Name = db.Column(db.String(250), nullable=False)
    CNIC = db.Column(db.String(250), nullable=True)
    Passport_Number = db.Column(db.String(250), nullable=True)
    DOB = db.Column(db.DateTime, nullable=True)
    Age = db.Column(db.String(100), nullable=True)
    Gender = db.Column(db.String(250), nullable=True)
    Cell_Phone = db.Column(db.String(250), nullable=True)
    Alternate_Number = db.Column(db.String(250), nullable=True)
    Email = db.Column(db.String(250), nullable=True)
    Residence = db.Column(db.String(500), nullable=True)
    Education_Level = db.Column(db.String(250), nullable=True)
    Education_Level_Others = db.Column(db.String(250), nullable=True)
    Degree = db.Column(db.String(250), nullable=True)
    Specialization = db.Column(db.String(250), nullable=True)
    Institute = db.Column(db.String(250), nullable=True)
    Fresh = db.Column(db.Boolean, nullable=True)
    Experienced = db.Column(db.Boolean, nullable=True)
    Total_Years_of_Experience = db.Column(db.String(250), nullable=True)
    Name_of_Last_Employer = db.Column(db.String(250), nullable=True)
    Employment_duration_from = db.Column(db.DateTime, nullable=True)
    Employment_duration_to = db.Column(db.DateTime, nullable=True)
    Designation = db.Column(db.String(250), nullable=True)
    Reason_for_leaving = db.Column(db.String(250), nullable=True)
    Last_drawn_gross_salary = db.Column(db.String(250), nullable=True)
    Benefits_if_any = db.Column(db.String(250), nullable=True)
    Preferred_campus = db.Column(db.String(250), nullable=True)
    Preferred_location = db.Column(db.String(250), nullable=True)
    Preferred_job_type = db.Column(db.String(250), nullable=True)
    Section = db.Column(db.String(250), nullable=True)
    Subject = db.Column(db.String(250), nullable=True)
    Expected_salary = db.Column(db.String(250), nullable=True)
    CV_Path = db.Column(db.String(250), nullable=True)
    CoverLetter_Path = db.Column(db.String(250), nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    Status = db.Column(db.Boolean, nullable=True)
    JobApplied_For = db.Column(db.String(250), nullable=True)

    def __repr__(self):
        return f"<JobApplicationForm Id={self.Id}, First_Name={self.First_Name}, Last_Name={self.Last_Name}>"

    def to_dict(self):
        return {
            'Id': self.Id,
            'Initial_ID': self.Initial_ID,
            'First_Name': self.First_Name,
            'Last_Name': self.Last_Name,
            'Father_Name': self.Father_Name,
            'CNIC': self.CNIC,
            'Passport_Number': self.Passport_Number,
            'DOB': self.DOB,
            'Age': self.Age,
            'Gender': self.Gender,
            'Cell_Phone': self.Cell_Phone,
            'Alternate_Number': self.Alternate_Number,
            'Email': self.Email,
            'Residence': self.Residence,
            'Education_Level': self.Education_Level,
            'Education_Level_Others': self.Education_Level_Others,
            'Degree': self.Degree,
            'Specialization': self.Specialization,
            'Institute': self.Institute,
            'Fresh': self.Fresh,
            'Experienced': self.Experienced,
            'Total_Years_of_Experience': self.Total_Years_of_Experience,
            'Name_of_Last_Employer': self.Name_of_Last_Employer,
            'Employment_duration_from': self.Employment_duration_from,
            'Employment_duration_to': self.Employment_duration_to,
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
            'CV_Path': self.CV_Path,
            'CoverLetter_Path': self.CoverLetter_Path,
            'CreateDate': self.CreateDate,
            'Status': self.Status,
            'JobApplied_For': self.JobApplied_For
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
        return f'InterviewSchedule {self.Id}'
    
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

class InterviewEvaluation(db.Model):
    __tablename__ = 'InterviewEvaluation'

    InterviewEvaluation_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    InterviewEvaluation_ConsideredPosition = db.Column(db.String(100), nullable=False)
    InterviewEvaluation_InterviewerId = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_JobApplicationFormId = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_WorkExperience = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_EducationTrainingProfQualifications = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_TechnicalCompetence = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_AppearanceMannerPersonality = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_SupervisoryLeadershipQualificationPotential = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_AttitudeStabilityMaturity = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_InterPersonalCommunicationSkills = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_AmbitionAndMotivation = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_ProblemSolvingSkillsAndAbility = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_OverAllRating = db.Column(db.Integer, nullable=False)
    InterviewEvaluation_Hire = db.Column(db.Boolean, nullable=False)
    InterviewEvaluation_NotHire = db.Column(db.Boolean, nullable=False)
    InterviewEvaluation_FurtherInterview = db.Column(db.Boolean, nullable=False)
    InterviewEvaluation_Shortlisted = db.Column(db.Boolean, nullable=False)
    InterviewEvaluation_Other = db.Column(db.Boolean, nullable=False)
    InterviewEvaluation_Comments = db.Column(db.String(500), nullable=False)
    InterviewEvaluation_FilePath = db.Column(db.String(200), nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer)
    UpdatedDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'InterviewEvaluation_Id': self.InterviewEvaluation_Id,
            'InterviewEvaluation_ConsideredPosition': self.InterviewEvaluation_ConsideredPosition,
            'InterviewEvaluation_InterviewerId': self.InterviewEvaluation_InterviewerId,
            'InterviewEvaluation_JobApplicationFormId': self.InterviewEvaluation_JobApplicationFormId,
            'InterviewEvaluation_WorkExperience': self.InterviewEvaluation_WorkExperience,
            'InterviewEvaluation_EducationTrainingProfQualifications': self.InterviewEvaluation_EducationTrainingProfQualifications,
            'InterviewEvaluation_TechnicalCompetence': self.InterviewEvaluation_TechnicalCompetence,
            'InterviewEvaluation_AppearanceMannerPersonality': self.InterviewEvaluation_AppearanceMannerPersonality,
            'InterviewEvaluation_SupervisoryLeadershipQualificationPotential': self.InterviewEvaluation_SupervisoryLeadershipQualificationPotential,
            'InterviewEvaluation_AttitudeStabilityMaturity': self.InterviewEvaluation_AttitudeStabilityMaturity,
            'InterviewEvaluation_InterPersonalCommunicationSkills': self.InterviewEvaluation_InterPersonalCommunicationSkills,
            'InterviewEvaluation_AmbitionAndMotivation': self.InterviewEvaluation_AmbitionAndMotivation,
            'InterviewEvaluation_ProblemSolvingSkillsAndAbility': self.InterviewEvaluation_ProblemSolvingSkillsAndAbility,
            'InterviewEvaluation_OverAllRating': self.InterviewEvaluation_OverAllRating,
            'InterviewEvaluation_Hire': self.InterviewEvaluation_Hire,
            'InterviewEvaluation_NotHire': self.InterviewEvaluation_NotHire,
            'InterviewEvaluation_FurtherInterview': self.InterviewEvaluation_FurtherInterview,
            'InterviewEvaluation_Shortlisted': self.InterviewEvaluation_Shortlisted,
            'InterviewEvaluation_Other': self.InterviewEvaluation_Other,
            'InterviewEvaluation_Comments': self.InterviewEvaluation_Comments,
            "InterviewEvaluation_FilePath": self.InterviewEvaluation_FilePath,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat(),
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
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
    Status = db.Column(db.Boolean, nullable=True)
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
            'Status': self.Status,
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
    Status = db.Column(db.Boolean, nullable=True)
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
            'Status': self.Status,
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
    EmployeeId = db.Column(db.Integer, db.ForeignKey('StaffInfo.Staff_ID'), nullable=False)
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

class SalaryHold(db.Model):
    __tablename__ = 'SalaryHold'

    SalaryHold_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SalaryHold_StaffId = db.Column(db.Integer, nullable=False)
    SalaryHold_Status = db.Column(db.Boolean, nullable=False)
    SalaryHold_Month = db.Column(db.String(20), nullable=False)
    SalaryHold_Reason = db.Column(db.String(100), nullable=False)
    SalaryHold_InitiatedBy = db.Column(db.Integer, nullable=False)
    SalaryHold_ApprovedBy = db.Column(db.Integer, nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'SalaryHold_Id': self.SalaryHold_Id,
            'SalaryHold_StaffId': self.SalaryHold_StaffId,
            'SalaryHold_Status': self.SalaryHold_Status,
            'SalaryHold_Month': self.SalaryHold_Month,
            'SalaryHold_Reason': self.SalaryHold_Reason,
            'SalaryHold_InitiatedBy': self.SalaryHold_InitiatedBy,
            'SalaryHold_ApprovedBy': self.SalaryHold_ApprovedBy,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat(),
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
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
    StaffIncrement_StaffId = db.Column(db.Integer, db.ForeignKey('StaffInfo.Staff_ID'), nullable=False)
    StaffIncrement_CurrentSalary = db.Column(db.Float, nullable=False)
    StaffIncrement_Date = db.Column(db.DateTime, nullable=False)
    StaffIncrement_Reason = db.Column(db.Integer, nullable=False)
    StaffIncrement_Others = db.Column(db.String(200))
    StaffIncrement_NewSalary = db.Column(db.Float, nullable=False)
    StaffIncrement_PercentageIncrease = db.Column(db.Float, nullable=False)
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
    StaffSeparation_NoticePeriod = db.Column(db.String(200), nullable=False)
    StaffSeparation_ResignationApproved = db.Column(db.String(200), nullable=False)
    StaffSeparation_SalaryHoldMonth = db.Column(db.String(20), nullable=False)
    StaffSeparation_ClearanceDone = db.Column(db.Boolean, nullable=False)
    StaffSeparation_ClearanceDate = db.Column(db.DateTime)
    StaffSeparation_ExitInterview = db.Column(db.String(200), nullable=False)
    StaffSeparation_ExitInterviewDate = db.Column(db.DateTime)
    StaffSeparation_FinalSettlementDone = db.Column(db.String(200), nullable=False)
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
    PayrollClose_Period = db.Column(db.String(100), nullable=False)
    PayrollClose_CloseDate = db.Column(db.DateTime, nullable=False)
    PayrollClose_ProcessedBy = db.Column(db.Integer, nullable=False)
    PayrollClose_ReviewedBy = db.Column(db.Integer, nullable=False)
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
            'PayrollClose_Period': self.PayrollClose_Period,
            'PayrollClose_CloseDate': self.PayrollClose_CloseDate.isoformat() if self.PayrollClose_CloseDate else None,
            'PayrollClose_ProcessedBy': self.PayrollClose_ProcessedBy,
            'PayrollClose_ReviewedBy': self.PayrollClose_ReviewedBy,
            'PayrollClose_ApprovedBy': self.PayrollClose_ApprovedBy,
            'PayrollClose_Remarks': self.PayrollClose_Remarks,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat() if self.CreatedDate else None,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class TeacherDemoEvaluation(db.Model):
    __tablename__ = 'TeacherDemoEvaluation'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    JobApplicationFormId = db.Column(db.Integer, nullable=False)
    InterviewerId = db.Column(db.Integer, nullable=False)
    EvaluationDate = db.Column(db.DateTime, nullable=True)
    CampusId = db.Column(db.Integer, nullable=True)
    IntroductionGivenRating = db.Column(db.Integer, nullable=False)
    IntroductionGivenComments = db.Column(db.String(200), nullable=True)
    AttireAndAppearanceRating = db.Column(db.Integer, nullable=False)
    AttireAndAppearanceComments = db.Column(db.String(200), nullable=True)
    MovementDuringTeachingRating = db.Column(db.Integer, nullable=False)
    MovementDuringTeachingComments = db.Column(db.String(200), nullable=True)
    EyecontactWithStudentsRating = db.Column(db.Integer, nullable=False)
    EyecontactWithStudentsComments = db.Column(db.String(200), nullable=True)
    GestureAndPostureRating = db.Column(db.Integer, nullable=False)
    GestureAndPostureComments = db.Column(db.String(200), nullable=True)
    SpokeLoudlyAndClearlyRating = db.Column(db.Integer, nullable=False)
    SpokeLoudlyAndClearlyComments = db.Column(db.String(200), nullable=True)
    AgeAppropriateToneAndLanguageRating = db.Column(db.Integer, nullable=False)
    AgeAppropriateToneAndLanguageComments = db.Column(db.String(200), nullable=True)
    CommunicationRating = db.Column(db.Integer, nullable=False)
    CommunicationComments = db.Column(db.String(200), nullable=True)
    WithitnessRating = db.Column(db.Integer, nullable=False)
    WithitnessComments = db.Column(db.String(200), nullable=True)
    ArousedStudentInterestAndEncouragementRating = db.Column(db.Integer, nullable=False)
    ArousedStudentInterestAndEncouragementComments = db.Column(db.String(200), nullable=True)
    CreativityAndInnovationRating = db.Column(db.Integer, nullable=False)
    CreativityAndInnovationComments = db.Column(db.String(200), nullable=True)
    SubjectMatterKnowledgeRating = db.Column(db.Integer, nullable=False)
    SubjectMatterKnowledgeComments = db.Column(db.String(200), nullable=True)
    PresentedSubjectMatterClearlyRating = db.Column(db.Integer, nullable=False)
    PresentedSubjectMatterClearlyComments = db.Column(db.String(200), nullable=True)
    AppropriateMethodologyRating = db.Column(db.Integer, nullable=False)
    AppropriateMethodologyComments = db.Column(db.String(200), nullable=True)
    RespondedToStudentQueriesRating = db.Column(db.Integer, nullable=False)
    RespondedToStudentQueriesComments = db.Column(db.String(200), nullable=True)
    ClassControlRating = db.Column(db.Integer, nullable=False)
    ClassControlComments = db.Column(db.String(200), nullable=True)
    TimeManagementRating = db.Column(db.Integer, nullable=False)
    TimeManagementComments = db.Column(db.String(200), nullable=True)
    UsedSuitableWarmUpStrategyRating = db.Column(db.Integer, nullable=False)
    UsedSuitableWarmUpStrategyComments = db.Column(db.String(200), nullable=True)
    WasAbleToEffectivelySumUpLessonRating = db.Column(db.Integer, nullable=False)
    WasAbleToEffectivelySumUpLessonComments = db.Column(db.String(200), nullable=True)
    ConfidenceLevelExhibitedRating = db.Column(db.Integer, nullable=False)
    ConfidenceLevelExhibitedComments = db.Column(db.String(200), nullable=True)
    ShowedDynamismAndEnthusiasmRating = db.Column(db.Integer, nullable=False)
    ShowedDynamismAndEnthusiasmComments = db.Column(db.String(200), nullable=True)
    AdditionalComments = db.Column(db.String(1000), nullable=True)
    Recommended = db.Column(db.Boolean, nullable=False)
    WritingOnBoardRating = db.Column(db.Integer, nullable=False)
    WritingOnBoardComments = db.Column(db.String(200), nullable=True)
    FilePath = db.Column(db.String(100), nullable=True)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    InActive = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<TeacherDemoEvaluation Id={self.Id}, JobApplicationFormId={self.JobApplicationFormId}, InterviewerId={self.InterviewerId}>"

    def to_dict(self):
        return {
            'Id': self.Id,
            'JobApplicationFormId': self.JobApplicationFormId,
            'InterviewerId': self.InterviewerId,
            'EvaluationDate': self.EvaluationDate,
            'CampusId': self.CampusId,
            'IntroductionGivenRating': self.IntroductionGivenRating,
            'IntroductionGivenComments': self.IntroductionGivenComments,
            'AttireAndAppearanceRating': self.AttireAndAppearanceRating,
            'AttireAndAppearanceComments': self.AttireAndAppearanceComments,
            'MovementDuringTeachingRating': self.MovementDuringTeachingRating,
            'MovementDuringTeachingComments': self.MovementDuringTeachingComments,
            'EyecontactWithStudentsRating': self.EyecontactWithStudentsRating,
            'EyecontactWithStudentsComments': self.EyecontactWithStudentsComments,
            'GestureAndPostureRating': self.GestureAndPostureRating,
            'GestureAndPostureComments': self.GestureAndPostureComments,
            'SpokeLoudlyAndClearlyRating': self.SpokeLoudlyAndClearlyRating,
            'SpokeLoudlyAndClearlyComments': self.SpokeLoudlyAndClearlyComments,
            'AgeAppropriateToneAndLanguageRating': self.AgeAppropriateToneAndLanguageRating,
            'AgeAppropriateToneAndLanguageComments': self.AgeAppropriateToneAndLanguageComments,
            'CommunicationRating': self.CommunicationRating,
            'CommunicationComments': self.CommunicationComments,
            'WithitnessRating': self.WithitnessRating,
            'WithitnessComments': self.WithitnessComments,
            'ArousedStudentInterestAndEncouragementRating': self.ArousedStudentInterestAndEncouragementRating,
            'ArousedStudentInterestAndEncouragementComments': self.ArousedStudentInterestAndEncouragementComments,
            'CreativityAndInnovationRating': self.CreativityAndInnovationRating,
            'CreativityAndInnovationComments': self.CreativityAndInnovationComments,
            'SubjectMatterKnowledgeRating': self.SubjectMatterKnowledgeRating,
            'SubjectMatterKnowledgeComments': self.SubjectMatterKnowledgeComments,
            'PresentedSubjectMatterClearlyRating': self.PresentedSubjectMatterClearlyRating,
            'PresentedSubjectMatterClearlyComments': self.PresentedSubjectMatterClearlyComments,
            'AppropriateMethodologyRating': self.AppropriateMethodologyRating,
            'AppropriateMethodologyComments': self.AppropriateMethodologyComments,
            'RespondedToStudentQueriesRating': self.RespondedToStudentQueriesRating,
            'RespondedToStudentQueriesComments': self.RespondedToStudentQueriesComments,
            'ClassControlRating': self.ClassControlRating,
            'ClassControlComments': self.ClassControlComments,
            'TimeManagementRating': self.TimeManagementRating,
            'TimeManagementComments': self.TimeManagementComments,
            'UsedSuitableWarmUpStrategyRating': self.UsedSuitableWarmUpStrategyRating,
            'UsedSuitableWarmUpStrategyComments': self.UsedSuitableWarmUpStrategyComments,
            'WasAbleToEffectivelySumUpLessonRating': self.WasAbleToEffectivelySumUpLessonRating,
            'WasAbleToEffectivelySumUpLessonComments': self.WasAbleToEffectivelySumUpLessonComments,
            'ConfidenceLevelExhibitedRating': self.ConfidenceLevelExhibitedRating,
            'ConfidenceLevelExhibitedComments': self.ConfidenceLevelExhibitedComments,
            'ShowedDynamismAndEnthusiasmRating': self.ShowedDynamismAndEnthusiasmRating,
            'ShowedDynamismAndEnthusiasmComments': self.ShowedDynamismAndEnthusiasmComments,
            'AdditionalComments': self.AdditionalComments,
            'Recommended': self.Recommended,
            'FilePath': self.FilePath,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate,
            'InActive': self.InActive
        }

class StaffOnDutyForm(db.Model):
    __tablename__ = 'StaffOnDutyForm'

    StaffOnDutyForm_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StaffOnDutyForm_StaffId = db.Column(db.Integer, nullable=False)
    StaffOnDutyForm_Date = db.Column(db.DateTime, nullable=False)
    StaffOnDutyForm_TimeIn = db.Column(db.Time, nullable=False)
    StaffOnDutyForm_TimeOut = db.Column(db.Time, nullable=False)
    StaffOnDutyForm_Task = db.Column(db.String(250), nullable=False)
    StaffOnDutyForm_Remarks = db.Column(db.String(500), nullable=True)
    StaffOnDutyForm_Location = db.Column(db.String(200), nullable=False)
    StaffOnDutyForm_ApprovedBy = db.Column(db.Integer, nullable=True)
    StaffOnDutyForm_ApprovedStatusId = db.Column(db.Integer, nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    InActive = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<StaffOnDutyForm Id={self.StaffOnDutyForm_Id}, StaffId={self.StaffOnDutyForm_StaffId}, Date={self.StaffOnDutyForm_Date}>"

    def to_dict(self):
        return {
            'StaffOnDutyForm_Id': self.StaffOnDutyForm_Id,
            'StaffOnDutyForm_StaffId': self.StaffOnDutyForm_StaffId,
            'StaffOnDutyForm_Date': self.StaffOnDutyForm_Date,
            'StaffOnDutyForm_TimeIn': self.StaffOnDutyForm_TimeIn,
            'StaffOnDutyForm_TimeOut': self.StaffOnDutyForm_TimeOut,
            'StaffOnDutyForm_Task': self.StaffOnDutyForm_Task,
            'StaffOnDutyForm_Remarks': self.StaffOnDutyForm_Remarks,
            'StaffOnDutyForm_Location': self.StaffOnDutyForm_Location,
            'StaffOnDutyForm_ApprovedBy': self.StaffOnDutyForm_ApprovedBy,
            'StaffOnDutyForm_ApprovedStatusId': self.StaffOnDutyForm_ApprovedStatusId,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate,
            'InActive': self.InActive
        }

class StaffWaiverForm(db.Model):
    __tablename__ = 'StaffWaiverForm'

    StaffWaiverForm_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StaffWaiverForm_StaffId = db.Column(db.Integer, nullable=False)
    StaffWaiverForm_Date = db.Column(db.DateTime, nullable=False)
    StaffWaiverForm_TimeIn = db.Column(db.Time, nullable=False)
    StaffWaiverForm_TimeOut = db.Column(db.Time, nullable=False)
    StaffWaiverForm_Reason = db.Column(db.String(250), nullable=False)
    StaffWaiverForm_ApprovedBy = db.Column(db.Integer, nullable=False)
    StaffWaiverForm_ApprovedStatusId = db.Column(db.Integer, nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    InActive = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<StaffWaiverForm Id={self.StaffWaiverForm_Id}, StaffId={self.StaffWaiverForm_StaffId}, Date={self.StaffWaiverForm_Date}>"

    def to_dict(self):
        return {
            'StaffWaiverForm_Id': self.StaffWaiverForm_Id,
            'StaffWaiverForm_StaffId': self.StaffWaiverForm_StaffId,
            'StaffWaiverForm_Date': self.StaffWaiverForm_Date,
            'StaffWaiverForm_TimeIn': self.StaffWaiverForm_TimeIn,
            'StaffWaiverForm_TimeOut': self.StaffWaiverForm_TimeOut,
            'StaffWaiverForm_Reason': self.StaffWaiverForm_Reason,
            'StaffWaiverForm_ApprovedBy': self.StaffWaiverForm_ApprovedBy,
            'StaffWaiverForm_ApprovedStatusId': self.StaffWaiverForm_ApprovedStatusId,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate,
            'InActive': self.InActive
        }

class StaffGraceTime(db.Model):
    __tablename__ = 'StaffGraceTime'

    StaffGraceTime_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StaffGraceTime_StaffId = db.Column(db.Integer, nullable=False)
    StaffGraceTime_Date = db.Column(db.DateTime, nullable=False)
    StaffGraceTime_Minutes = db.Column(db.Integer, nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    InActive = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<StaffGraceTime Id={self.StaffGraceTime_Id}, StaffId={self.StaffGraceTime_StaffId}, Date={self.StaffGraceTime_Date}>"

    def to_dict(self):
        return {
            'StaffGraceTime_Id': self.StaffGraceTime_Id,
            'StaffGraceTime_StaffId': self.StaffGraceTime_StaffId,
            'StaffGraceTime_Date': self.StaffGraceTime_Date,
            'StaffGraceTime_Minutes': self.StaffGraceTime_Minutes,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate,
            'InActive': self.InActive
        }

class SpecialApprovalForm(db.Model):
    __tablename__ = 'SpecialApprovalForm'

    SpecialApprovalForm_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SpecialApprovalForm_StaffId = db.Column(db.Integer, nullable=False)
    SpecialApprovalForm_FromDate = db.Column(db.DateTime, nullable=False)
    SpecialApprovalForm_ToDate = db.Column(db.DateTime, nullable=False)
    SpecialApprovalForm_Reason = db.Column(db.String(200), nullable=False)
    SpecialApprovalForm_ApprovedBy = db.Column(db.Integer, nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    InActive = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return f"<SpecialApprovalForm Id={self.SpecialApprovalForm_Id}, StaffId={self.SpecialApprovalForm_StaffId}>"

    def to_dict(self):
        return {
            'SpecialApprovalForm_Id': self.SpecialApprovalForm_Id,
            'SpecialApprovalForm_StaffId': self.SpecialApprovalForm_StaffId,
            'SpecialApprovalForm_FromDate': self.SpecialApprovalForm_FromDate,
            'SpecialApprovalForm_ToDate': self.SpecialApprovalForm_ToDate,
            'SpecialApprovalForm_Reason': self.SpecialApprovalForm_Reason,
            'SpecialApprovalForm_ApprovedBy': self.SpecialApprovalForm_ApprovedBy,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate,
            'InActive': self.InActive
        }

class FinalStatus(db.Model):
    __tablename__ = 'FinalStatus'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Form_Id = db.Column(db.Integer, nullable=True)
    Status = db.Column(db.Boolean, nullable=True)
    Remarks = db.Column(db.String(200), nullable=True)
    CreatorId = db.Column(db.Integer, nullable=True)
    CreatedDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    def __repr__(self):
        return f"<FinalStatus Id={self.Id}, Form_Id={self.Form_Id}, Status={self.Status}>"

    def to_dict(self):
        return {
            'Id': self.Id,
            'Form_Id': self.Form_Id,
            'Status': self.Status,
            'Remarks': self.Remarks,
            'CreatorId': self.CreatorId,
            'CreatedDate': self.CreatedDate
        }

class CCHST(db.Model):
    __tablename__ = 'CCHST'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    JobApplicationForm_Id = db.Column(db.Integer, nullable=False)
    Status = db.Column(db.String(50), nullable=True)
    Auto = db.Column(db.Boolean, nullable=True)
    Manual = db.Column(db.Boolean, nullable=True)
    Remarks = db.Column(db.String(200), nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    CreatorId = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<CCHST Id={self.Id}, JobApplicationForm_Id={self.JobApplicationForm_Id}, Status={self.Status}>"

    def to_dict(self):
        return {
            'Id': self.Id,
            'JobApplicationForm_Id': self.JobApplicationForm_Id,
            'Status': self.Status,
            'Auto': self.Auto,
            'Manual': self.Manual,
            'Remarks': self.Remarks,
            'CreateDate': self.CreateDate,
            'CreatorId': self.CreatorId
        }
# ------- LEAVE -------

class LeaveStatus(db.Model):
    __tablename__ = 'LeaveStatus'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    LeaveStatusName = db.Column(db.String(50), nullable=False)
    Status = db.Column(db.Boolean, nullable=False)
    CampusId = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'Id': self.Id,
            'LeaveStatusName': self.LeaveStatusName,
            'Status': self.Status,
            'CampusId': self.CampusId
        }

class LeaveType(db.Model):
    __tablename__ = 'LeaveType'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    LeaveTypeName = db.Column(db.String(50), nullable=True)
    LeaveTypeCode = db.Column(db.String(50), nullable=True)
    Status = db.Column(db.Boolean, nullable=False)
    UpdaterId = db.Column(db.BigInteger, nullable=True)
    UpdaterIP = db.Column(db.String(20), nullable=True)
    UpdaterTerminal = db.Column(db.String(255), nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)
    CreatorId = db.Column(db.BigInteger, nullable=True)
    CreatorIP = db.Column(db.String(20), nullable=True)
    CreatorTerminal = db.Column(db.String(255), nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True)
    CampusId = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'Id': self.Id,
            'LeaveTypeName': self.LeaveTypeName,
            'LeaveTypeCode': self.LeaveTypeCode,
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

class StaffLeaveRequest(db.Model):
    __tablename__ = 'StaffLeaveRequest'
    
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StaffId = db.Column(db.Integer, nullable=False)
    FromDate = db.Column(db.Date, nullable=False)
    ToDate = db.Column(db.Date, nullable=False)
    Reason = db.Column(db.String(255), nullable=False)
    Remarks = db.Column(db.String(255))
    LeaveStatusId = db.Column(db.Integer, nullable=False)
    ApprovedBy = db.Column(db.Integer)
    LeaveApplicationPath = db.Column(db.String(255))
    AcademicYearId = db.Column(db.Integer)
    status = db.Column(db.Boolean, nullable=False)
    UpdaterId = db.Column(db.BigInteger)
    UpdaterIP = db.Column(db.String(20))
    UpdaterTerminal = db.Column(db.String(255))
    UpdateDate = db.Column(db.DateTime)
    CreatorId = db.Column(db.BigInteger)
    CreatorIP = db.Column(db.String(20))
    CreatorTerminal = db.Column(db.String(255))
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow)
    CampusId = db.Column(db.Integer)
    LeaveTypeId = db.Column(db.Integer)

    def to_dict(self):
        return {
            'Id': self.Id,
            'StaffId': self.StaffId,
            'FromDate': self.FromDate.isoformat(),
            'ToDate': self.ToDate.isoformat(),
            'Reason': self.Reason,
            'Remarks': self.Remarks,
            'LeaveStatusId': self.LeaveStatusId,
            'ApprovedBy': self.ApprovedBy,
            'LeaveApplicationPath': self.LeaveApplicationPath,
            'AcademicYearId': self.AcademicYearId,
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
            'LeaveTypeId': self.LeaveTypeId
        }

class StaffLeaveAssign(db.Model):
    __tablename__ = 'StaffLeaveAssign'
    
    LeaveAssignId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserId = db.Column(db.Integer, nullable=False)
    DepartmentId = db.Column(db.Integer, nullable=False)
    CampusId = db.Column(db.Integer)
    CreatorId = db.Column(db.Integer)
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'LeaveAssignId': self.LeaveAssignId,
            'UserId': self.UserId,
            'DepartmentId': self.DepartmentId,
            'CampusId': self.CampusId,
            'CreatorId': self.CreatorId,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None
        }

class StaffLeaveRequestDateRanges(db.Model):
    __tablename__ = 'StaffLeaveRequestDateRanges'
    
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    LeaveRequestId = db.Column(db.Integer)
    Date = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'Id': self.Id,
            'LeaveRequestId': self.LeaveRequestId,
            'Date': self.Date.isoformat() if self.Date else None
        }


# ------- HISTORY -------

class NewJoinerApprovalHistory(Base):
    __tablename__ = 'NewJoinerApprovalHistory'
    History_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    History_NewJoinerApproval_StaffId = db.Column(db.Integer, nullable=False)
    History_NewJoinerApproval_Salary = db.Column(db.Float, nullable=False)
    History_NewJoinerApproval_HiringApprovedBy = db.Column(db.Integer, nullable=False)
    History_NewJoinerApproval_FileVerified = db.Column(db.Boolean, nullable=False)
    History_NewJoinerApproval_EmpDetailsVerified = db.Column(db.Boolean, nullable=False)
    History_NewJoinerApproval_AddToPayrollMonth = db.Column(db.String(15), nullable=False)
    History_NewJoinerApproval_Remarks = db.Column(db.String(300), nullable=False)
    History_NewJoinerApproval_Id = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    CreatedBy = db.Column(db.Integer, nullable=False)
    UpdatedBy = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True)
    InActive = db.Column(db.Boolean, nullable=False)
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class OneTimeAllowanceHistory(db.Model):
    __tablename__ = 'OneTimeAllowanceHistory'

    OneTimeAllowanceHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OneTimeAllowanceHistory_StaffId = db.Column(db.Integer, nullable=False)
    OneTimeAllowanceHistory_AllowanceHeadId = db.Column(db.Integer, nullable=False)
    OneTimeAllowanceHistory_Amount = db.Column(db.Float, nullable=False)
    OneTimeAllowanceHistory_PamentMonth = db.Column(db.String(15), nullable=False)
    OneTimeAllowanceHistory_ApprovedBy = db.Column(db.Integer, nullable=False)
    OneTimeAllowanceHistory_Taxable = db.Column(db.Boolean, nullable=False)
    OneTimeAllowanceHistory_OneTimeAllowance_Id = db.Column(db.Integer, nullable=False)
    CreatorId = db.Column(db.Integer, nullable=False)
    CreateDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatorId = db.Column(db.Integer, nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'OneTimeAllowanceHistory_Id': self.OneTimeAllowanceHistory_Id,
            'OneTimeAllowanceHistory_StaffId': self.OneTimeAllowanceHistory_StaffId,
            'OneTimeAllowanceHistory_AllowanceHeadId': self.OneTimeAllowanceHistory_AllowanceHeadId,
            'OneTimeAllowanceHistory_Amount': self.OneTimeAllowanceHistory_Amount,
            'OneTimeAllowanceHistory_PamentMonth': self.OneTimeAllowanceHistory_PamentMonth,
            'OneTimeAllowanceHistory_ApprovedBy': self.OneTimeAllowanceHistory_ApprovedBy,
            'OneTimeAllowanceHistory_Taxable': self.OneTimeAllowanceHistory_Taxable,
            'OneTimeAllowanceHistory_OneTimeAllowance_Id': self.OneTimeAllowanceHistory_OneTimeAllowance_Id,
            'CreatorId': self.CreatorId,
            'CreateDate': self.CreateDate.isoformat(),
            'UpdatorId': self.UpdatorId,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'InActive': self.InActive
        }

class OneTimeDeductionHistory(db.Model):
    __tablename__ = 'OneTimeDeductionHistory'

    OneTimeDeductionHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OneTimeDeductionHistory_StaffId = db.Column(db.Integer, nullable=False)
    OneTimeDeductionHistory_DeductionHeadId = db.Column(db.Integer, nullable=False)
    OneTimeDeductionHistory_Amount = db.Column(db.Float, nullable=False)
    OneTimeDeductionHistory_DeductionMonth = db.Column(db.String(15), nullable=False)
    OneTimeDeductionHistory_ApprovedBy = db.Column(db.Integer, nullable=False)
    OneTimeDeductionHistory_OneTimeDeduction_Id = db.Column(db.Integer, nullable=False)
    CreatorId = db.Column(db.Integer, nullable=False)
    CreateDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatorId = db.Column(db.Integer, nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'OneTimeDeductionHistory_Id': self.OneTimeDeductionHistory_Id,
            'OneTimeDeductionHistory_StaffId': self.OneTimeDeductionHistory_StaffId,
            'OneTimeDeductionHistory_DeductionHeadId': self.OneTimeDeductionHistory_DeductionHeadId,
            'OneTimeDeductionHistory_Amount': self.OneTimeDeductionHistory_Amount,
            'OneTimeDeductionHistory_DeductionMonth': self.OneTimeDeductionHistory_DeductionMonth,
            'OneTimeDeductionHistory_ApprovedBy': self.OneTimeDeductionHistory_ApprovedBy,
            'OneTimeDeductionHistory_OneTimeDeduction_Id': self.OneTimeDeductionHistory_OneTimeDeduction_Id,
            'CreatorId': self.CreatorId,
            'CreateDate': self.CreateDate.isoformat(),
            'UpdatorId': self.UpdatorId,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'InActive': self.InActive
        }

class PayrollCloseHistory(db.Model):
    __tablename__ = 'PayrollCloseHistory'

    PayrollCloseHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PayrollCloseHistory_Period = db.Column(db.String(100), nullable=False)
    PayrollCloseHistory_CloseDate = db.Column(db.DateTime, nullable=False)
    PayrollCloseHistory_ProcessedBy = db.Column(db.Integer, nullable=False)
    PayrollCloseHistory_ReviewedBy = db.Column(db.Integer, nullable=False)
    PayrollCloseHistory_ApprovedBy = db.Column(db.Integer, nullable=False)
    PayrollCloseHistory_Remarks = db.Column(db.String(200), nullable=False)
    PayrollCloseHistory_PayrollClose_Id = db.Column(db.Integer, nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'PayrollCloseHistory_Id': self.PayrollCloseHistory_Id,
            'PayrollCloseHistory_Period': self.PayrollCloseHistory_Period,
            'PayrollCloseHistory_CloseDate': self.PayrollCloseHistory_CloseDate.isoformat(),
            'PayrollCloseHistory_ProcessedBy': self.PayrollCloseHistory_ProcessedBy,
            'PayrollCloseHistory_ReviewedBy': self.PayrollCloseHistory_ReviewedBy,
            'PayrollCloseHistory_ApprovedBy': self.PayrollCloseHistory_ApprovedBy,
            'PayrollCloseHistory_Remarks': self.PayrollCloseHistory_Remarks,
            'PayrollCloseHistory_PayrollClose_Id': self.PayrollCloseHistory_PayrollClose_Id,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat(),
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class SalaryHoldHistory(db.Model):
    __tablename__ = 'SalaryHoldHistory'

    SalaryHoldHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SalaryHoldHistory_StaffId = db.Column(db.Integer, nullable=False)
    SalaryHoldHistory_Status = db.Column(db.Boolean, nullable=False)
    SalaryHoldHistory_Month = db.Column(db.String(20), nullable=False)
    SalaryHoldHistory_Reason = db.Column(db.String(100), nullable=False)
    SalaryHoldHistory_InitiatedBy = db.Column(db.Integer, nullable=False)
    SalaryHoldHistory_ApprovedBy = db.Column(db.Integer, nullable=False)
    SalaryHoldHistory_SalaryHold_Id = db.Column(db.Integer, nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'SalaryHoldHistory_Id': self.SalaryHoldHistory_Id,
            'SalaryHoldHistory_StaffId': self.SalaryHoldHistory_StaffId,
            'SalaryHoldHistory_Status': self.SalaryHoldHistory_Status,
            'SalaryHoldHistory_Month': self.SalaryHoldHistory_Month,
            'SalaryHoldHistory_Reason': self.SalaryHoldHistory_Reason,
            'SalaryHoldHistory_InitiatedBy': self.SalaryHoldHistory_InitiatedBy,
            'SalaryHoldHistory_ApprovedBy': self.SalaryHoldHistory_ApprovedBy,
            'SalaryHoldHistory_SalaryHold_Id': self.SalaryHoldHistory_SalaryHold_Id,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat(),
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class SalaryTransferDetailsHistory(db.Model):
    __tablename__ = 'SalaryTransferDetailsHistory'

    SalaryTransferDetailsHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SalaryTransferDetailsHistory_StaffId = db.Column(db.Integer, nullable=False)
    SalaryTransferDetailsHistory_TransferMethod = db.Column(db.String(20), nullable=False)
    SalaryTransferDetailsHistory_BankName = db.Column(db.String(200), nullable=True)
    SalaryTransferDetailsHistory_BankAccountNumber = db.Column(db.String(200), nullable=True)
    SalaryTransferDetailsHistory_BankBranch = db.Column(db.String(200), nullable=True)
    SalaryTransferDetailsHistory_BankOrChequeTitle = db.Column(db.String(200), nullable=False)
    SalaryTransferDetailsHistory_ReasonForChequeIssuance = db.Column(db.String(200), nullable=True)
    SalaryTransferDetailsHistory_EffectiveDate = db.Column(db.DateTime, nullable=False)
    SalaryTransferDetailsHistory_Remarks = db.Column(db.String(200), nullable=False)
    SalaryTransferDetailsHistory_SalaryTransferDetails_Id = db.Column(db.Integer, nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer, nullable=True)
    UpdatedDate = db.Column(db.DateTime, nullable=True)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'SalaryTransferDetailsHistory_Id': self.SalaryTransferDetailsHistory_Id,
            'SalaryTransferDetailsHistory_StaffId': self.SalaryTransferDetailsHistory_StaffId,
            'SalaryTransferDetailsHistory_TransferMethod': self.SalaryTransferDetailsHistory_TransferMethod,
            'SalaryTransferDetailsHistory_BankName': self.SalaryTransferDetailsHistory_BankName,
            'SalaryTransferDetailsHistory_BankAccountNumber': self.SalaryTransferDetailsHistory_BankAccountNumber,
            'SalaryTransferDetailsHistory_BankBranch': self.SalaryTransferDetailsHistory_BankBranch,
            'SalaryTransferDetailsHistory_BankOrChequeTitle': self.SalaryTransferDetailsHistory_BankOrChequeTitle,
            'SalaryTransferDetailsHistory_ReasonForChequeIssuance': self.SalaryTransferDetailsHistory_ReasonForChequeIssuance,
            'SalaryTransferDetailsHistory_EffectiveDate': self.SalaryTransferDetailsHistory_EffectiveDate.isoformat(),
            'SalaryTransferDetailsHistory_Remarks': self.SalaryTransferDetailsHistory_Remarks,
            'SalaryTransferDetailsHistory_SalaryTransferDetails_Id': self.SalaryTransferDetailsHistory_SalaryTransferDetails_Id,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat(),
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class ScheduledAllowanceHistory(db.Model):
    __tablename__ = 'ScheduledAllowanceHistory'

    ScheduledAllowanceHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ScheduledAllowanceHistory_StaffId = db.Column(db.Integer, nullable=False)
    ScheduledAllowanceHistory_AllowanceHeadId = db.Column(db.Integer, nullable=False)
    ScheduledAllowanceHistory_AmountPerMonth = db.Column(db.Float, nullable=False)
    ScheduledAllowanceHistory_StartDate = db.Column(db.DateTime, nullable=False)
    ScheduledAllowanceHistory_EndDate = db.Column(db.DateTime, nullable=False)
    ScheduledAllowanceHistory_ApprovedBy = db.Column(db.Integer, nullable=False)
    ScheduledAllowanceHistory_ScheduledAllowance_Id = db.Column(db.Integer, nullable=False)
    CreatorId = db.Column(db.Integer, nullable=False)
    CreateDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatorId = db.Column(db.Integer, nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)
    InActive = db.Column(db.Boolean, nullable=False)
    ScheduledAllowanceHistory_Taxable = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'ScheduledAllowanceHistory_Id': self.ScheduledAllowanceHistory_Id,
            'ScheduledAllowanceHistory_StaffId': self.ScheduledAllowanceHistory_StaffId,
            'ScheduledAllowanceHistory_AllowanceHeadId': self.ScheduledAllowanceHistory_AllowanceHeadId,
            'ScheduledAllowanceHistory_AmountPerMonth': self.ScheduledAllowanceHistory_AmountPerMonth,
            'ScheduledAllowanceHistory_StartDate': self.ScheduledAllowanceHistory_StartDate.isoformat(),
            'ScheduledAllowanceHistory_EndDate': self.ScheduledAllowanceHistory_EndDate.isoformat(),
            'ScheduledAllowanceHistory_ApprovedBy': self.ScheduledAllowanceHistory_ApprovedBy,
            'ScheduledAllowanceHistory_ScheduledAllowance_Id': self.ScheduledAllowanceHistory_ScheduledAllowance_Id,
            'CreatorId': self.CreatorId,
            'CreateDate': self.CreateDate.isoformat(),
            'UpdatorId': self.UpdatorId,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'InActive': self.InActive,
            'ScheduledAllowanceHistory_Taxable': self.ScheduledAllowanceHistory_Taxable
        }

class ScheduledDeductionHistory(db.Model):
    __tablename__ = 'ScheduledDeductionHistory'

    ScheduledDeductionHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ScheduledDeductionHistory_StaffId = db.Column(db.Integer, nullable=False)
    ScheduledDeductionHistory_DeductionHeadId = db.Column(db.Integer, nullable=False)
    ScheduledDeductionHistory_AmountPerMonth = db.Column(db.Float, nullable=False)
    ScheduledDeductionHistory_StartDate = db.Column(db.DateTime, nullable=False)
    ScheduledDeductionHistory_EndDate = db.Column(db.DateTime, nullable=False)
    ScheduledDeductionHistory_ApprovedBy = db.Column(db.Integer, nullable=False)
    ScheduledDeductionHistory_ScheduledDeduction_Id = db.Column(db.Integer, nullable=False)
    CreatorId = db.Column(db.Integer, nullable=False)
    CreateDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatorId = db.Column(db.Integer, nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)
    InActive = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            'ScheduledDeductionHistory_Id': self.ScheduledDeductionHistory_Id,
            'ScheduledDeductionHistory_StaffId': self.ScheduledDeductionHistory_StaffId,
            'ScheduledDeductionHistory_DeductionHeadId': self.ScheduledDeductionHistory_DeductionHeadId,
            'ScheduledDeductionHistory_AmountPerMonth': self.ScheduledDeductionHistory_AmountPerMonth,
            'ScheduledDeductionHistory_StartDate': self.ScheduledDeductionHistory_StartDate.isoformat(),
            'ScheduledDeductionHistory_EndDate': self.ScheduledDeductionHistory_EndDate.isoformat(),
            'ScheduledDeductionHistory_ApprovedBy': self.ScheduledDeductionHistory_ApprovedBy,
            'ScheduledDeductionHistory_ScheduledDeduction_Id': self.ScheduledDeductionHistory_ScheduledDeduction_Id,
            'CreatorId': self.CreatorId,
            'CreateDate': self.CreateDate.isoformat(),
            'UpdatorId': self.UpdatorId,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'InActive': self.InActive
        }

class StaffInfoHistory(db.Model):
    __tablename__ = 'StaffInfo_History'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Staff_ID = db.Column(db.Integer, nullable=False)
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
    P_Salary = db.Column(db.Float)
    Grace_In = db.Column(db.Integer)
    Grace_Out = db.Column(db.Integer)

    def to_dict(self):
        return {
            'Id': self.Id,
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
            'P_Salary': self.P_Salary,
            'Grace_In': self.Grace_In,
            'Grace_Out': self.Grace_Out
        }

class StaffPromotionsHistory(db.Model):
    __tablename__ = 'StaffPromotionsHistory'

    StaffPromotionHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StaffPromotionHistory_StaffId = db.Column(db.Integer, nullable=False)
    StaffPromotionHistory_SalaryHold = db.Column(db.Boolean, nullable=False)
    StaffPromotionHistory_NewDesignationId = db.Column(db.Integer, nullable=False)
    StaffPromotionHistory_NewDepartmentId = db.Column(db.Integer, nullable=False)
    StaffPromotionHistory_Date = db.Column(db.DateTime, nullable=False)
    StaffPromotionHistory_Reason = db.Column(db.String(100), nullable=False)
    StaffPromotionHistory_InitiatedBy = db.Column(db.Integer, nullable=False)
    StaffPromotionHistory_ApprovedBy = db.Column(db.Integer, nullable=False)
    StaffPromotionHistory_NewSalary = db.Column(db.Float, nullable=False)
    StaffPromotionHistory_NewSalaryEffectiveDate = db.Column(db.DateTime, nullable=False)
    StaffPromotionHistory_Remarks = db.Column(db.String(200), nullable=False)
    StaffPromotionHistory_StaffPromotion_Id = db.Column(db.Integer, nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer)
    UpdatedDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'StaffPromotionHistory_Id': self.StaffPromotionHistory_Id,
            'StaffPromotionHistory_StaffId': self.StaffPromotionHistory_StaffId,
            'StaffPromotionHistory_SalaryHold': self.StaffPromotionHistory_SalaryHold,
            'StaffPromotionHistory_NewDesignationId': self.StaffPromotionHistory_NewDesignationId,
            'StaffPromotionHistory_NewDepartmentId': self.StaffPromotionHistory_NewDepartmentId,
            'StaffPromotionHistory_Date': self.StaffPromotionHistory_Date.isoformat() if self.StaffPromotionHistory_Date else None,
            'StaffPromotionHistory_Reason': self.StaffPromotionHistory_Reason,
            'StaffPromotionHistory_InitiatedBy': self.StaffPromotionHistory_InitiatedBy,
            'StaffPromotionHistory_ApprovedBy': self.StaffPromotionHistory_ApprovedBy,
            'StaffPromotionHistory_NewSalary': self.StaffPromotionHistory_NewSalary,
            'StaffPromotionHistory_NewSalaryEffectiveDate': self.StaffPromotionHistory_NewSalaryEffectiveDate.isoformat() if self.StaffPromotionHistory_NewSalaryEffectiveDate else None,
            'StaffPromotionHistory_Remarks': self.StaffPromotionHistory_Remarks,
            'StaffPromotionHistory_StaffPromotion_Id': self.StaffPromotionHistory_StaffPromotion_Id,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat() if self.CreatedDate else None,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class StaffPayrollHistory(db.Model):
    __tablename__ = 'StaffPayrollHistory'

    StaffPayrollHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StaffPayrollHistory_StaffPayrollId = db.Column(db.Integer, nullable=False)
    StaffPayrollHistory_StaffId = db.Column(db.Integer, nullable=False)
    StaffPayrollHistory_FromDate = db.Column(db.DateTime, nullable=False)
    StaffPayrollHistory_ToDate = db.Column(db.DateTime, nullable=False)
    StaffPayrollHistory_TotalDays = db.Column(db.Integer, nullable=False)
    StaffPayrollHistory_AbsentDays = db.Column(db.Integer, nullable=False)
    StaffPayrollHistory_PresentDays = db.Column(db.Integer, nullable=False)
    StaffPayrollHistory_LeaveDays = db.Column(db.Integer, nullable=False)
    StaffPayrollHistory_LateComingDays = db.Column(db.Numeric(18, 2))
    StaffPayrollHistory_Toil = db.Column(db.Numeric(18, 2))
    StaffPayrollHistory_EarlyGoingDays = db.Column(db.Numeric(18, 2))
    StaffPayrollHistory_RecommendedDeduction = db.Column(db.Numeric(18, 2))
    StaffPayrollHistory_CL = db.Column(db.Integer)
    StaffPayrollHistory_SL = db.Column(db.Integer)
    StaffPayrollHistory_EL = db.Column(db.Integer)
    StaffPayrollHistory_AL = db.Column(db.Integer)
    StaffPayrollHistory_SA = db.Column(db.Integer)
    StaffPayrollHistory_PatMat = db.Column(db.Integer)
    StaffPayrollHistory_Remarks = db.Column(db.String(500))
    StaffPayrollHistory_TotalAmount = db.Column(db.Integer, nullable=False)
    StaffPayrollHistory_ToilApprovedBy = db.Column(db.Integer)
    StaffPayroll_ProccessToHR = db.Column(db.Boolean)
    StaffPayroll_HRRemarks = db.Column(db.String(500))
    StaffPayroll_ProcessToFinance = db.Column(db.Boolean)
    StaffPayroll_FinanceRemarks = db.Column(db.String(500))
    StaffPayroll_MarkedDayOff = db.Column(db.Integer)
    CreatorId = db.Column(db.Integer, nullable=False)
    CreateDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdaterId = db.Column(db.Integer)
    UpdateDate = db.Column(db.DateTime)
    CampusId = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'StaffPayrollHistory_Id': self.StaffPayrollHistory_Id,
            'StaffPayrollHistory_StaffPayrollId': self.StaffPayrollHistory_StaffPayrollId,
            'StaffPayrollHistory_StaffId': self.StaffPayrollHistory_StaffId,
            'StaffPayrollHistory_FromDate': self.StaffPayrollHistory_FromDate.isoformat() if self.StaffPayrollHistory_FromDate else None,
            'StaffPayrollHistory_ToDate': self.StaffPayrollHistory_ToDate.isoformat() if self.StaffPayrollHistory_ToDate else None,
            'StaffPayrollHistory_TotalDays': self.StaffPayrollHistory_TotalDays,
            'StaffPayrollHistory_AbsentDays': self.StaffPayrollHistory_AbsentDays,
            'StaffPayrollHistory_PresentDays': self.StaffPayrollHistory_PresentDays,
            'StaffPayrollHistory_LeaveDays': self.StaffPayrollHistory_LeaveDays,
            'StaffPayrollHistory_LateComingDays': str(self.StaffPayrollHistory_LateComingDays) if self.StaffPayrollHistory_LateComingDays else None,
            'StaffPayrollHistory_Toil': str(self.StaffPayrollHistory_Toil) if self.StaffPayrollHistory_Toil else None,
            'StaffPayrollHistory_EarlyGoingDays': str(self.StaffPayrollHistory_EarlyGoingDays) if self.StaffPayrollHistory_EarlyGoingDays else None,
            'StaffPayrollHistory_RecommendedDeduction': str(self.StaffPayrollHistory_RecommendedDeduction) if self.StaffPayrollHistory_RecommendedDeduction else None,
            'StaffPayrollHistory_CL': self.StaffPayrollHistory_CL,
            'StaffPayrollHistory_SL': self.StaffPayrollHistory_SL,
            'StaffPayrollHistory_EL': self.StaffPayrollHistory_EL,
            'StaffPayrollHistory_AL': self.StaffPayrollHistory_AL,
            'StaffPayrollHistory_SA': self.StaffPayrollHistory_SA,
            'StaffPayrollHistory_PatMat': self.StaffPayrollHistory_PatMat,
            'StaffPayrollHistory_Remarks': self.StaffPayrollHistory_Remarks,
            'StaffPayrollHistory_TotalAmount': self.StaffPayrollHistory_TotalAmount,
            'StaffPayrollHistory_ToilApprovedBy': self.StaffPayrollHistory_ToilApprovedBy,
            'StaffPayroll_ProccessToHR': self.StaffPayroll_ProccessToHR,
            'StaffPayroll_HRRemarks': self.StaffPayroll_HRRemarks,
            'StaffPayroll_ProcessToFinance': self.StaffPayroll_ProcessToFinance,
            'StaffPayroll_FinanceRemarks': self.StaffPayroll_FinanceRemarks,
            'StaffPayroll_MarkedDayOff': self.StaffPayroll_MarkedDayOff,
            'CreatorId': self.CreatorId,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None,
            'UpdaterId': self.UpdaterId,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'CampusId': self.CampusId
        }

class StaffSeparationHistory(db.Model):
    __tablename__ = 'StaffSeparationHistory'

    StaffSeparationHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StaffSeparationHistory_StaffId = db.Column(db.Integer, nullable=False)
    StaffSeparationHistory_Type = db.Column(db.String(50), nullable=False)
    StaffSeparationHistory_Reason = db.Column(db.String(20), nullable=False)
    StaffSeparationHistory_Details = db.Column(db.String(200), nullable=False)
    StaffSeparationHistory_ReleventDocumentReceived = db.Column(db.Boolean, nullable=False)
    StaffSeparationHistory_ResignationDate = db.Column(db.DateTime, nullable=False)
    StaffSeparationHistory_LastWorkingDate = db.Column(db.DateTime, nullable=False)
    StaffSeparationHistory_NoticePeriod = db.Column(db.String(10), nullable=False)
    StaffSeparationHistory_ResignationApproved = db.Column(db.String(10), nullable=False)
    StaffSeparationHistory_SalaryHoldMonth = db.Column(db.String(20), nullable=False)
    StaffSeparationHistory_ClearanceDone = db.Column(db.Boolean, nullable=False)
    StaffSeparationHistory_ClearanceDate = db.Column(db.DateTime)
    StaffSeparationHistory_ExitInterview = db.Column(db.String(10), nullable=False)
    StaffSeparationHistory_ExitInterviewDate = db.Column(db.DateTime)
    StaffSeparationHistory_FinalSettlementDone = db.Column(db.String(10), nullable=False)
    StaffSeparationHistory_FinalSettlementDate = db.Column(db.DateTime)
    StaffSeparationHistory_StaffSeparation_Id = db.Column(db.Integer, nullable=False)
    CreatedBy = db.Column(db.Integer, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    UpdatedBy = db.Column(db.Integer)
    UpdatedDate = db.Column(db.DateTime)
    InActive = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'StaffSeparationHistory_Id': self.StaffSeparationHistory_Id,
            'StaffSeparationHistory_StaffId': self.StaffSeparationHistory_StaffId,
            'StaffSeparationHistory_Type': self.StaffSeparationHistory_Type,
            'StaffSeparationHistory_Reason': self.StaffSeparationHistory_Reason,
            'StaffSeparationHistory_Details': self.StaffSeparationHistory_Details,
            'StaffSeparationHistory_ReleventDocumentReceived': self.StaffSeparationHistory_ReleventDocumentReceived,
            'StaffSeparationHistory_ResignationDate': self.StaffSeparationHistory_ResignationDate.isoformat() if self.StaffSeparationHistory_ResignationDate else None,
            'StaffSeparationHistory_LastWorkingDate': self.StaffSeparationHistory_LastWorkingDate.isoformat() if self.StaffSeparationHistory_LastWorkingDate else None,
            'StaffSeparationHistory_NoticePeriod': self.StaffSeparationHistory_NoticePeriod,
            'StaffSeparationHistory_ResignationApproved': self.StaffSeparationHistory_ResignationApproved,
            'StaffSeparationHistory_SalaryHoldMonth': self.StaffSeparationHistory_SalaryHoldMonth,
            'StaffSeparationHistory_ClearanceDone': self.StaffSeparationHistory_ClearanceDone,
            'StaffSeparationHistory_ClearanceDate': self.StaffSeparationHistory_ClearanceDate.isoformat() if self.StaffSeparationHistory_ClearanceDate else None,
            'StaffSeparationHistory_ExitInterview': self.StaffSeparationHistory_ExitInterview,
            'StaffSeparationHistory_ExitInterviewDate': self.StaffSeparationHistory_ExitInterviewDate.isoformat() if self.StaffSeparationHistory_ExitInterviewDate else None,
            'StaffSeparationHistory_FinalSettlementDone': self.StaffSeparationHistory_FinalSettlementDone,
            'StaffSeparationHistory_FinalSettlementDate': self.StaffSeparationHistory_FinalSettlementDate.isoformat() if self.StaffSeparationHistory_FinalSettlementDate else None,
            'StaffSeparationHistory_StaffSeparation_Id': self.StaffSeparationHistory_StaffSeparation_Id,
            'CreatedBy': self.CreatedBy,
            'CreatedDate': self.CreatedDate.isoformat() if self.CreatedDate else None,
            'UpdatedBy': self.UpdatedBy,
            'UpdatedDate': self.UpdatedDate.isoformat() if self.UpdatedDate else None,
            'InActive': self.InActive
        }

class StudentFeeReceivingsDetailHistory(db.Model):
    __tablename__ = 'StudentFeeReceivingsDetailHistory'

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ChartOfAccountId = db.Column(db.Integer, nullable=False)
    Narration = db.Column(db.String(200), nullable=False)
    Amount = db.Column(db.Numeric(18, 2), nullable=False)
    CampusId = db.Column(db.Integer, nullable=False)
    StudentFeeReceivingsId = db.Column(db.Integer, nullable=False)
    InActive = db.Column(db.Boolean, nullable=True)

    def to_dict(self):
        return {
            'Id': self.Id,
            'ChartOfAccountId': self.ChartOfAccountId,
            'Narration': self.Narration,
            'Amount': float(self.Amount),
            'CampusId': self.CampusId,
            'StudentFeeReceivingsId': self.StudentFeeReceivingsId,
            'InActive': self.InActive
        }

class StudentFeeStructureDeletedHistory(db.Model):
    __tablename__ = 'StudentFeeStructureDeletedHistory'

    StudentFeeStructureDeletedHistory_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StudentFeeStructure_AlphaFeeStructureId = db.Column(db.Integer, nullable=False)
    StudentFeeStructure_ClassId = db.Column(db.Integer, nullable=False)
    StudentFeeStructure_StudentId = db.Column(db.Integer, nullable=False)
    StudentFeeStructure_Quantity = db.Column(db.Integer, nullable=False)
    StudentFeeStructure_FeeAmount = db.Column(db.Numeric(18, 2), nullable=False)
    StudentFeeStructure_TaxPercent = db.Column(db.Numeric(18, 2), nullable=True)
    StudentFeeStructure_TaxAmount = db.Column(db.Numeric(18, 2), nullable=True)
    StudentFeeStructure_DiscountPercent = db.Column(db.Numeric(18, 2), nullable=True)
    StudentFeeStructure_DiscountAmount = db.Column(db.Numeric(18, 2), nullable=True)
    StudentFeeStructure_IntervalMonth = db.Column(db.Integer, nullable=True)
    StudentFeeStructure_NetAmount = db.Column(db.Numeric(18, 2), nullable=True)
    StudentFeeStructure_Remarks = db.Column(db.String(100), nullable=True)
    StudentFeeStructure_DefaultChg = db.Column(db.Boolean, nullable=True)
    StudentFeeStructure_FeeCount = db.Column(db.Integer, nullable=True)
    StudentFeeStructure_StartDate = db.Column(db.DateTime, nullable=True)
    StudentFeeStructure_AccountId = db.Column(db.Integer, nullable=True)
    CampusId = db.Column(db.BigInteger, nullable=True)
    UpdaterId = db.Column(db.BigInteger, nullable=True)
    UpdaterIP = db.Column(db.String(20), nullable=True)
    UpdaterTerminal = db.Column(db.String(255), nullable=True)
    UpdateDate = db.Column(db.DateTime, nullable=True)
    CreatorId = db.Column(db.BigInteger, nullable=True)
    CreatorIP = db.Column(db.String(20), nullable=True)
    CreatorTerminal = db.Column(db.String(255), nullable=True)
    CreateDate = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'StudentFeeStructureDeletedHistory_Id': self.StudentFeeStructureDeletedHistory_Id,
            'StudentFeeStructure_AlphaFeeStructureId': self.StudentFeeStructure_AlphaFeeStructureId,
            'StudentFeeStructure_ClassId': self.StudentFeeStructure_ClassId,
            'StudentFeeStructure_StudentId': self.StudentFeeStructure_StudentId,
            'StudentFeeStructure_Quantity': self.StudentFeeStructure_Quantity,
            'StudentFeeStructure_FeeAmount': float(self.StudentFeeStructure_FeeAmount),
            'StudentFeeStructure_TaxPercent': float(self.StudentFeeStructure_TaxPercent) if self.StudentFeeStructure_TaxPercent else None,
            'StudentFeeStructure_TaxAmount': float(self.StudentFeeStructure_TaxAmount) if self.StudentFeeStructure_TaxAmount else None,
            'StudentFeeStructure_DiscountPercent': float(self.StudentFeeStructure_DiscountPercent) if self.StudentFeeStructure_DiscountPercent else None,
            'StudentFeeStructure_DiscountAmount': float(self.StudentFeeStructure_DiscountAmount) if self.StudentFeeStructure_DiscountAmount else None,
            'StudentFeeStructure_IntervalMonth': self.StudentFeeStructure_IntervalMonth,
            'StudentFeeStructure_NetAmount': float(self.StudentFeeStructure_NetAmount) if self.StudentFeeStructure_NetAmount else None,
            'StudentFeeStructure_Remarks': self.StudentFeeStructure_Remarks,
            'StudentFeeStructure_DefaultChg': self.StudentFeeStructure_DefaultChg,
            'StudentFeeStructure_FeeCount': self.StudentFeeStructure_FeeCount,
            'StudentFeeStructure_StartDate': self.StudentFeeStructure_StartDate.isoformat() if self.StudentFeeStructure_StartDate else None,
            'StudentFeeStructure_AccountId': self.StudentFeeStructure_AccountId,
            'CampusId': self.CampusId,
            'UpdaterId': self.UpdaterId,
            'UpdaterIP': self.UpdaterIP,
            'UpdaterTerminal': self.UpdaterTerminal,
            'UpdateDate': self.UpdateDate.isoformat() if self.UpdateDate else None,
            'CreatorId': self.CreatorId,
            'CreatorIP': self.CreatorIP,
            'CreatorTerminal': self.CreatorTerminal,
            'CreateDate': self.CreateDate.isoformat() if self.CreateDate else None
        }
























