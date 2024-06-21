from app import db
from datetime import datetime
import re
from exceptions import ValidationError

class JobApplicationForm(db.Model):
    __tablename__ = 'JobApplicationForms'

    id = db.Column(db.Integer, primary_key=True)
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
            'dob': self.dob.isoformat(),
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
        if not re.match(r'^(?!0+$)\d{11}$', phone_number):
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
