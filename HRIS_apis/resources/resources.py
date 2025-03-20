import base64
from flask_restful import Resource, reqparse, abort
from models.models import *
from datetime import datetime, date, timedelta
from app import db, mail
from flask import jsonify, request, Response
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import and_
from sqlalchemy import extract
from sqlalchemy.orm import joinedload
import json
from sqlalchemy.exc import SQLAlchemyError ,IntegrityError
from flask_mail import Message
from werkzeug.utils import secure_filename
import os
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from exceptions import *
from sqlalchemy import text, literal
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from resources.crypto_utils import encrypt, decrypt
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import ast
import uuid
import smtplib
import random
from email.mime.text import MIMEText


load_dotenv()

ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx']
UPLOAD_FOLDER = 'uploads/'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()

class JobApplicationFormResource(Resource):
    
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                return {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            columns = [
                {"field":"first_name", "headerName": "First Name", "width": width},
                {"field":"last_name", "headerName": "Last Name", "width": width},
                {"field":"father_name", "headerName": "Father's Name", "width": width},
                {"field":"cnic", "headerName": "CNIC", "width": width},
                {"field":"passport_number", "headerName": "Passport Number", "width": width},
                {"field":"dob", "headerName": "Date of Birth", "width": width},
                {"field":"age", "headerName": "Age", "width": width},
                {"field":"gender", "headerName": "Gender", "width": width},
                {"field":"cell_phone", "headerName": "Cell Phone", "width": width},
                {"field":"alternate_number", "headerName": "Alternate Number", "width": width},
                {"field":"email", "headerName": "Email Address", "width": width},
                {"field":"residence", "headerName": "Address", "width": width},
                {"field":"education_level", "headerName": "Education Level", "width": width},
                {"field":"education_level_others", "headerName": "Others", "width": width},
                {"field":"degree", "headerName": "Degree", "width": width},
                {"field":"specialization", "headerName": "Specialization", "width": width},
                {"field":"institute", "headerName": "Institute", "width": width},
                {"field":"fresh", "headerName": "Fresh", "width": width},
                {"field":"experienced", "headerName": "Experienced", "width": width},
                {"field":"total_years_of_experience", "headerName": "Total Years of Experience", "width": width},
                {"field":"name_of_last_employer", "headerName": "Name of Last Employer", "width": width},
                {"field":"employment_duration_from", "headerName": "Employment Duration: From", "width": width},
                {"field":"employment_duration_to", "headerName": "Employment Duration: To", "width": width},
                {"field":"designation", "headerName": "Designation", "width": width},
                {"field":"reason_for_leaving", "headerName": "Reason For Leaving(if already left)", "width": width},
                {"field":"last_drawn_gross_salary", "headerName": "Last Drawn Gross Salary", "width": width},
                {"field":"benefits_if_any", "headerName": "Benefits if any", "width": width},
                {"field":"preferred_campus", "headerName": "Preferred Campus", "width": width},
                {"field":"preferred_location", "headerName": "Preferred Location", "width": width},
                {"field":"preferred_job_type", "headerName": "Preferred Job Type", "width": width},
                {"field":"section", "headerName": "Section", "width": width},
                {"field":"subject", "headerName": "Subject", "width": width},
                {"field":"expected_salary", "headerName": "Expected Salary", "width": width},
                {"field":"cv_path", "headerName": "CV", "width": width},
                {"field":"coverLetter_Path", "headerName": "Cover Letter", "width": width}
            ]
            
            if id:
                job_application_form = JobApplicationForms.query.get_or_404(id)
                
                return {
                    "data": [job_application_form.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            else:
                query = JobApplicationForms.query.order_by(JobApplicationForms.Id)
                total = query.count()

                # Apply pagination
                job_application_forms = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [form.to_dict() for form in job_application_forms],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
                
        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    """
    def post(self):
        parser = reqparse.RequestParser()
        if request.content_type == 'multipart/form-data':
            parser.add_argument('Initial_id', required=False)
            parser.add_argument('First_name', required=True)
            parser.add_argument('Last_name', required=True)
            parser.add_argument('Father_name', required=True)
            parser.add_argument('Cnic', required=True)
            parser.add_argument('Passport_number')
            parser.add_argument('Dob', required=True)
            parser.add_argument('Age', required=True, type=str)
            parser.add_argument('Gender', required=True)
            parser.add_argument('Cell_phone', required=True)
            parser.add_argument('Alternate_number')
            parser.add_argument('Email', required=True)
            parser.add_argument('Residence', required=True)
            parser.add_argument('Education_level', required=True)
            parser.add_argument('Education_level_others')
            parser.add_argument('Degree', required=True)
            parser.add_argument('Specialization', required=True)
            parser.add_argument('Institute', required=True)
            parser.add_argument('Fresh', type=bool)
            parser.add_argument('Experienced', type=bool)
            parser.add_argument('Total_years_of_experience')
            parser.add_argument('Name_of_last_employer')
            parser.add_argument('Employment_duration_from')
            parser.add_argument('Employment_duration_to')
            parser.add_argument('Designation')
            parser.add_argument('Reason_for_leaving')
            parser.add_argument('Last_drawn_gross_salary')
            parser.add_argument('Benefits_if_any')
            parser.add_argument('JobApplied_For')
            parser.add_argument('Preferred_campus')
            parser.add_argument('Preferred_location')
            parser.add_argument('Preferred_job_type')
            parser.add_argument('Section')
            parser.add_argument('Subject')
            parser.add_argument('Expected_salary', required=True)
            parser.add_argument('Status', type=bool)
            args = parser.parse_args()

        try:
            # Handle file uploads
            if 'Cv_path' not in request.files or 'CoverLetter_Path' not in request.files:
                return {"error": "CV and Cover Letter files are required"}, 400
            
            cv_file = request.files['Cv_path']
            cover_letter_file = request.files['CoverLetter_Path']
            
            if cv_file.filename == '' or cover_letter_file.filename == '':
                return {"error": "No selected file"}, 400
            
            if cv_file and allowed_file(cv_file.filename):
                cv_filename = secure_filename(cv_file.filename)
                cv_path = os.path.join(app.config['UPLOAD_FOLDER'], cv_filename)
                cv_file.save(cv_path)
            else:
                return {"error": "CV file type not allowed"}, 400
            
            if cover_letter_file and allowed_file(cover_letter_file.filename):
                cover_letter_filename = secure_filename(cover_letter_file.filename)
                cover_letter_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_letter_filename)
                cover_letter_file.save(cover_letter_path)
            else:
                return {"error": "Cover Letter file type not allowed"}, 400

            employment_duration_from = datetime.strptime(args['Employment_duration_from'], '%Y-%m-%d') if args['Employment_duration_from'] else None
            employment_duration_to = datetime.strptime(args['Employment_duration_to'], '%Y-%m-%d') if args['Employment_duration_to'] else None

            job_application_form = JobApplicationForm(
                Initial_id=args['Initial_id'],
                First_name=args['First_name'],
                Last_name=args['Last_name'],
                Father_name=args['Father_name'],
                Cnic=args['Cnic'],
                Passport_number=args['Passport_number'],
                Dob=datetime.strptime(args['Dob'], '%Y-%m-%d'),
                Age=args['Age'],
                Gender=args['Gender'],
                Cell_phone=args['Cell_phone'],
                Alternate_number=args['Alternate_number'],
                Email=args['Email'],
                Residence=args['Residence'],
                Education_level=args['Education_level'],
                Education_level_others=args['Education_level_others'],
                Degree=args['Degree'],
                Specialization=args['Specialization'],
                Institute=args['Institute'],
                Fresh=args['Fresh'],
                Experienced=args['Experienced'],
                Total_years_of_experience=args['Total_years_of_experience'],
                Name_of_last_employer=args['Name_of_last_employer'],
                Employment_duration_from=employment_duration_from,
                Employment_duration_to=employment_duration_to,
                Designation=args['Designation'],
                Reason_for_leaving=args['Reason_for_leaving'],
                Last_drawn_gross_salary=args['Last_drawn_gross_salary'],
                Benefits_if_any=args['Benefits_if_any'],
                JobApplied_For=args['JobApplied_For'],
                Preferred_campus=args['Preferred_campus'],
                Preferred_location=args['Preferred_location'],
                Preferred_job_type=args['Preferred_job_type'],
                Section=args['Section'],
                Subject=args['Subject'],
                Expected_salary=args['Expected_salary'],
                Cv_path=cv_path,
                CoverLetter_Path=cover_letter_path,
                Status=args['Status']
            )

            db.session.add(job_application_form)
            db.session.commit()

            job_application_form = JobApplicationForm.query.get_or_404(job_application_form.Id)
            if not job_application_form:
                return {'message': 'New joiner approval record not found'}, 404

            job_application_form.Initial_id = str(args['Cnic']) + '-' + str(job_application_form.Id)
            db.session.commit()
            
            return {'message': f'Job application form created successfully {str(args["Cnic"])}-{str(job_application_form.Id)}'}, 201
        except ValueError as e:
            return {'error': 'Validation Error', 'message': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500
    """
    
    
    def post(self):
        
        # if 'Cv_path' not in request.files or 'CoverLetter_Path' not in request.files:
        #     return {"error": "CV and Cover Letter files are required"}, 400
        if 'Cv_path' not in request.files:
            return {"error": "CV file are required"}, 400

        cv_file = request.files['Cv_path']
        cover_letter_file = request.files['CoverLetter_Path']

        # if cv_file.filename == '' or cover_letter_file.filename == '':
            # return {"error": "No selected file"}, 400
        
        if cv_file.filename == '':
            return {"error": "No selected file"}, 400

        if cv_file and self.allowed_file(cv_file.filename):
            cv_filename = secure_filename(cv_file.filename)
            cv_path = os.path.join(UPLOAD_FOLDER, cv_filename)
            cv_file.save(cv_path)
        else:
            return {"status": "error",
                "message": "CV file type not allowed"}, 400

        if cover_letter_file and self.allowed_file(cover_letter_file.filename):
            cover_letter_filename = secure_filename(cover_letter_file.filename)
            cover_letter_path = os.path.join(UPLOAD_FOLDER, cover_letter_filename)
            cover_letter_file.save(cover_letter_path)
        # else:
        #     return {"status": "error"
        #         "message": "Cover Letter file type not allowed"}, 400

        # Parse JSON data from the 'data' field
        # Parse JSON data from the 'data' field
        try:
            data = json.loads(request.form.get('data'))
        except json.JSONDecodeError as e:
            return {"status": "error",
                "message": 'JSON Decode Error', 'message': str(e)}, 400
        
        try:
            employment_duration_from = datetime.strptime(data.get('Employment_duration_from'), '%Y-%m-%d') if data.get('Employment_duration_from') else None
            employment_duration_to = datetime.strptime(data.get('Employment_duration_to'), '%Y-%m-%d') if data.get('Employment_duration_to') else None

            job_application_form = JobApplicationForms(
                Initial_id=data.get('Initial_id'),
                First_name=data.get('First_name'),
                Last_name=data.get('Last_name'),
                Father_name=data.get('Father_name'),
                Cnic=data.get('Cnic'),
                Passport_number=data.get('Passport_number'),
                Dob=datetime.strptime(data.get('Dob'), '%Y-%m-%d'),
                Age=data.get('Age'),
                Gender=data.get('Gender'),
                Cell_phone=data.get('Cell_phone'),
                Alternate_number=data.get('Alternate_number'),
                Email=data.get('Email'),
                Residence=data.get('Residence'),
                Education_level=data.get('Education_level'),
                Education_level_others=data.get('Education_level_others'),
                Degree=data.get('Degree'),
                Specialization=data.get('Specialization'),
                Institute=data.get('Institute'),
                Fresh=data.get('Fresh'),
                Experienced=data.get('Experienced'),
                Total_years_of_experience=data.get('Total_years_of_experience'),
                Name_of_last_employer=data.get('Name_of_last_employer'),
                Employment_duration_from=employment_duration_from,
                Employment_duration_to=employment_duration_to,
                Designation=data.get('Designation'),
                Reason_for_leaving=data.get('Reason_for_leaving'),
                Last_drawn_gross_salary=data.get('Last_drawn_gross_salary'),
                Benefits_if_any=data.get('Benefits_if_any'),
                JobApplied_For=data.get('JobApplied_For'),
                Preferred_campus=data.get('Preferred_campus'),
                Preferred_location=data.get('Preferred_location'),
                Preferred_job_type=data.get('Preferred_job_type'),
                Section=data.get('Section'),
                Subject=data.get('Subject'),
                Expected_salary=data.get('Expected_salary'),
                Cv_path=cv_path,
                CoverLetter_Path=cover_letter_path,
                Status=data.get('Status')
            )

            db.session.add(job_application_form)
            db.session.commit()

            job_application_form = JobApplicationForms.query.get_or_404(job_application_form.Id)
            if not job_application_form:
                return {"status": "error",
                "message": 'New joiner approval record not found'}, 404

            job_application_form.Initial_id = str(data.get('Cnic')) + '-' + str(job_application_form.Id)
            db.session.commit()
            
            return {"status": "success",
                "message": f'Job application form created successfully {str(data["Cnic"])}-{str(job_application_form.Id)}'}, 201
        except ValueError as e:
            return {"status": "error",
                "message": 'Validation Error', 'message': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {"status": "error",
                "message": 'Internal Server Error', 'message': str(e)}, 500
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Initial_id')
        parser.add_argument('First_name')
        parser.add_argument('Last_name')
        parser.add_argument('Father_name')
        parser.add_argument('Cnic')
        parser.add_argument('Passport_number')
        parser.add_argument('Dob')
        parser.add_argument('Age', type=int)
        parser.add_argument('Gender')
        parser.add_argument('Cell_phone')
        parser.add_argument('Alternate_number')
        parser.add_argument('Email')
        parser.add_argument('Residence')
        parser.add_argument('Education_level')
        parser.add_argument('Education_level_others')
        parser.add_argument('Degree')
        parser.add_argument('Specialization')
        parser.add_argument('Institute')
        parser.add_argument('Fresh', type=bool)
        parser.add_argument('Experienced', type=bool)
        parser.add_argument('Total_years_of_experience')
        parser.add_argument('Name_of_last_employer')
        parser.add_argument('Employment_duration_from')
        parser.add_argument('Employment_duration_to')
        parser.add_argument('Designation')
        parser.add_argument('Reason_for_leaving')
        parser.add_argument('Last_drawn_gross_salary')
        parser.add_argument('Benefits_if_any')
        parser.add_argument('Preferred_campus')
        parser.add_argument('Preferred_location')
        parser.add_argument('Preferred_job_type')
        parser.add_argument('Section')
        parser.add_argument('Subject')
        parser.add_argument('Expected_salary')
        parser.add_argument('Cv_path')
        parser.add_argument('CoverLetter_Path')
        parser.add_argument('Status', type=bool)

        args = parser.parse_args()

        try:
            job_application_form = JobApplicationForms.query.get_or_404(id)

            # if args['Cell_phone'] and not JobApplicationForms.validate_phone_number(args['Cell_phone']):
            #     raise ValueError("Invalid phone number format.")
            # if args['Cnic'] and not JobApplicationForms.validate_cnic(args['Cnic']):
            #     raise ValueError("Invalid CNIC format.")
            # if args['Email'] and not JobApplicationForms.validate_email(args['Email']):
            #     raise ValueError("Invalid email format.")
            # if args['Passport_number'] and not JobApplicationForms.validate_passport_number(args['Passport_number']):
            #     raise ValueError("Invalid passport number format.")

            employment_duration_from = datetime.strptime(args['Employment_duration_from'], '%Y-%m-%d') if args['Employment_duration_from'] else None
            employment_duration_to = datetime.strptime(args['Employment_duration_to'], '%Y-%m-%d') if args['Employment_duration_to'] else None

            for key, value in args.items():
                if value is not None:
                    setattr(job_application_form, key, value)

            job_application_form.employment_duration_from = employment_duration_from
            job_application_form.employment_duration_to = employment_duration_to

            db.session.commit()
            return {'message': 'Job application form updated successfully'}, 200
        except ValueError as e:
            return {'error': 'Validation Error', 'message': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

    def delete(self, id):
        try:
            job_application_form = JobApplicationForms.query.get_or_404(id)
            db.session.delete(job_application_form)
            db.session.commit()
            return {'message': 'Job application form deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

class NewJoinerApprovalResource(Resource):
    def get(self, id=None):
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                return {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            columns = [
            {"fields": "NewJoinerApproval_StaffId", "headerName": "Staff ID", "width": width},
            {"fields": "NewJoinerApproval_Salary", "headerName": "Salary", "width": width},
            {"fields": "NewJoinerApproval_HiringApprovedBy", "headerName": "Hiring Approved By", "width": width},
            {"fields": "NewJoinerApproval_Remarks", "headerName": "Remarks", "width": width},
            {"fields": "NewJoinerApproval_FileVerified", "headerName": "File Verified", "width": width},
            {"fields": "NewJoinerApproval_EmpDetailsVerified", "headerName": "Employee Details Verified", "width": width},
            {"fields": "NewJoinerApproval_AddToPayrollMonth", "headerName": "Add to Payroll Month", "width": width},
        ]
            if id:
                new_joiner_approval = NewJoinerApproval.query.get_or_404(id)
                return {
                    "data": [new_joiner_approval.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            else:
                
                query = NewJoinerApproval.query.order_by(NewJoinerApproval.NewJoinerApproval_Id)
                total = query.count()

                # Apply pagination
                new_joiner_approvals = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [approval.to_dict() for approval in new_joiner_approvals],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200

        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        """
        Handles the creation of a new joiner approval record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('NewJoinerApproval_StaffId', type=int, required=True, help='Staff ID is required')
        parser.add_argument('NewJoinerApproval_Salary', type=float, required=True, help='Salary is required')
        parser.add_argument('NewJoinerApproval_HiringApprovedBy', type=int, required=True, help='Hiring approved by is required')
        parser.add_argument('NewJoinerApproval_Remarks', type=str, required=False)
        parser.add_argument('NewJoinerApproval_FileVerified', type=bool, required=True, help='File verified is required')
        parser.add_argument('NewJoinerApproval_EmpDetailsVerified', type=bool, required=True, help='Employee details verified is required')
        parser.add_argument('NewJoinerApproval_AddToPayrollMonth', type=str, required=True, help='Add to payroll month is required')
        parser.add_argument('CreatedBy', type=int, required=True, help='Creator ID is required')
        
        args = parser.parse_args()

        try:
            new_joiner_approval = NewJoinerApproval(
                NewJoinerApproval_StaffId=args['NewJoinerApproval_StaffId'],
                NewJoinerApproval_Salary=args['NewJoinerApproval_Salary'],
                NewJoinerApproval_HiringApprovedBy=args['NewJoinerApproval_HiringApprovedBy'],
                NewJoinerApproval_Remarks=args.get('NewJoinerApproval_Remarks'),
                NewJoinerApproval_FileVerified=args['NewJoinerApproval_FileVerified'],
                NewJoinerApproval_EmpDetailsVerified=args['NewJoinerApproval_EmpDetailsVerified'],
                NewJoinerApproval_AddToPayrollMonth=args['NewJoinerApproval_AddToPayrollMonth'],
                CreatedBy=args['CreatedBy'],
                CreatedDate=datetime.utcnow() + timedelta(hours=5)
            )

            db.session.add(new_joiner_approval)
            db.session.commit()
            
            # Create salary record for the new joiner
            self.create_employee_salary(new_joiner_approval.NewJoinerApproval_StaffId, new_joiner_approval.NewJoinerApproval_Salary)

            return {"message": "New joiner approval created successfully", "newJoinerApproval": new_joiner_approval.to_dict()}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, approval_id):
        
        """
        Handles updating an existing joiner approval record by its ID.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('NewJoinerApproval_Salary', type=float, required=False)
        parser.add_argument('NewJoinerApproval_HiringApprovedBy', type=int, required=False)
        parser.add_argument('NewJoinerApproval_Remarks', type=str, required=False)
        parser.add_argument('NewJoinerApproval_FileVerified', type=bool, required=False)
        parser.add_argument('NewJoinerApproval_EmpDetailsVerified', type=bool, required=False)
        parser.add_argument('NewJoinerApproval_AddToPayrollMonth', type=str, required=False)
        parser.add_argument('UpdatedBy', type=int, required=True, help='Updater ID is required')
        
        args = parser.parse_args()

        try:
            new_joiner_approval = NewJoinerApproval.query.get(approval_id)
            if not new_joiner_approval:
                return {'message': 'New joiner approval record not found'}, 404
            
            try:
                new_joiner_approval_history = NewJoinerApprovalHistory(
                    NewJoinerApprovalHistory_NewJoinerApprovalId = approval_id,
                    NewJoinerApprovalHistory_StaffId= new_joiner_approval.NewJoinerApproval_StaffId,
                    NewJoinerApprovalHistory_Salary= new_joiner_approval.NewJoinerApproval_Salary,
                    NewJoinerApprovalHistory_HiringApprovedBy= new_joiner_approval.NewJoinerApproval_HiringApprovedBy,
                    NewJoinerApprovalHistory_Remarks= new_joiner_approval.NewJoinerApproval_Remarks,
                    NewJoinerApprovalHistory_FileVerified= new_joiner_approval.NewJoinerApproval_FileVerified,
                    NewJoinerApprovalHistory_EmpDetailsVerified= new_joiner_approval.NewJoinerApproval_EmpDetailsVerified,
                    NewJoinerApprovalHistory_AddToPayrollMonth= new_joiner_approval.NewJoinerApproval_AddToPayrollMonth,
                    CreatedBy= new_joiner_approval.CreatedBy,
                    CreatedDate= new_joiner_approval.CreatedDate,
                    UpdatedBy = args['UpdatedBy'],
                    UpdatedDate = datetime.utcnow() + timedelta(hours=5),
                    InActive = 0
                )

                db.session.add(new_joiner_approval_history)
                db.session.commit()
                
            except SQLAlchemyError as e:
                db.session.rollback()
                return {'error': f"Database error occurred: {str(e)}"}, 500
            except Exception as e:
                db.session.rollback()
                return {'error': f"An unexpected error occurred: {str(e)}"}, 500

            for key, value in args.items():
                if value is not None:
                    setattr(new_joiner_approval, key, value)

            new_joiner_approval.updatedBy = args['UpdatedBy']
            new_joiner_approval.updatedDate = datetime.utcnow() + timedelta(hours=5)

            db.session.commit()

            # Update the corresponding salary record
            self.update_employee_salary(new_joiner_approval.NewJoinerApproval_StaffId, new_joiner_approval.NewJoinerApproval_Salary)

            return {"message": "New joiner approval updated successfully", "newJoinerApproval": new_joiner_approval.to_dict()}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def create_employee_salary(self, staff_id, total_salary):
        """
        Creates a new salary record for the given staff ID.
        """
        try:
            staff_info = StaffInfo.query.get(staff_id)
            if not staff_info:
                return

            is_non_teacher = staff_info.IsNonTeacher
            basic = total_salary / 2

            new_salary = Salaries(
                BasicAmount=basic,
                AllowancesAmount=basic,
                TotalAmount=total_salary,
                AnnualLeaves=10,
                RemainingAnnualLeaves=10,
                DailyHours=8,
                PFAmount=basic / 12,
                EOBIAmount=basic / 12,
                SESSIAmount=basic / 12,
                SalaryMode=1,
                IsProbationPeriod=False,
                From=datetime.utcnow() + timedelta(hours=5),
                To=datetime.utcnow() + timedelta(hours=5),
                EmployeeId=staff_id,
                CreatedOn=datetime.utcnow() + timedelta(hours=5),
                CreatedByUserId=get_jwt_identity(),
                HouseRent=basic / 2,
                MedicalAllowance=basic / 10,
                UtilityAllowance=basic / 5,
                IncomeTax=0,
                Toil=0,
                ConveyanceAllowance=basic / 5,
                StaffLunch=0,
                CasualLeaves=12 if is_non_teacher else 10,
                SickLeaves=7,
                RemainingCasualLeaves=12 if is_non_teacher else 10,
                RemainingSickLeaves=7,
                StudyLeaves=5,
                RemainingStudyLeaves=5,
                Loan=0,
                Arrears=0
            )

            db.session.add(new_salary)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating employee salary: {str(e)}")

    def update_employee_salary(self, staff_id, total_salary):
        """
        Updates the existing active salary record for the given staff ID.
        """
        try:
            salary = Salaries.query.filter_by(EmployeeId=staff_id, IsActive=True).first()
            if not salary:
                return

            staff_info = StaffInfo.query.get(staff_id)
            if not staff_info:
                return

            is_non_teacher = staff_info.IsNonTeacher
            basic = total_salary / 2

            salary.BasicAmount = basic
            salary.AllowancesAmount = basic
            salary.TotalAmount = total_salary
            salary.PFAmount = basic / 12
            salary.EOBIAmount = basic / 12
            salary.SESSIAmount = basic / 12
            salary.From = datetime.utcnow() + timedelta(hours=5)
            salary.To = datetime.utcnow() + timedelta(hours=5)
            salary.HouseRent = basic / 2
            salary.MedicalAllowance = basic / 10
            salary.UtilityAllowance = basic / 5
            salary.ConveyanceAllowance = basic / 5
            salary.UpdatedOn = datetime.utcnow() + timedelta(hours=5)
            salary.UpdatedByUserId = get_jwt_identity()

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error updating employee salary: {str(e)}")
    
    def delete(self, id):
        try:
            new_joiner_approval = NewJoinerApproval.query.get_or_404(id)
            db.session.delete(new_joiner_approval)
            db.session.commit()
            return {'message': 'New joiner approval deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

class InterviewSchedulesResource(Resource):
    
    def get(self, id=None):
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            columns = [
                {"field":'Interview_type_id', "headerName": "Interview Type ID", "width": width},
                {"field":'Date', "headerName": "Date", "width": width},
                {"field":'Time', "headerName": "Time", "width": width},
                {"field":'Venue', "headerName": "Venue", "width": width},
                {"field":'Job_application_form_id', "headerName": "Job Application Form Id", "width": width},
                {"field":'Interview_conductor_id', "headerName": "Interview Conductor Id", "width": width},
                {"field":'Demo_topic', "headerName": "Demo Topic", "width": width},
                {"field":'Position', "headerName": "Position", "width": width},
                {"field":'Location', "headerName": "Location", "width": width},
                {"field":'Created_by', "headerName": "Created By", "width": width},
                {"field":'Create_date', "headerName": "Created Date", "width": width},
                {"field":'Campus_id', "headerName": "Campus Id", "width": width}
            ]
            
            if id is None:
                
                query = InterviewSchedules.query.order_by(InterviewSchedules.Id)
                total = query.count()

                # Apply pagination
                interviews = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [interview.to_dict() for interview in interviews],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
                
            else:
                interview = InterviewSchedules.query.get(id)
                if interview is None:
                    abort(404, message=f"Interview schedule {id} doesn't exist")
                
                interview = interview.to_dict()
                return {
                    "data": [interview.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200

        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('InterviewTypeId', type=int, required=True, help="Interview type ID is required")
        parser.add_argument('Date', type=str, required=False)
        parser.add_argument('Time', type=str, required=False)
        parser.add_argument('Venue', type=str, required=False)
        parser.add_argument('JobApplicationFormId', type=int, required=False)
        parser.add_argument('InterviewConductorId', type=str, required=False)
        parser.add_argument('DemoTopic', type=str, required=False)
        parser.add_argument('Position', type=str, required=False)
        parser.add_argument('Location', type=str, required=False)
        parser.add_argument('CreatedBy', type=int, required=False)
        parser.add_argument('CreateDate', type=str, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        args = parser.parse_args()

        
        # Parse Date (with both date and time in the string)
        Date = datetime.strptime(args['Date'], '%Y-%m-%d %H:%M:%S') if args['Date'] else None

        # Parse Time correctly using only time format
        Time = datetime.strptime(args['Time'], '%H:%M:%S').time() if args['Time'] else None
        
        print(Date, Time)
        
        try:
            new_schedule = InterviewSchedules(
                InterviewTypeId=args['InterviewTypeId'],
                Date=Date,
                Time=Time,
                Venue=args['Venue'],
                JobApplicationFormId=args['JobApplicationFormId'],
                InterviewConductorId=args['InterviewConductorId'],
                DemoTopic=args['DemoTopic'],
                Position=args['Position'],
                Location=args['Location'],
                CreatedBy=args['CreatedBy'],
                CreateDate=datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S') if args['CreateDate'] else datetime.utcnow() + timedelta(hours=5),
                CampusId=args['CampusId']
            )
            db.session.add(new_schedule)
            db.session.commit()
            return {"message": "Interview schedule created", "id": new_schedule.Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating interview schedule: {str(e)}")
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('InterviewTypeId', type=int, required=False)
        parser.add_argument('Date', type=str, required=False)
        parser.add_argument('Time', type=str, required=False)
        parser.add_argument('Venue', type=str, required=False)
        parser.add_argument('JobApplicationFormId', type=int, required=False)
        parser.add_argument('InterviewConductorId', type=str, required=False)
        parser.add_argument('DemoTopic', type=str, required=False)
        parser.add_argument('Position', type=str, required=False)
        parser.add_argument('Location', type=str, required=False)
        parser.add_argument('CreatedBy', type=int, required=False)
        parser.add_argument('CreateDate', type=str, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        args = parser.parse_args()

        schedule = InterviewSchedules.query.get(id)
        if schedule is None:
            abort(404, message=f"Interview schedule {id} doesn't exist")

        try:
            if args['InterviewTypeId'] is not None:
                schedule.InterviewTypeId = args['InterviewTypeId']
            if args['Date']:
                schedule.Date = datetime.strptime(args['Date'], '%Y-%m-%d')
            if args['Time']:
                schedule.Time = datetime.strptime(args['Time'], '%H:%M:%S').time()
            if args['Venue']:
                schedule.Venue = args['Venue']
            if args['JobApplicationFormId'] is not None:
                schedule.JobApplicationFormId = args['JobApplicationFormId']
            if args['InterviewConductorId']:
                schedule.InterviewConductorId = args['InterviewConductorId']
            if args['DemoTopic']:
                schedule.DemoTopic = args['DemoTopic']
            if args['Position']:
                schedule.Position = args['Position']
            if args['Location']:
                schedule.Location = args['Location']
            if args['CreatedBy'] is not None:
                schedule.CreatedBy = args['CreatedBy']
            if args['CreateDate']:
                schedule.CreateDate = datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S')
            if args['CampusId'] is not None:
                schedule.CampusId = args['CampusId']
            
            db.session.commit()
            return {"message": "Interview schedule updated", "id": schedule.Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating interview schedule: {str(e)}")
    
    def delete(self, id):
        schedule = InterviewSchedules.query.get(id)
        if schedule is None:
            abort(404, message=f"Interview schedule {id} doesn't exist")

        try:
            db.session.delete(schedule)
            db.session.commit()
            return {"message": "Interview schedule deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting interview schedule: {str(e)}")

class DeductionHeadResource(Resource):
    def get(self, id=None):

        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            columns = [
                {"field": "DeductionHead_Id", "headerName": "Deduction Head Id", "width": width},
                {"field": "DeductionHead_Name", "headerName": "Deduction Head Name", "width": width}
            ]
            
            if id is None:
                query = DeductionHead.query.order_by(DeductionHead.DeductionHead_Id)
                total = query.count()

                # Apply pagination
                deductionHeads = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [deductionHead.to_dict() for deductionHead in deductionHeads],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200

            else:
                deductionHeads = DeductionHead.query.get(id)
                if deductionHeads is None:
                    abort(404, message=f"deductionHeads {id} doesn't exist")
                
                deductionHeads = deductionHeads.to_dict()
                return {
                    "data": [deductionHeads.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200

        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('DeductionHead_Name', type=str, required=True, help="Deduction head name is required")
        args = parser.parse_args()

        try:
            new_head = DeductionHead(DeductionHead_Name=args['DeductionHead_Name'])
            db.session.add(new_head)
            db.session.commit()
            return {"message": "Deduction head created", "id": new_head.DeductionHead_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating deduction head: {str(e)}")
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('DeductionHead_Name', type=str, required=True, help="Deduction head name is required")
        args = parser.parse_args()

        head = DeductionHead.query.get(id)
        if head is None:
            abort(404, message=f"DeductionHead {id} doesn't exist")

        try:
            head.DeductionHead_Name = args['DeductionHead_Name']
            db.session.commit()
            return {"message": "Deduction head updated", "id": head.DeductionHead_Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating deduction head: {str(e)}")
    
    def delete(self, id):
        head = DeductionHead.query.get(id)
        if head is None:
            abort(404, message=f"DeductionHead {id} doesn't exist")

        try:
            db.session.delete(head)
            db.session.commit()
            return {"message": "Deduction head deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting deduction head: {str(e)}")

class OneTimeDeductionResource(Resource):
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
        
            columns = [
                {"field":"OneTimeDeduction_Id", "headername": "Id", "width": width},
                {"field":"OneTimeDeduction_StaffId", "headername": "Staff Id", "width": width},
                {"field":"OneTimeDeduction_DeductionHeadId", "headername": "Deduction Head Id", "width": width},
                {"field":"OneTimeDeduction_Amount", "headername": "Amount", "width": width},
                {"field":"OneTimeDeduction_DeductionMonth", "headername": "Deduction Month", "width": width},
                {"field":"OneTimeDeduction_ApprovedBy", "headername": "Approved By", "width": width},
                {"field":"CreatorId", "headername": "Creator Id", "width": width},
                {"field":"CeateDate", "headername": "Created Date", "width": width},
                {"field":"UdatorId", "headername": "Updator Id", "width": width},
                {"field":"UpdateDate", "headername": "Updated Date", "width": width},
                {"field":"InActive", "headername": "In active", "width": width}
            ]

            if id is None:
                
                query = OneTimeDeduction.query.order_by(OneTimeDeduction.OneTimeDeduction_Id)
                total = query.count()

                # Apply pagination
                oneTimeDeductions = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [oneTimeDeduction.to_dict() for oneTimeDeduction in oneTimeDeductions],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200

            else:
                oneTimeDeductions = OneTimeDeduction.query.get(id)
                if oneTimeDeductions is None:
                    abort(404, message=f"Interview schedule {id} doesn't exist")
                
                return {
                    "data": [oneTimeDeductions.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200

        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('OneTimeDeduction_StaffId', type=int, required=True, help="Staff ID is required")
        parser.add_argument('OneTimeDeduction_DeductionHeadId', type=int, required=True, help="Deduction head ID is required")
        parser.add_argument('OneTimeDeduction_Amount', type=float, required=True, help="Amount is required")
        parser.add_argument('OneTimeDeduction_DeductionMonth', type=str, required=True, help="Deduction month is required")
        parser.add_argument('OneTimeDeduction_ApprovedBy', type=int, required=True, help="Approved by is required")
        parser.add_argument('CreatorId', type=int, required=True, help="Creator ID is required")
        args = parser.parse_args()

        try:
            new_deduction = OneTimeDeduction(
                OneTimeDeduction_StaffId=args['OneTimeDeduction_StaffId'],
                OneTimeDeduction_DeductionHeadId=args['OneTimeDeduction_DeductionHeadId'],
                OneTimeDeduction_Amount=args['OneTimeDeduction_Amount'],
                OneTimeDeduction_DeductionMonth=args['OneTimeDeduction_DeductionMonth'],
                OneTimeDeduction_ApprovedBy=args['OneTimeDeduction_ApprovedBy'],
                CreatorId=args['CreatorId'],
                CreateDate=datetime.utcnow() + timedelta(hours=5),
                InActive = 0
            )
            db.session.add(new_deduction)
            db.session.commit()
            return {"message": "One-time deduction created", "id": new_deduction.OneTimeDeduction_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating one-time deduction: {str(e)}")
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('OneTimeDeduction_Id', type=int, required=False)
        parser.add_argument('OneTimeDeduction_DeductionHeadId', type=int, required=False)
        parser.add_argument('OneTimeDeduction_Amount', type=float, required=False)
        parser.add_argument('OneTimeDeduction_DeductionMonth', type=str, required=False)
        parser.add_argument('OneTimeDeduction_ApprovedBy', type=int, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreateDate', type=str, required=False)
        parser.add_argument('UpdatorId', type=int, required=False)
        parser.add_argument('UpdateDate', type=str, required=False)
        parser.add_argument('InActive', type=bool, required=False)
        args = parser.parse_args()

        deduction = OneTimeDeduction.query.get(id)
        if deduction is None:
            abort(404, message=f"OneTimeDeduction {id} doesn't exist")
        
        try:
            new_deduction_history = OneTimeDeductionHistory(
                OneTimeDeductionHistory_OneTimeDeduction_Id = args['OneTimeDeduction_Id'],
                OneTimeDeductionHistory_StaffId=deduction.OneTimeDeduction_StaffId,
                OneTimeDeductionHistory_DeductionHeadId=deduction.OneTimeDeduction_DeductionHeadId,
                OneTimeDeductionHistory_Amount=deduction.OneTimeDeduction_Amount,
                OneTimeDeductionHistory_DeductionMonth=deduction.OneTimeDeduction_DeductionMonth,
                OneTimeDeductionHistory_ApprovedBy=deduction.OneTimeDeduction_ApprovedBy,
                CreatorId=deduction.CreatorId,
                CreateDate=deduction.CreateDate,
                UpdatorId = args['UpdatorId'],
                UpdateDate = datetime.utcnow() + timedelta(hours=5),
                InActive = 0
            )
            db.session.add(new_deduction_history)
            db.session.commit()
            # return {"message": "One-time deduction History created", "id": new_deduction.OneTimeDeduction_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating one-time deduction: {str(e)}")
        
        try:
            if args['OneTimeDeduction_StaffId'] is not None:
                deduction.OneTimeDeduction_StaffId = args['OneTimeDeduction_StaffId']
            if args['OneTimeDeduction_DeductionHeadId'] is not None:
                deduction.OneTimeDeduction_DeductionHeadId = args['OneTimeDeduction_DeductionHeadId']
            if args['OneTimeDeduction_Amount'] is not None:
                deduction.OneTimeDeduction_Amount = args['OneTimeDeduction_Amount']
            if args['OneTimeDeduction_DeductionMonth']:
                deduction.OneTimeDeduction_DeductionMonth = args['OneTimeDeduction_DeductionMonth']
            if args['OneTimeDeduction_ApprovedBy'] is not None:
                deduction.OneTimeDeduction_ApprovedBy = args['OneTimeDeduction_ApprovedBy']
            if args['CreatorId'] is not None:
                deduction.CreatorId = args['CreatorId']
            if args['CreateDate']:
                deduction.CreateDate = datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S')
            if args['UpdatorId'] is not None:
                deduction.UpdatorId = args['UpdatorId']
            if args['UpdateDate']:
                deduction.UpdateDate = datetime.strptime(args['UpdateDate'], '%Y-%m-%d %H:%M:%S')
            if args['InActive'] is not None:
                deduction.InActive = args['InActive']

            db.session.commit()
            return {"message": "One-time deduction updated", "id": deduction.OneTimeDeduction_Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating one-time deduction: {str(e)}")
    
    def delete(self, id):
        deduction = OneTimeDeduction.query.get(id)
        if deduction is None:
            abort(404, message=f"OneTimeDeduction {id} doesn't exist")

        try:
            db.session.delete(deduction)
            db.session.commit()
            return {"message": "One-time deduction deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting one-time deduction: {str(e)}")

class ScheduledDeductionResource(Resource):
    
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            columns = [
                {"field":"ScheduledDeduction_Id", "headerName": "Id", "width": width},
                {"field":"ScheduledDeduction_StaffId", "headerName": "Staff Id", "width": width},
                {"field":"ScheduledDeduction_DeductionHeadId", "headerName": "Deduction head Id", "width": width},
                {"field":"ScheduledDeduction_AmountPerMonth", "headerName": "Amount Per Month", "width": width},
                {"field":"ScheduledDeduction_StartDate", "headerName": "Start Date", "width": width},
                {"field":"ScheduledDeduction_EndDate", "headerName": "End Date", "width": width},
                {"field":"ScheduledDeduction_ApprovedBy", "headerName": "Approved By", "width": width},
                {"field":"CreatorId", "headerName": "Creator Id", "width": width},
                {"field":"CreateDate", "headerName": "Created Date", "width": width},
                {"field":"UpdatorId", "headerName": "Updator Id", "width": width},
                {"field":"UpdateDate", "headerName": "Updated Date", "width": width},
                {"field":"InActive", "headerName": "In Active", "width": width}
            ]
            
            # if id is None:
            if id:
                
                deduction = ScheduledDeduction.query.get(id)
                if deduction is None:
                    abort(404, message=f"Interview schedule {id} doesn't exist")
                
                return {
                    "data": [deduction.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
                
            else:

                query = ScheduledDeduction.query.order_by(ScheduledDeduction.ScheduledDeduction_Id)
                total = query.count()

                # Apply pagination
                deductions = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [deduction.to_dict() for deduction in deductions],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
                
        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ScheduledDeduction_StaffId', type=int, required=True, help="Staff ID is required")
        parser.add_argument('ScheduledDeduction_DeductionHeadId', type=int, required=True, help="Deduction Head ID is required")
        parser.add_argument('ScheduledDeduction_AmountPerMonth', type=float, required=True, help="Amount Per Month is required")
        parser.add_argument('ScheduledDeduction_StartDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help="Start Date is required and must be in ISO format")
        parser.add_argument('ScheduledDeduction_EndDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help="End Date is required and must be in ISO format")
        parser.add_argument('ScheduledDeduction_ApprovedBy', type=int, required=True, help="Approved By is required")
        parser.add_argument('CreatorId', type=int, required=True, help="Creator ID is required")
        
        args = parser.parse_args()

        new_deduction = ScheduledDeduction(
            ScheduledDeduction_StaffId=args['ScheduledDeduction_StaffId'],
            ScheduledDeduction_DeductionHeadId=args['ScheduledDeduction_DeductionHeadId'],
            ScheduledDeduction_AmountPerMonth=args['ScheduledDeduction_AmountPerMonth'],
            ScheduledDeduction_StartDate=args['ScheduledDeduction_StartDate'],
            ScheduledDeduction_EndDate=args['ScheduledDeduction_EndDate'],
            ScheduledDeduction_ApprovedBy=args['ScheduledDeduction_ApprovedBy'],
            CreatorId=args['CreatorId'],
            CreateDate = datetime.utcnow() + timedelta(hours=5),
            InActive = 0
        )

        try:
            db.session.add(new_deduction)
            db.session.commit()
            return {"message": "Scheduled deduction created", "id": new_deduction.ScheduledDeduction_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating scheduled deduction: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('ScheduledDeduction_StaffId', type=int, required=False)
        parser.add_argument('ScheduledDeduction_DeductionHeadId', type=int, required=False)
        parser.add_argument('ScheduledDeduction_AmountPerMonth', type=float, required=False)
        parser.add_argument('ScheduledDeduction_StartDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('ScheduledDeduction_EndDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('ScheduledDeduction_ApprovedBy', type=int, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('UpdatorId', type=int, required=False)
        parser.add_argument('UpdateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('InActive', type=bool, required=False)
        args = parser.parse_args()

        deduction = ScheduledDeduction.query.get(id)
        if not deduction:
            abort(404, message=f"Scheduled Deduction {id} does not exist")

        try:
            if args.get('ScheduledDeduction_StaffId') is not None:
                deduction.ScheduledDeduction_StaffId = args['ScheduledDeduction_StaffId']
            if args.get('ScheduledDeduction_DeductionHeadId') is not None:
                deduction.ScheduledDeduction_DeductionHeadId = args['ScheduledDeduction_DeductionHeadId']
            if args.get('ScheduledDeduction_AmountPerMonth') is not None:
                deduction.ScheduledDeduction_AmountPerMonth = args['ScheduledDeduction_AmountPerMonth']
            if args.get('ScheduledDeduction_StartDate') is not None:
                deduction.ScheduledDeduction_StartDate = args['ScheduledDeduction_StartDate']
            if args.get('ScheduledDeduction_EndDate') is not None:
                deduction.ScheduledDeduction_EndDate = args['ScheduledDeduction_EndDate']
            if args.get('ScheduledDeduction_ApprovedBy') is not None:
                deduction.ScheduledDeduction_ApprovedBy = args['ScheduledDeduction_ApprovedBy']
            if args.get('CreatorId') is not None:
                deduction.CreatorId = args['CreatorId']
            if args.get('UpdatorId') is not None:
                deduction.UpdatorId = args['UpdatorId']
            
            deduction.UpdateDate = datetime.utcnow() + timedelta(hours=5)
            if args.get('InActive') is not None:
                deduction.InActive = args['InActive']

            db.session.commit()
            return {"message": "Scheduled deduction updated", "id": deduction.ScheduledDeduction_Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating scheduled deduction: {str(e)}")

    def delete(self, id):
        deduction = ScheduledDeduction.query.get(id)
        if not deduction:
            abort(404, message=f"Scheduled Deduction {id} does not exist")

        try:
            db.session.delete(deduction)
            db.session.commit()
            return {"message": "Scheduled deduction deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting scheduled deduction: {str(e)}")

class IARResource(Resource):
    
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
        
            columns = [
                {"field":"id", "headerName": "id", "width": width},
                {"field":"form_Id", "headerName": "Form Id", "width": width},
                {"field":"IAR_Type_Id", "headerName": "IAR Type Id", "width": width},
                {"field":"status_Check", "headerName": "Status Check", "width": width},
                {"field":"remarks", "headerName": "Remarks", "width": width},
                {"field":"creatorId", "headerName": "Creator Id", "width": width},
                {"field":"createdDate", "headerName": "Created Date", "width": width}
            ]
            
            if id:
                
                iar = IAR.query.get(id)
                if iar is None:
                    abort(404, message=f"IAR {id} doesn't exist")
                
                return {
                    "data": [iar.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            else:
                query = IAR.query.order_by(IAR.Id)
                total = query.count()

                # Apply pagination
                iars = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [iar.to_dict() for iar in iars],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
                
        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500
                
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Form_Id', type=int, required=True, help="Form ID is required")
        parser.add_argument('IAR_Type_Id', type=int, required=True, help="IAR Type ID is required")
        parser.add_argument('Status_Check', type=bool, required=True, help="Status Check is required")
        parser.add_argument('Remarks', type=str, required=True, help="Remarks are required")
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatedDate', type=str, required=False)
        args = parser.parse_args()

            
        try:
            form_exists = IAR.query.filter_by(Form_Id=args['Form_Id'], IAR_Type_Id = args['IAR_Type_Id']).first()
            if form_exists:
                # form_exists.IAR_Type_Id = args['IAR_Type_Id']
                form_exists.Status_Check = args['Status_Check']
                form_exists.Remarks = args['Remarks']
                form_exists.CreatorId = args['CreatorId']
                form_exists.CreatedDate = args['CreatedDate']
            
            else:
                new_iar = IAR(
                    Form_Id=args['Form_Id'],
                    IAR_Type_Id=args['IAR_Type_Id'],
                    Status_Check=args['Status_Check'],
                    Remarks=args['Remarks'],
                    CreatorId=args['CreatorId'],
                    CreatedDate=datetime.utcnow() + timedelta(hours=5)
                )
            
            # Start a database transaction
            with db.session.begin_nested():
                if form_exists:
                    self.updateRemarks(form_exists.Id, args)
                else:
                    db.session.add(new_iar)
                    db.session.flush()
                    self.updateRemarks(new_iar.Id, args)
                    
            db.session.commit()
            
            return {"status": "success",
                    "message": "IAR created and related tables updated successfully"}, 201
        except (ValueError, TypeError) as ve:
            db.session.rollback()
            return {"error": str(ve)}, 400
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error creating IAR: {str(e)}"}, 400

    def updateRemarks(self, new_iar_id, args):
        try:
            new_remark = IAR_Remarks(
                IAR_Id=new_iar_id,
                Remarks=args['Remarks'],
                Status=args['Status_Check'],
                CreatorId=args['CreatorId'],
                CreateDate=datetime.utcnow() + timedelta(hours=5)
            )
            
            db.session.add(new_remark)
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating IAR_Remarks: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Form_Id', type=int, required=False)
        parser.add_argument('IAR_Type_Id', type=int, required=False)
        parser.add_argument('Status_Check', type=bool, required=False)
        parser.add_argument('Remarks', type=str, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatedDate', type=str, required=False)
        args = parser.parse_args()

        iar = IAR.query.get(id)
        if iar is None:
            abort(404, message=f"IAR {id} doesn't exist")

        try:
            if args['Form_Id'] is not None:
                iar.form_Id = args['form_Id']
            if args['IAR_Type_Id'] is not None:
                iar.IAR_Type_Id = args['IAR_Type_Id']
            if args['Status_Check'] is not None:
                iar.Status_Check = args['Status_Check']
            if args['Remarks'] is not None:
                iar.Remarks = args['Remarks']
            if args['CreatorId'] is not None:
                iar.CreatorId = args['CreatorId']
            if args['CreatedDate']:
                iar.CreatedDate = datetime.strptime(args['CreatedDate'], '%Y-%m-%d %H:%M:%S')

            db.session.commit()
            try:
                new_remark = IAR_Remarks(
                    IAR_Id=iar.Id,
                    remarks=args['Remarks'],
                    status=args['Status_Check'],
                    creatorId=args.get('CreatorId'),
                    createDate=datetime.utcnow() + timedelta(hours=5)
                )
                db.session.add(new_remark)
                db.session.commit()
                return {"message": "IAR_Remarks created", "id": new_remark.id}, 201
            except Exception as e:
                db.session.rollback()
                abort(400, message=f"Error creating IAR_Remarks: {str(e)}")
                
            return {"message": "IAR updated", "id": iar.Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating IAR: {str(e)}")

    def delete(self, id):
        iar = IAR.query.get(id)
        if iar is None:
            abort(404, message=f"IAR {id} doesn't exist")

        try:
            # Delete related IAR_Remarks entries first
            IAR_Remarks.query.filter_by(IAR_Id=id).delete()
            
            db.session.delete(iar)
            db.session.commit()
            return {"message": "IAR deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting IAR: {str(e)}")

class IARRemarksResource(Resource):
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
        
            columns = [
                {"field":"id", "headerName": "id", "width": width},
                {"field":"IAR_Id", "headerName": "IAR id", "width": width},
                {"field":"remarks", "headerName": "Remarks", "width": width},
                {"field":"status", "headerName": "Status", "width": width},
                {"field":"creatorId", "headerName": "Creator Id", "width": width},
                {"field":"createDate", "headerName": "Created Date", "width": width}
            ]
            if id is None:
                query = IAR_Remarks.query.order_by(IAR_Remarks.id)
                total = query.count()

                # Apply pagination
                remarks = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [remark.to_dict() for remark in remarks],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
            else:
                remark = IAR_Remarks.query.get(id)
                if remark is None:
                    abort(404, message=f"IAR_Remarks {id} doesn't exist")
                return {
                    "data": [remark.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
                
        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('IAR_Id', type=int, required=True, help="IAR ID is required")
        parser.add_argument('Remarks', type=str, required=False)
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreateDate', type=str, required=False)
        args = parser.parse_args()

        try:
            new_remark = IAR_Remarks(
                IAR_Id=args['IAR_Id'],
                remarks=args['Remarks'],
                status=args['Status'],
                creatorId=args.get('CreatorId'),
                createDate=datetime.utcnow() + timedelta(hours=5)
            )
            db.session.add(new_remark)
            db.session.commit()
            return {"message": "IAR_Remarks created", "id": new_remark.id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating IAR_Remarks: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('IAR_Id', type=int, required=False)
        parser.add_argument('Remarks', type=str, required=False)
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreateDate', type=str, required=False)
        args = parser.parse_args()

        remark = IAR_Remarks.query.get(id)
        if remark is None:
            abort(404, message=f"IAR_Remarks {id} doesn't exist")

        try:
            if args['IAR_Id'] is not None:
                remark.IAR_Id = args['IAR_Id']
            if args['Remarks'] is not None:
                remark.Remarks = args['Remarks']
            if args['Status'] is not None:
                remark.Status = args['Status']
            if args['CreatorId'] is not None:
                remark.CreatorId = args['CreatorId']
            if args['CreateDate']:
                remark.CreateDate = datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S')

            db.session.commit()
            return {"message": "IAR_Remarks updated", "id": remark.id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating IAR_Remarks: {str(e)}")

    def delete(self, id):
        remark = IAR_Remarks.query.get(id)
        if remark is None:
            abort(404, message=f"IAR_Remarks {id} doesn't exist")

        try:
            db.session.delete(remark)
            db.session.commit()
            return {"message": "IAR_Remarks deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting IAR_Remarks: {str(e)}")

class IARTypesResource(Resource):
    def get(self, id=None, ):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            columns = [
                {"field": "id", "headerName": "Id", "width": width},
                {"field": "name", "headerName": "Name", "width": width}
            ]
            if id:
                iar_type = IAR_Types.query.get(id)
                if iar_type is None:
                    abort(404, message=f"IAR_Types {id} doesn't exist")
                return {
                    "data": [iar_type.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            else:
                query = IAR_Types.query.order_by(IAR_Types.Id)
                total = query.count()

                # Apply pagination
                types = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [iar_type.to_dict() for iar_type in types],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
                
        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Name', type=str, required=True, help="Name is required")
        args = parser.parse_args()

        try:
            new_type = IAR_Types(name=args['Name'])
            db.session.add(new_type)
            db.session.commit()
            return jsonify({"message": "IAR_Types created", "id": new_type.Id}), 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating IAR_Types: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Name', type=str, required=False)
        args = parser.parse_args()

        iar_type = IAR_Types.query.get(id)
        if iar_type is None:
            abort(404, message=f"IAR_Types {id} doesn't exist")

        try:
            if args['Name'] is not None:
                iar_type.name = args['Name']

            db.session.commit()
            return jsonify({"message": "IAR_Types updated", "id": iar_type.Id}), 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating IAR_Types: {str(e)}")

    def delete(self, id):
        iar_type = IAR_Types.query.get(id)
        if iar_type is None:
            abort(404, message=f"IAR_Types {id} doesn't exist")

        try:
            db.session.delete(iar_type)
            db.session.commit()
            return jsonify({"message": "IAR_Types deleted"}), 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting IAR_Types: {str(e)}")

class EmailTypesResource(Resource):
    
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}

            columns = [
                {"field":"id", "headerName": "Id", "width": width},
                {"field":"name", "headerName": "Name", "width": width},
            ]
            
            if id is None:
                query = EmailTypes.query.order_by(EmailTypes.Id)
                total = query.count()

                # Apply pagination
                email_types = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [email_type.to_dict() for email_type in email_types],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
            
            else:
                email_type = EmailTypes.query.get(id)
                if email_type is None:
                    abort(404, message=f"EmailTypes {id} doesn't exist")
                
                return {
                    "data": [email_type.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
            
        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Name', type=str, required=False)
        args = parser.parse_args()

        try:
            new_email_type = EmailTypes(name=args['Name'])
            db.session.add(new_email_type)
            db.session.commit()
            return {"message": "EmailTypes created", "id": new_email_type.Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating EmailTypes: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Name', type=str, required=False)
        args = parser.parse_args()

        email_type = EmailTypes.query.get(id)
        if email_type is None:
            abort(404, message=f"EmailTypes {id} doesn't exist")

        try:
            if args['Name'] is not None:
                email_type.Name = args['Name']
            db.session.commit()
            return {"message": "EmailTypes updated", "id": email_type.Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating EmailTypes: {str(e)}")

    def delete(self, id):
        email_type = EmailTypes.query.get(id)
        if email_type is None:
            abort(404, message=f"EmailTypes {id} doesn't exist")

        try:
            db.session.delete(email_type)
            db.session.commit()
            return {"message": "EmailTypes deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting EmailTypes: {str(e)}")

class EmailStorageSystemResource(Resource):
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}

            columns = [
                {"field":"Email_Id", "headerName": "", "width": width},
                {"field":"Email_Title", "headerName": "", "width": width},
                {"field":"Email_Subject", "headerName": "", "width": width},
                {"field":"Email_Body", "headerName": "", "width": width},
                {"field":"Status", "headerName": "", "width": width},
                {"field":"CreatorId", "headerName": "", "width": width},
                {"field":"CreatedDate", "headerName": "", "width": width},
                {"field":"UpdatorId", "headerName": "", "width": width},
                {"field":"UpdatedDate", "headerName": "", "width": width},
                {"field":"EmailType", "headerName": "", "width": width}
            ]
            if id is None:
                
                query = EmailStorageSystem.query.order_by(EmailStorageSystem.Email_Id)
                total = query.count()

                # Apply pagination
                emails = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [email.to_dict() for email in emails],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
            else:
                email = EmailStorageSystem.query.get(id)
                if email is None:
                    abort(404, message=f"EmailStorageSystem {id} doesn't exist")
                return {
                    "data": [email.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            
        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Email_Title', type=str, required=False)
        parser.add_argument('Email_Subject', type=str, required=False)
        parser.add_argument('Email_Body', type=str, required=False)
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('EmailType', type=int, required=False)
        args = parser.parse_args()

        try:
            new_email = EmailStorageSystem(
                Email_Title=args['Email_Title'],
                Email_Subject=args['Email_Subject'],
                Email_Body=args['Email_Body'],
                Status=args['Status'],
                CreatorId=args.get('CreatorId'),
                CreatedDate=datetime.utcnow() + timedelta(hours=5),
                EmailType=args.get('EmailType')
            )
            db.session.add(new_email)
            db.session.commit()
            return {"status": "success","message": "EmailStorageSystem created", "Email_Id": new_email.Email_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating EmailStorageSystem: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Email_Title', type=str, required=False)
        parser.add_argument('Email_Subject', type=str, required=False)
        parser.add_argument('Email_Body', type=str, required=False)
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatedDate', type=str, required=False)
        parser.add_argument('UpdatorId', type=int, required=False)
        parser.add_argument('UpdatedDate', type=str, required=False)
        parser.add_argument('EmailType', type=int, required=False)
        args = parser.parse_args()

        email = EmailStorageSystem.query.get(id)
        if email is None:
            abort(404, message=f"EmailStorageSystem {id} doesn't exist")

        try:
            if args['Email_Title'] is not None:
                email.Email_Title = args['Email_Title']
            if args['Email_Subject'] is not None:
                email.Email_Subject = args['Email_Subject']
            if args['Email_Body'] is not None:
                email.Email_Body = args['Email_Body']
            if args['Status'] is not None:
                email.Status = args['Status']
            if args['CreatorId'] is not None:
                email.CreatorId = args['CreatorId']
            # if args['CreatedDate']:
            #     email.CreatedDate = datetime.strptime(args['CreatedDate'], '%Y-%m-%d %H:%M:%S')
            if args['UpdatorId'] is not None:
                email.UpdatorId = args['UpdatorId']
            
            email.UpdatedDate = datetime.utcnow() + timedelta(hours=5)
            
            if args['EmailType'] is not None:
                email.EmailType = args['EmailType']
            db.session.commit()
            return {"status": "success",
                "message": "EmailStorageSystem updated", "Email_Id": email.Email_Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating EmailStorageSystem: {str(e)}")

    def delete(self, id):
        email = EmailStorageSystem.query.get(id)
        if email is None:
            abort(404, message=f"EmailStorageSystem {id} doesn't exist")

        try:
            db.session.delete(email)
            db.session.commit()
            return {"message": "EmailStorageSystem deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting EmailStorageSystem: {str(e)}")

class AvailableJobsResource(Resource):
    
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                return {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            columns = [
                {"field":"job_Id", "headerName": "Id", "width": width},
                {"field":"job_Title", "headerName": "Title", "width": width},
                {"field":"job_Level", "headerName": "Level", "width": width},
                {"field":"job_PostedBy", "headerName": "Posted By", "width": width},
                {"field":"job_Status", "headerName": "Status", "width": width},
                {"field":"creatorId", "headerName": "Creator Id", "width": width},
                {"field":"createdDate", "headerName": "Created Date", "width": width},
                {"field":"updatorId", "headerName": "Updator Id", "width": width},
                {"field":"updatedDate", "headerName": "Updated Date", "width": width}
            ]
            if id is None:
                query = AvailableJobs.query.order_by(AvailableJobs.job_Id)
                total = query.count()

                # Apply pagination
                jobs = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [job.to_dict() for job in jobs],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
            else:
                job = AvailableJobs.query.get(id)
                if job is None:
                    abort(404, message=f"AvailableJobs {id} doesn't exist")
                return {
                    "data": [job.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            
        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('job_Title', type=str, required=True, help="Job Title is required")
        parser.add_argument('job_Level', type=str, required=True, help="Job Level is required")
        parser.add_argument('job_PostedBy', type=int, required=False)
        parser.add_argument('job_Status', type=bool, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        args = parser.parse_args()

        try:
            new_job = AvailableJobs(
                job_Title=args['job_Title'],
                job_Level=args['job_Level'],
                job_PostedBy=args.get('job_PostedBy'),
                job_Status=args.get('job_Status'),
                creatorId=args.get('creatorId'),
                createdDate=datetime.utcnow() + timedelta(hours=5)
            )
            db.session.add(new_job)
            db.session.commit()
            return {"message": "AvailableJobs created", "job_Id": new_job.job_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating AvailableJobs: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('job_Title', type=str, required=False)
        parser.add_argument('job_Level', type=str, required=False)
        parser.add_argument('job_PostedBy', type=int, required=False)
        parser.add_argument('job_Status', type=bool, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('createdDate', type=str, required=False)
        parser.add_argument('updatorId', type=int, required=False)
        parser.add_argument('updatedDate', type=str, required=False)
        args = parser.parse_args()

        job = AvailableJobs.query.get(id)
        if job is None:
            abort(404, message=f"AvailableJobs {id} doesn't exist")

        try:
            if args['job_Title'] is not None:
                job.job_Title = args['job_Title']
            if args['job_Level'] is not None:
                job.job_Level = args['job_Level']
            if args['job_PostedBy'] is not None:
                job.job_PostedBy = args['job_PostedBy']
            if args['job_Status'] is not None:
                job.job_Status = args['job_Status']
            if args['creatorId'] is not None:
                job.creatorId = args['creatorId']
            if args['createdDate']:
                job.createdDate = datetime.strptime(args['createdDate'], '%Y-%m-%d %H:%M:%S')
            if args['updatorId'] is not None:
                job.updatorId = args['updatorId']
            
            job.updatedDate = datetime.strptime(datetime.utcnow() + timedelta(hours=5), '%Y-%m-%d %H:%M:%S')
            db.session.commit()
            return {"message": "AvailableJobs updated", "job_Id": job.job_Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating AvailableJobs: {str(e)}")

    def delete(self, id):
        job = AvailableJobs.query.get(id)
        if job is None:
            abort(404, message=f"AvailableJobs {id} doesn't exist")

        try:
            db.session.delete(job)
            db.session.commit()
            return {"message": "AvailableJobs deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting AvailableJobs: {str(e)}")

class StaffInfoResource(Resource):
    def get(self, id=None):
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                return {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            if id:
                staff = StaffInfo.query.get_or_404(id)
                print("Date of Joining: ", staff.S_JoiningDate)
                
                return json.loads(json.dumps({
                    "Employee Name": str(staff.Staff_ID) + " | " + staff.S_Name,
                    "Designation": staff.Designation_ID,
                    "Campus": staff.CampusId,
                    "Department": staff.DepartmentId,
                    "Date of Joining": staff.S_JoiningDate
                    }, indent=4, cls=DateTimeEncoder)), 200
            else:
                
                query = StaffInfo.query.order_by(StaffInfo.Staff_ID)
                total = query.count()
                
                paginated_staff = query.paginate(page=page_no, per_page=page_size, error_out=False).items
                
                return {
                    "data": [json.loads(json.dumps(staff.to_dict())) for staff in paginated_staff],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size
                }, 200
        except Exception as e:
            return {"error": str(e)}, 500
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Personal_ID', type=str)
        parser.add_argument('S_Name', type=str, required=True, help='Name is required')
        parser.add_argument('S_FName', type=str)
        parser.add_argument('S_Gender', type=int, required=True, help='Gender is required')
        parser.add_argument('S_CNIC', type=str)
        parser.add_argument('S_Email', type=str)
        parser.add_argument('S_ContactNo', type=str)
        parser.add_argument('S_DoB', type=str, required=True, help='Date of Birth is required')
        parser.add_argument('S_JoiningDate', type=str, required=True, help='Joining Date is required')
        parser.add_argument('S_firstJOrderNo', type=str)
        parser.add_argument('S_JoiningDesg', type=int)
        parser.add_argument('S_JoiningGrade', type=int)
        parser.add_argument('S_firstJPlace', type=str)
        parser.add_argument('S_PresentDesignation', type=int)
        parser.add_argument('S_PresentGrade', type=int)
        parser.add_argument('S_SchoolName', type=str)
        parser.add_argument('S_District', type=str)
        parser.add_argument('S_Union', type=str)
        parser.add_argument('S_WardNo', type=str)
        parser.add_argument('S_Village', type=str)
        parser.add_argument('Designation_ID', type=int, required=True, help='Designation ID is required')
        parser.add_argument('Grade_ID', type=int)
        parser.add_argument('IsNonTeacher', type=bool, required=True, help='IsNonTeacher is required')
        parser.add_argument('S_Salary', type=float)
        parser.add_argument('UpdaterId', type=int)
        parser.add_argument('UpdaterIP', type=str)
        parser.add_argument('UpdaterTerminal', type=str)
        parser.add_argument('UpdateDate', type=str)
        parser.add_argument('CreatorId', type=int)
        parser.add_argument('CreatorIP', type=str)
        parser.add_argument('CreatorTerminal', type=str)
        parser.add_argument('CreateDate', type=str)
        parser.add_argument('PhotoPath', type=str)
        parser.add_argument('IsDisable', type=bool, required=True, help='IsDisable is required')
        parser.add_argument('disableDetail', type=str)
        parser.add_argument('EOBI', type=str)
        parser.add_argument('ProbationPeriod', type=float)
        parser.add_argument('ProbationEndDate', type=str)
        parser.add_argument('IsPermanent', type=bool, required=True, help='IsPermanent is required')
        parser.add_argument('IsTerminate', type=bool)
        parser.add_argument('DepartmentId', type=int)
        parser.add_argument('HouseNo', type=str)
        parser.add_argument('Street_Sector_BlockNo', type=str)
        parser.add_argument('AreaId', type=int)
        parser.add_argument('CityId', type=int)
        parser.add_argument('District', type=str)
        parser.add_argument('Province', type=str)
        parser.add_argument('CountryId', type=int)
        parser.add_argument('PresentAddress', type=str)
        parser.add_argument('TempAddress', type=str)
        parser.add_argument('Whatsapp', type=str)
        parser.add_argument('EmergencyContactName', type=str)
        parser.add_argument('EmergencyContactNo', type=str)
        parser.add_argument('HomeNo', type=str)
        parser.add_argument('Rent_Personal', type=str)
        parser.add_argument('MaritalStatus', type=str)
        parser.add_argument('AccountTitle', type=str)
        parser.add_argument('AccountNo', type=str)
        parser.add_argument('BankName', type=str)
        parser.add_argument('Branch', type=str)
        parser.add_argument('IsFatherName', type=bool)
        parser.add_argument('FHWName', type=str)
        parser.add_argument('FHWCNIC', type=str)
        parser.add_argument('FWHDOB', type=str)
        parser.add_argument('CampusId', type=int)
        parser.add_argument('BarcodeId', type=str, required=True, help='BarcodeId is required')
        parser.add_argument('IsAppearLive', type=bool, required=True, help='IsAppearLive is required')
        parser.add_argument('Category', type=int)
        parser.add_argument('FId', type=int)
        parser.add_argument('Initials', type=str)
        parser.add_argument('IsSalaryOn', type=bool)
        parser.add_argument('EmpId', type=int)
        parser.add_argument('IsAEN', type=int)
        parser.add_argument('ReportingOfficerId', type=int)
        parser.add_argument('FileNumber', type=int)
        parser.add_argument('FileLocation', type=str)
        parser.add_argument('IsExit', type=bool)
        parser.add_argument('Grace_In', type=int)
        parser.add_argument('Grace_Out', type=int)
        parser.add_argument('ShiftType', type=int)
        args = parser.parse_args()

        try:
            new_staff = StaffInfo(
                Personal_ID=args['Personal_ID'],
                S_Name=args['S_Name'],
                S_FName=args['S_FName'],
                S_Gender=args['S_Gender'],
                S_CNIC=args['S_CNIC'],
                S_Email=args['S_Email'],
                S_ContactNo=args['S_ContactNo'],
                S_DoB=datetime.strptime(args['S_DoB'], '%Y-%m-%d'),
                S_JoiningDate=datetime.strptime(args['S_JoiningDate'], '%Y-%m-%d'),
                S_firstJOrderNo=args['S_firstJOrderNo'],
                S_JoiningDesg=args['S_JoiningDesg'],
                S_JoiningGrade=args['S_JoiningGrade'],
                S_firstJPlace=args['S_firstJPlace'],
                S_PresentDesignation=args['S_PresentDesignation'],
                S_PresentGrade=args['S_PresentGrade'],
                S_SchoolName=args['S_SchoolName'],
                S_District=args['S_District'],
                S_Union=args['S_Union'],
                S_WardNo=args['S_WardNo'],
                S_Village=args['S_Village'],
                Designation_ID=args['Designation_ID'],
                Grade_ID=args['Grade_ID'],
                IsNonTeacher=args['IsNonTeacher'],
                S_Salary=args['S_Salary'],
                UpdaterId=args['UpdaterId'],
                UpdaterIP=args['UpdaterIP'],
                UpdaterTerminal=args['UpdaterTerminal'],
                UpdateDate=datetime.strptime(args['UpdateDate'], '%Y-%m-%d') if args['UpdateDate'] else None,
                CreatorId=args['CreatorId'],
                CreatorIP=args['CreatorIP'],
                CreatorTerminal=args['CreatorTerminal'],
                CreateDate=datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S') if args['CreateDate'] else datetime.utcnow() + timedelta(hours=5),
                PhotoPath=args['PhotoPath'],
                IsDisable=args['IsDisable'],
                disableDetail=args['disableDetail'],
                EOBI=args['EOBI'],
                ProbationPeriod=args['ProbationPeriod'],
                ProbationEndDate=datetime.strptime(args['ProbationEndDate'], '%Y-%m-%d') if args['ProbationEndDate'] else None,
                IsPermanent=args['IsPermanent'],
                IsTerminate=args['IsTerminate'],
                DepartmentId=args['DepartmentId'],
                HouseNo=args['HouseNo'],
                Street_Sector_BlockNo=args['Street_Sector_BlockNo'],
                AreaId=args['AreaId'],
                CityId=args['CityId'],
                District=args['District'],
                Province=args['Province'],
                CountryId=args['CountryId'],
                PresentAddress=args['PresentAddress'],
                TempAddress=args['TempAddress'],
                Whatsapp=args['Whatsapp'],
                EmergencyContactName=args['EmergencyContactName'],
                EmergencyContactNo=args['EmergencyContactNo'],
                HomeNo=args['HomeNo'],
                Rent_Personal=args['Rent_Personal'],
                MaritalStatus=args['MaritalStatus'],
                AccountTitle=args['AccountTitle'],
                AccountNo=args['AccountNo'],
                BankName=args['BankName'],
                Branch=args['Branch'],
                IsFatherName=args['IsFatherName'],
                FHWName=args['FHWName'],
                FHWCNIC=args['FHWCNIC'],
                FWHDOB=datetime.strptime(args['FWHDOB'], '%Y-%m-%d') if args['FWHDOB'] else None,
                CampusId=args['CampusId'],
                BarcodeId=args['BarcodeId'],
                IsAppearLive=args['IsAppearLive'],
                Category=args['Category'],
                FId=args['FId'],
                Initials=args['Initials'],
                IsSalaryOn=args['IsSalaryOn'],
                EmpId=args['EmpId'],
                IsAEN=args['IsAEN'],
                ReportingOfficerId=args['ReportingOfficerId'],
                FileNumber=args['FileNumber'],
                FileLocation=args['FileLocation'],
                IsExit=args['IsExit'],
                Grace_In=args['Grace_In'],
                Grace_Out=args['Grace_Out'],
                ShiftType=args['ShiftType'],
            )

            db.session.add(new_staff)
            db.session.commit()
            return new_staff.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Personal_ID', type=str)
        parser.add_argument('S_Name', type=str)
        parser.add_argument('S_FName', type=str)
        parser.add_argument('S_Gender', type=int)
        parser.add_argument('S_CNIC', type=str)
        parser.add_argument('S_Email', type=str)
        parser.add_argument('S_ContactNo', type=str)
        parser.add_argument('S_DoB', type=str)
        parser.add_argument('S_JoiningDate', type=str)
        parser.add_argument('S_firstJOrderNo', type=str)
        parser.add_argument('S_JoiningDesg', type=int)
        parser.add_argument('S_JoiningGrade', type=int)
        parser.add_argument('S_firstJPlace', type=str)
        parser.add_argument('S_PresentDesignation', type=int)
        parser.add_argument('S_PresentGrade', type=int)
        parser.add_argument('S_SchoolName', type=str)
        parser.add_argument('S_District', type=str)
        parser.add_argument('S_Union', type=str)
        parser.add_argument('S_WardNo', type=str)
        parser.add_argument('S_Village', type=str)
        parser.add_argument('Designation_ID', type=int)
        parser.add_argument('Grade_ID', type=int)
        parser.add_argument('IsActive', type=bool)
        parser.add_argument('IsNonTeacher', type=bool)
        parser.add_argument('S_Salary', type=float)
        parser.add_argument('UpdaterId', type=int)
        parser.add_argument('UpdaterIP', type=str)
        parser.add_argument('UpdaterTerminal', type=str)
        parser.add_argument('UpdateDate', type=str)
        parser.add_argument('CreatorId', type=int)
        parser.add_argument('CreatorIP', type=str)
        parser.add_argument('CreatorTerminal', type=str)
        parser.add_argument('CreateDate', type=str)
        parser.add_argument('PhotoPath', type=str)
        parser.add_argument('IsDisable', type=bool)
        parser.add_argument('disableDetail', type=str)
        parser.add_argument('EOBI', type=str)
        parser.add_argument('ProbationPeriod', type=float)
        parser.add_argument('ProbationEndDate', type=str)
        parser.add_argument('IsPermanent', type=bool)
        parser.add_argument('IsTerminate', type=bool)
        parser.add_argument('DepartmentId', type=int)
        parser.add_argument('HouseNo', type=str)
        parser.add_argument('Street_Sector_BlockNo', type=str)
        parser.add_argument('AreaId', type=int)
        parser.add_argument('CityId', type=int)
        parser.add_argument('District', type=str)
        parser.add_argument('Province', type=str)
        parser.add_argument('CountryId', type=int)
        parser.add_argument('PresentAddress', type=str)
        parser.add_argument('TempAddress', type=str)
        parser.add_argument('Whatsapp', type=str)
        parser.add_argument('EmergencyContactName', type=str)
        parser.add_argument('EmergencyContactNo', type=str)
        parser.add_argument('HomeNo', type=str)
        parser.add_argument('Rent_Personal', type=str)
        parser.add_argument('MaritalStatus', type=str)
        parser.add_argument('AccountTitle', type=str)
        parser.add_argument('AccountNo', type=str)
        parser.add_argument('BankName', type=str)
        parser.add_argument('Branch', type=str)
        parser.add_argument('IsFatherName', type=bool)
        parser.add_argument('FHWName', type=str)
        parser.add_argument('FHWCNIC', type=str)
        parser.add_argument('FWHDOB', type=str)
        parser.add_argument('CampusId', type=int)
        parser.add_argument('BarcodeId', type=str)
        parser.add_argument('IsAppearLive', type=bool)
        parser.add_argument('Category', type=int)
        parser.add_argument('FId', type=int)
        parser.add_argument('Initials', type=str)
        parser.add_argument('IsSalaryOn', type=bool)
        parser.add_argument('EmpId', type=int)
        parser.add_argument('IsAEN', type=int)
        parser.add_argument('ReportingOfficerId', type=int)
        parser.add_argument('FileNumber', type=int)
        parser.add_argument('FileLocation', type=str)
        parser.add_argument('IsExit', type=bool)
        parser.add_argument('Grace_In', type=int)
        parser.add_argument('Grace_Out', type=int)
        parser.add_argument('ShiftType', type=int)
        args = parser.parse_args()

        try:
            staff = StaffInfo.query.get_or_404(id)

            if args['Personal_ID'] is not None:
                staff.Personal_ID = args['Personal_ID']
            if args['S_Name'] is not None:
                staff.S_Name = args['S_Name']
            if args['S_FName'] is not None:
                staff.S_FName = args['S_FName']
            if args['S_Gender'] is not None:
                staff.S_Gender = args['S_Gender']
            if args['S_CNIC'] is not None:
                staff.S_CNIC = args['S_CNIC']
            if args['S_Email'] is not None:
                staff.S_Email = args['S_Email']
            if args['S_ContactNo'] is not None:
                staff.S_ContactNo = args['S_ContactNo']
            if args['S_DoB'] is not None:
                staff.S_DoB = datetime.strptime(args['S_DoB'], '%Y-%m-%d')
            if args['S_JoiningDate'] is not None:
                staff.S_JoiningDate = datetime.strptime(args['S_JoiningDate'], '%Y-%m-%d')
            if args['S_firstJOrderNo'] is not None:
                staff.S_firstJOrderNo = args['S_firstJOrderNo']
            if args['S_JoiningDesg'] is not None:
                staff.S_JoiningDesg = args['S_JoiningDesg']
            if args['S_JoiningGrade'] is not None:
                staff.S_JoiningGrade = args['S_JoiningGrade']
            if args['S_firstJPlace'] is not None:
                staff.S_firstJPlace = args['S_firstJPlace']
            if args['S_PresentDesignation'] is not None:
                staff.S_PresentDesignation = args['S_PresentDesignation']
            if args['S_PresentGrade'] is not None:
                staff.S_PresentGrade = args['S_PresentGrade']
            if args['S_SchoolName'] is not None:
                staff.S_SchoolName = args['S_SchoolName']
            if args['S_District'] is not None:
                staff.S_District = args['S_District']
            if args['S_Union'] is not None:
                staff.S_Union = args['S_Union']
            if args['S_WardNo'] is not None:
                staff.S_WardNo = args['S_WardNo']
            if args['S_Village'] is not None:
                staff.S_Village = args['S_Village']
            if args['Designation_ID'] is not None:
                staff.Designation_ID = args['Designation_ID']
            if args['Grade_ID'] is not None:
                staff.Grade_ID = args['Grade_ID']
            if args['IsActive'] is not None:
                staff.IsActive = args['IsActive']
            if args['IsNonTeacher'] is not None:
                staff.IsNonTeacher = args['IsNonTeacher']
            if args['S_Salary'] is not None:
                staff.S_Salary = args['S_Salary']
            if args['UpdaterId'] is not None:
                staff.UpdaterId = args['UpdaterId']
            if args['UpdaterIP'] is not None:
                staff.UpdaterIP = args['UpdaterIP']
            if args['UpdaterTerminal'] is not None:
                staff.UpdaterTerminal = args['UpdaterTerminal']
            
            staff.UpdateDate = datetime.strptime(datetime.utcnow() + timedelta(hours=5), '%Y-%m-%d %H:%M:%S')
            if args['CreatorId'] is not None:
                staff.CreatorId = args['CreatorId']
            if args['CreatorIP'] is not None:
                staff.CreatorIP = args['CreatorIP']
            if args['CreatorTerminal'] is not None:
                staff.CreatorTerminal = args['CreatorTerminal']
            if args['CreateDate'] is not None:
                staff.CreateDate = datetime.strptime(args['CreateDate'], '%Y-%m-%d')
            if args['PhotoPath'] is not None:
                staff.PhotoPath = args['PhotoPath']
            if args['IsDisable'] is not None:
                staff.IsDisable = args['IsDisable']
            if args['disableDetail'] is not None:
                staff.disableDetail = args['disableDetail']
            if args['EOBI'] is not None:
                staff.EOBI = args['EOBI']
            if args['ProbationPeriod'] is not None:
                staff.ProbationPeriod = args['ProbationPeriod']
            if args['ProbationEndDate'] is not None:
                staff.ProbationEndDate = datetime.strptime(args['ProbationEndDate'], '%Y-%m-%d')
            if args['IsPermanent'] is not None:
                staff.IsPermanent = args['IsPermanent']
            if args['IsTerminate'] is not None:
                staff.IsTerminate = args['IsTerminate']
            if args['DepartmentId'] is not None:
                staff.DepartmentId = args['DepartmentId']
            if args['HouseNo'] is not None:
                staff.HouseNo = args['HouseNo']
            if args['Street_Sector_BlockNo'] is not None:
                staff.Street_Sector_BlockNo = args['Street_Sector_BlockNo']
            if args['AreaId'] is not None:
                staff.AreaId = args['AreaId']
            if args['CityId'] is not None:
                staff.CityId = args['CityId']
            if args['District'] is not None:
                staff.District = args['District']
            if args['Province'] is not None:
                staff.Province = args['Province']
            if args['CountryId'] is not None:
                staff.CountryId = args['CountryId']
            if args['PresentAddress'] is not None:
                staff.PresentAddress = args['PresentAddress']
            if args['TempAddress'] is not None:
                staff.TempAddress = args['TempAddress']
            if args['Whatsapp'] is not None:
                staff.Whatsapp = args['Whatsapp']
            if args['EmergencyContactName'] is not None:
                staff.EmergencyContactName = args['EmergencyContactName']
            if args['EmergencyContactNo'] is not None:
                staff.EmergencyContactNo = args['EmergencyContactNo']
            if args['HomeNo'] is not None:
                staff.HomeNo = args['HomeNo']
            if args['Rent_Personal'] is not None:
                staff.Rent_Personal = args['Rent_Personal']
            if args['MaritalStatus'] is not None:
                staff.MaritalStatus = args['MaritalStatus']
            if args['AccountTitle'] is not None:
                staff.AccountTitle = args['AccountTitle']
            if args['AccountNo'] is not None:
                staff.AccountNo = args['AccountNo']
            if args['BankName'] is not None:
                staff.BankName = args['BankName']
            if args['Branch'] is not None:
                staff.Branch = args['Branch']
            if args['IsFatherName'] is not None:
                staff.IsFatherName = args['IsFatherName']
            if args['FHWName'] is not None:
                staff.FHWName = args['FHWName']
            if args['FHWCNIC'] is not None:
                staff.FHWCNIC = args['FHWCNIC']
            if args['FWHDOB'] is not None:
                staff.FWHDOB = datetime.strptime(args['FWHDOB'], '%Y-%m-%d')
            if args['CampusId'] is not None:
                staff.CampusId = args['CampusId']
            if args['BarcodeId'] is not None:
                staff.BarcodeId = args['BarcodeId']
            if args['IsAppearLive'] is not None:
                staff.IsAppearLive = args['IsAppearLive']
            if args['Category'] is not None:
                staff.Category = args['Category']
            if args['FId'] is not None:
                staff.FId = args['FId']
            if args['Initials'] is not None:
                staff.Initials = args['Initials']
            if args['IsSalaryOn'] is not None:
                staff.IsSalaryOn = args['IsSalaryOn']
            if args['EmpId'] is not None:
                staff.EmpId = args['EmpId']
            if args['IsAEN'] is not None:
                staff.IsAEN = args['IsAEN']
            if args['ReportingOfficerId'] is not None:
                staff.ReportingOfficerId = args['ReportingOfficerId']
            if args['FileNumber'] is not None:
                staff.FileNumber = args['FileNumber']
            if args['FileLocation'] is not None:
                staff.FileLocation = args['FileLocation']
            if args['IsExit'] is not None:
                staff.IsExit = args['IsExit']
            if args['Grace_In'] is not None:
                staff.Grace_In = args['Grace_In']
            if args['Grace_Out'] is not None:
                staff.Grace_Out = args['Grace_Out']
            if args['ShiftType'] is not None:
                staff.ShiftType = args['ShiftType']

            db.session.commit()
            return staff.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, id):
        try:
            staff = StaffInfo.query.get_or_404(id)
            db.session.delete(staff)
            db.session.commit()
            return {"message": "Staff member deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class StaffDepartmentResource(Resource):
    def get(self, id=None):
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                return {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            if id:
                department = StaffDepartments.query.get_or_404(id)
                return jsonify({"data": department.to_dict()})
            else:
                query = StaffDepartments.query.order_by(StaffDepartments.Id)
                total = query.count()
                departments = query.paginate(page=page_no, per_page=page_size, error_out=False).items
                return jsonify({
                    "data": [dept.to_dict() for dept in departments],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size
                })

        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('DepartmentName', type=str, required=False)
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('UpdaterId', type=int, required=False)
        parser.add_argument('UpdaterIP', type=str, required=False)
        parser.add_argument('UpdaterTerminal', type=str, required=False)
        parser.add_argument('UpdateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatorIP', type=str, required=False)
        parser.add_argument('CreatorTerminal', type=str, required=False)
        parser.add_argument('CreateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CampusId', type=int, required=False)
        parser.add_argument('ManagerId', type=int, required=False)
        args = parser.parse_args()

        try:
            new_department = StaffDepartments(
                DepartmentName=args['DepartmentName'],
                status=args['status'],
                UpdaterId=args['UpdaterId'],
                UpdaterIP=args['UpdaterIP'],
                UpdaterTerminal=args['UpdaterTerminal'],
                UpdateDate=args['UpdateDate'],
                CreatorId=args['CreatorId'],
                CreatorIP=args['CreatorIP'],
                CreatorTerminal=args['CreatorTerminal'],
                CreateDate=datetime.utcnow() + timedelta(hours=5),
                CampusId=args['CampusId'],
                ManagerId=args['ManagerId']
            )

            db.session.add(new_department)
            db.session.commit()
            return {"message": "Staff department created", "id": new_department.Id}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('DepartmentName', type=str, required=False)
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('UpdaterId', type=int, required=False)
        parser.add_argument('UpdaterIP', type=str, required=False)
        parser.add_argument('UpdaterTerminal', type=str, required=False)
        parser.add_argument('UpdateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatorIP', type=str, required=False)
        parser.add_argument('CreatorTerminal', type=str, required=False)
        parser.add_argument('CreateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CampusId', type=int, required=False)
        parser.add_argument('ManagerId', type=int, required=False)
        args = parser.parse_args()

        try:
            department = StaffDepartments.query.get_or_404(id)

            if args['DepartmentName']:
                department.DepartmentName = args['DepartmentName']
            if args['status'] is not None:
                department.status = args['status']
            if args['UpdaterId']:
                department.UpdaterId = args['UpdaterId']
            if args['UpdaterIP']:
                department.UpdaterIP = args['UpdaterIP']
            if args['UpdaterTerminal']:
                department.UpdaterTerminal = args['UpdaterTerminal']
            
            department.UpdateDate = datetime.utcnow() + timedelta(hours=5)
            
            if args['CreatorId']:
                department.CreatorId = args['CreatorId']
            if args['CreatorIP']:
                department.CreatorIP = args['CreatorIP']
            if args['CreatorTerminal']:
                department.CreatorTerminal = args['CreatorTerminal']
            if args['CreateDate']:
                department.CreateDate = args['CreateDate']
            if args['CampusId']:
                department.CampusId = args['CampusId']
            if args['ManagerId']:
                department.ManagerId = args['ManagerId']

            db.session.commit()
            return {"message": "Staff department updated", "id": department.Id}, 200
        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        try:
            department = StaffDepartments.query.get_or_404(id)
            db.session.delete(department)
            db.session.commit()
            return {"message": "Staff department deleted"}, 200
        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

class StaffTransferResource(Resource):
    
    def get(self, id=None):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            
            if id:
                staff_transfer = StaffTransfer.query.get_or_404(id)
                return jsonify({"data": staff_transfer.to_dict()})
            else:
                query = StaffTransfer.query.order_by(StaffTransfer.Id)
                total = query.count()
                transfers = query.paginate(page=page_no, per_page=page_size, error_out=False).items
                return jsonify({
                    "data": [transfer.to_dict() for transfer in transfers],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size
                })

        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        """
        Handles the creation of a new staff transfer request.
        Parses incoming request data, creates a new StaffTransfer record,
        and updates related tables within a single transaction.
        """
        # Parse the incoming request data
        parser = reqparse.RequestParser()
        parser.add_argument('StaffId', type=int, required=True, help='StaffId is required')
        parser.add_argument('Transfer_Type', type=str, required=True, help='Transfer_Type is required')
        parser.add_argument('Transfer_Date', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help='Transfer_Date is required in format %Y-%m-%dT%H:%M:%S')
        parser.add_argument('Reason_for_Transfer', type=str, required=True, help='Reason_for_Transfer is required')
        parser.add_argument('Transfer_from_Campus', type=int, required=True, help='Transfer_from_Campus is required')
        parser.add_argument('Transfer_To_Campus', type=int, required=True, help='Transfer_To_Campus is required')
        parser.add_argument('DepartmentId', type=int, required=True, help='DepartmentId is required')
        parser.add_argument('OldDepartmentId', type=int)
        parser.add_argument('DesignationId', type=int, required=True, help='DesignationId is required')
        parser.add_argument('OldDesignationId', type=int)
        parser.add_argument('ReportingOfficerId', type=int, required=True, help='ReportingOfficerId is required')
        parser.add_argument('Transfer_initiated_by', type=int, required=True, help='Transfer_initiated_by is required')
        parser.add_argument('Transfer_approval', type=int, required=True, help='Transfer_approval is required')
        parser.add_argument('CampusId', type=int),
        parser.add_argument('CreatorId', type=int),
        parser.add_argument('Remarks', type=str, required=True, help='Remarks is required')
        args = parser.parse_args()
        logging.info(f"Args {args}")

        try:
            # Retrieve the staff record
            staff = StaffInfo.query.get(args['StaffId'])
            if staff is None:
                return {"message": "Staff not found"}, 404

            # Determine the from_campus_id based on the IsAEN flag
            print(f"staff.IsAEN: {staff.IsAEN}, staff.CampusId: {staff.CampusId}")
            from_campus_id = 11 if staff.IsAEN == 1 else staff.CampusId
            current_campus_id=staff.CampusId
            to_campus_id = args['Transfer_To_Campus']

            # Create a new StaffTransfer record
            new_transfer = StaffTransfer(
                StaffId=args['StaffId'],
                Transfer_Type=args['Transfer_Type'],
                Transfer_Date=args['Transfer_Date'],
                Reason_for_Transfer=args['Reason_for_Transfer'],
                Transfer_from_Campus=from_campus_id,
                Transfer_To_Campus=to_campus_id,
                DepartmentId=args['DepartmentId'],
                OldDepartmentId=args['OldDepartmentId'],
                DesignationId=args['DesignationId'],
                OldDesignationId=args['OldDesignationId'],
                ReportingOfficerId=args['ReportingOfficerId'],
                Transfer_initiated_by=args['Transfer_initiated_by'],
                Transfer_approval=args['Transfer_approval'],
                Remarks=args['Remarks'],
                Status=True,
                CampusId=args['CampusId'],
                CreatorId=args['CreatorId'],
                # CreatorId=get_jwt_identity(),
                CreateDate=datetime.utcnow() + timedelta(hours=5)
            )

            # Start a database transaction
            with db.session.begin_nested():
                db.session.add(new_transfer)
                db.session.flush()

                # Update related tables
                self.update_staff_info(staff, to_campus_id, args['ReportingOfficerId'], args['DepartmentId'],args['OldDepartmentId'], args['DesignationId'], args['OldDesignationId'])
                self.update_staff_shift(args['StaffId'], to_campus_id)
                self.update_user_campus(args['StaffId'], to_campus_id, current_campus_id)
                self.update_user(args['StaffId'], to_campus_id)

            # Commit the transaction
            db.session.commit()
            return {"status": "success",
                "message": "Staff transfer created and related tables updated successfully"}, 201
        except SQLAlchemyError as e:
            # Rollback transaction in case of database error
            db.session.rollback()
            return {"error": f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            # Rollback transaction in case of any unexpected error
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def update_staff_info(self, staff, to_campus_id, reporting_officer_id, department_id, Olddepartment_id,designation_id, Olddesignation_id):
        """
        Updates the StaffInfo table with the new transfer details, 
        including setting the IsAEN flag if transferring to campus 11.
        """
        try:
            # staff = StaffInfo.query.get(staff_id)
            if to_campus_id == 11:
                staff.IsAEN = 1  # Set IsAEN flag if transferring to campus 11
            else:
                staff.IsAEN = 0  # Unset IsAEN flag for other campuses
            
            staff.CampusId = to_campus_id
            staff.DepartmentId = department_id
            # staff.OldDepartmentId = Olddepartment_id
            staff.Designation_ID = designation_id
            # staff.OldDesignation_ID = Olddesignation_id
            staff.ReportingOfficerId = reporting_officer_id
            # staff.UpdateDate = datetime.utcnow() + timedelta(hours=5)
            db.session.add(staff)
        except SQLAlchemyError as e:
            # Rollback transaction in case of database error
            db.session.rollback()
            print("update_staff_info")
            raise e
        except Exception as e:
            # Rollback transaction in case of any unexpected error
            db.session.rollback()
            print("update_staff_info")
            raise e
        
    def update_staff_shift(self, staff_id, to_campus_id):
        """
        Updates the StaffShift table with the new campus ID and sets the UpdatedOn date.
        """
        try:
            staff_shift = StaffShifts.query.filter_by(StaffId=staff_id).first()
            
            if staff_shift:
                staff_shift.CampusId = to_campus_id
                staff_shift.UpdatedOn = datetime.utcnow() + timedelta(hours=5)
                db.session.add(staff_shift)
        
        except SQLAlchemyError as e:
            # Rollback transaction in case of database error
            db.session.rollback()
            print("update_staff_shift")
            raise e
        except Exception as e:
            # Rollback transaction in case of any unexpected error
            db.session.rollback()
            print("update_staff_shift")
            raise e
        
    def update_user_campus(self, staff_id, to_campus_id, current_campus_id):
        """
        Updates the UserCampus table with the new campus ID.
        Inserts a new record if necessary.
        """
        try:
            print(f"to_campus_id: {to_campus_id}, staff_id: {staff_id}, current_campus_id: {current_campus_id}")
            user_campus = UserCampus.query.filter_by(StaffId=staff_id, CampusId=current_campus_id).first()
            user_campus.CampusId = to_campus_id
            user_campus.UpdateDate = datetime.utcnow() + timedelta(hours=5)
            db.session.add(user_campus)
            # if to_campus_id == 11:
            #     user_campus = UserCampus.query.filter_by(StaffId=staff_id, CampusId=to_campus_id).first()
                
            #     if not user_campus:
            #         user_campus = UserCampus.query.filter_by(StaffId=staff_id).first()
            #         new_user_campus = UserCampus(
            #             UserId=user_campus.UserId,
            #             CampusId=to_campus_id,
            #             StaffId=staff_id,
            #             Date=datetime.utcnow() + timedelta(hours=5),
            #             Status=True
            #         )
            #         db.session.add(new_user_campus)
                
            # else:

        except SQLAlchemyError as e:
            # Rollback transaction in case of database error
            db.session.rollback()
            print("update_user_campus")
            raise e
        except Exception as e:
            # Rollback transaction in case of any unexpected error
            db.session.rollback()
            print("update_user_campus")
            raise e

    def update_user(self, staff_id, to_campus_id):
        """
        Updates the USERS table with the new campus ID and sets the IsAEN flag if transferring to campus 11
        """
        
        try:
            user_id = UserCampus.query.filter_by(StaffId=staff_id).first().UserId
            user = USERS.query.get(user_id)
            
            if to_campus_id == 11:
                user.IsAEN = 1  # Set IsAEN flag if transferring to campus 11
            else:
                user.IsAEN = 0  # Unset IsAEN flag for other campuses
            
            user.CampusId = to_campus_id
            #user.updateDate = datetime.utcnow() + timedelta(hours=5)
            db.session.add(user)
        
        except SQLAlchemyError as e:
            # Rollback transaction in case of database error
            print("update_user")
            db.session.rollback()
            raise e
        except Exception as e:
            # Rollback transaction in case of any unexpected error
            db.session.rollback()
            print("update_user")
            raise e

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('StaffId', type=int, required=False)
        parser.add_argument('Transfer_Type', type=str, required=False)
        parser.add_argument('Transfer_Date', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('Reason_for_Transfer', type=str, required=False)
        parser.add_argument('Transfer_from_Campus', type=int, required=False)
        parser.add_argument('Transfer_To_Campus', type=int, required=False)
        parser.add_argument('DepartmentId', type=int, required=False)
        parser.add_argument('DesignationId', type=int, required=False)
        parser.add_argument('ReportingOfficerId', type=int, required=False)
        parser.add_argument('Transfer_initiated_by', type=int, required=False)
        parser.add_argument('Transfer_approval', type=int, required=False)
        parser.add_argument('Remarks', type=str, required=False)
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('UpdaterId', type=int, required=False)
        parser.add_argument('UpdateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        args = parser.parse_args()

        try:
            transfer = StaffTransfer.query.get_or_404(id)

            if args['StaffId'] is not None:
                transfer.StaffId = args['StaffId']
            if args['Transfer_Type'] is not None:
                transfer.Transfer_Type = args['Transfer_Type']
            if args['Transfer_Date'] is not None:
                transfer.Transfer_Date = args['Transfer_Date']
            if args['Reason_for_Transfer'] is not None:
                transfer.Reason_for_Transfer = args['Reason_for_Transfer']
            if args['Transfer_from_Campus'] is not None:
                transfer.Transfer_from_Campus = args['Transfer_from_Campus']
            if args['Transfer_To_Campus'] is not None:
                transfer.Transfer_To_Campus = args['Transfer_To_Campus']
            if args['DepartmentId'] is not None:
                transfer.DepartmentId = args['DepartmentId']
            if args['DesignationId'] is not None:
                transfer.DesignationId = args['DesignationId']
            if args['ReportingOfficerId'] is not None:
                transfer.ReportingOfficerId = args['ReportingOfficerId']
            if args['Transfer_initiated_by'] is not None:
                transfer.Transfer_initiated_by = args['Transfer_initiated_by']
            if args['Transfer_approval'] is not None:
                transfer.Transfer_approval = args['Transfer_approval']
            if args['Remarks'] is not None:
                transfer.Remarks = args['Remarks']
            if args['status'] is not None:
                transfer.status = args['status']
            if args['CampusId'] is not None:
                transfer.CampusId = args['CampusId']
            if args['CreatorId'] is not None:
                transfer.CreatorId = args['CreatorId']
            if args['CreateDate'] is not None:
                transfer.CreateDate = args['CreateDate']
            if args['UpdaterId'] is not None:
                transfer.UpdaterId = args['UpdaterId']
            if args['UpdateDate'] is not None:
                transfer.UpdateDate = datetime.utcnow() + timedelta(hours=5)

            db.session.commit()
            return {"message": "Staff transfer updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        try:
            transfer = StaffTransfer.query.get_or_404(id)
            db.session.delete(transfer)
            db.session.commit()
            return {"message": "Staff transfer deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

class StaffShiftResource(Resource):
    def get(self, staff_id=None):
        try:
            if staff_id:
                staff_shift = StaffShifts.query.get(staff_id)
                if staff_shift is None:
                    return {"message": f"StaffShift with StaffId {staff_id} not found"}, 404
                return staff_shift.to_dict(), 200
            else:
                staff_shifts = StaffShifts.query.all()
                return [shift.to_dict() for shift in staff_shifts], 200
        except SQLAlchemyError as e:
            return {"error": f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('StaffId', type=int, required=True)
        parser.add_argument('ShiftId', type=int, required=True)
        parser.add_argument('CreatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True)
        parser.add_argument('UpdatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CreatedByUserId', type=int, required=True)
        parser.add_argument('UpdatedByUserId', type=int, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        args = parser.parse_args()

        try:
            new_shift = StaffShifts(
                StaffId=args['StaffId'],
                ShiftId=args['ShiftId'],
                CreatedOn=args['CreatedOn'],
                UpdatedOn=args.get('UpdatedOn'),
                CreatedByUserId=args['CreatedByUserId'],
                UpdatedByUserId=args.get('UpdatedByUserId'),
                CampusId=args.get('CampusId')
            )
            db.session.add(new_shift)
            db.session.commit()
            return {"status": "success",
                    "message": "StaffShift created successfully", "StaffId": new_shift.StaffId}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error",
                    "message": f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"status": "error",
                    "message": f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, staff_id, shift_id):
        parser = reqparse.RequestParser()
        parser.add_argument('ShiftId', type=int, required=True)
        parser.add_argument('UpdatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('UpdatedByUserId', type=int, required=False)
        args = parser.parse_args()

        try:
            # Retrieve the record using the composite key
            staff_shift = StaffShifts.query.get((staff_id, shift_id))
            if staff_shift is None:
                return {"status": "error",
                        "message": f"StaffShifts with StaffId {staff_id} and ShiftId {shift_id} not found"}, 404

            # Update the record with provided data
            if args['UpdatedOn'] is not None:
                staff_shift.UpdatedOn = args['UpdatedOn']
            if args['ShiftId'] is not None:
                staff_shift.ShiftId = args['ShiftId']
            if args['UpdatedByUserId'] is not None:
                staff_shift.UpdatedByUserId = args['UpdatedByUserId']
            
            db.session.commit()
            return {"status": "success",
                    "message": "StaffShifts updated successfully", "StaffId": staff_shift.StaffId, "ShiftId": staff_shift.ShiftId}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error",
                    "message": f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"status": "error",
                    "message": f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, staff_id, shift_id):
        try:
            staff_shift = StaffShifts.query.get((staff_id, shift_id))
            if staff_shift is None:
                return {"status": "error",
                        "message": f"StaffShifts with StaffId {staff_id} and ShiftId {shift_id} not found"}, 404

            db.session.delete(staff_shift)
            db.session.commit()
            return {"status": "success",
                    "message": "StaffShifts deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error",
                    "message": f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"status": "error",
                    "message": f"An unexpected error occurred: {str(e)}"}, 500

class SalaryResource(Resource):
    
    def get(self, salary_id):
        """
        Handles the retrieval of a salary record by its ID.
        """
        try:
            salary = Salaries.query.get(salary_id)
            if salary:
                return salary.to_dict(), 200
            else:
                return {'message': 'Salary record not found'}, 404
        except SQLAlchemyError as e:
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        """
        Handles the creation of a new salary record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('BasicAmount', type=float, required=True, help='BasicAmount is required')
        parser.add_argument('AllowancesAmount', type=float, required=True, help='AllowancesAmount is required')
        parser.add_argument('TotalAmount', type=float, required=True, help='TotalAmount is required')
        parser.add_argument('AnnualLeaves', type=int, required=True, help='AnnualLeaves is required')
        parser.add_argument('RemainingAnnualLeaves', type=int, required=True, help='RemainingAnnualLeaves is required')
        parser.add_argument('DailyHours', type=int, required=True, help='DailyHours is required')
        parser.add_argument('PFAmount', type=float, required=True, help='PFAmount is required')
        parser.add_argument('EOBIAmount', type=float, required=True, help='EOBIAmount is required')
        parser.add_argument('SESSIAmount', type=float, required=True, help='SESSIAmount is required')
        parser.add_argument('SalaryMode', type=int, required=True, help='SalaryMode is required')
        parser.add_argument('IsProbationPeriod', type=bool, required=True, help='IsProbationPeriod is required')
        parser.add_argument('From', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help='From date is required')
        parser.add_argument('To', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help='To date is required')
        parser.add_argument('EmployeeId', type=int, required=True, help='EmployeeId is required')
        parser.add_argument('CreatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help='CreatedOn date is required')
        parser.add_argument('UpdatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), help='UpdatedOn date is optional')
        parser.add_argument('InActiveOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), help='InActiveOn date is optional')
        parser.add_argument('CreatedByUserId', type=int, required=True, help='CreatedByUserId is required')
        parser.add_argument('UpdatedByUserId', type=int, help='UpdatedByUserId is optional')
        parser.add_argument('InActiveByUserId', type=int, help='InActiveByUserId is optional')
        parser.add_argument('HouseRent', type=float, help='HouseRent is optional')
        parser.add_argument('MedicalAllowance', type=float, help='MedicalAllowance is optional')
        parser.add_argument('UtilityAllowance', type=float, help='UtilityAllowance is optional')
        parser.add_argument('IncomeTax', type=float, help='IncomeTax is optional')
        parser.add_argument('Toil', type=float, help='Toil is optional')
        parser.add_argument('ConveyanceAllowance', type=float, help='ConveyanceAllowance is optional')
        parser.add_argument('StaffLunch', type=float, help='StaffLunch is optional')
        parser.add_argument('CasualLeaves', type=int, help='CasualLeaves is optional')
        parser.add_argument('SickLeaves', type=int, help='SickLeaves is optional')
        parser.add_argument('RemainingCasualLeaves', type=int, required=True, help='RemainingCasualLeaves is required')
        parser.add_argument('RemainingSickLeaves', type=int, required=True, help='RemainingSickLeaves is required')
        parser.add_argument('StudyLeaves', type=int, help='StudyLeaves is optional')
        parser.add_argument('RemainingStudyLeaves', type=int, required=True, help='RemainingStudyLeaves is required')
        parser.add_argument('Loan', type=int, required=True, help='Loan is required')
        parser.add_argument('Arrears', type=int, required=True, help='Arrears is required')

        args = parser.parse_args()

        try:
            new_salary = Salaries(
                BasicAmount=args['BasicAmount'],
                AllowancesAmount=args['AllowancesAmount'],
                TotalAmount=args['TotalAmount'],
                AnnualLeaves=args['AnnualLeaves'],
                RemainingAnnualLeaves=args['RemainingAnnualLeaves'],
                DailyHours=args['DailyHours'],
                PFAmount=args['PFAmount'],
                EOBIAmount=args['EOBIAmount'],
                SESSIAmount=args['SESSIAmount'],
                SalaryMode=args['SalaryMode'],
                IsProbationPeriod=args['IsProbationPeriod'],
                From=args['From'],
                To=args['To'],
                EmployeeId=args['EmployeeId'],
                CreatedOn=args['CreatedOn'],
                UpdatedOn=args.get('UpdatedOn'),
                InActiveOn=args.get('InActiveOn'),
                CreatedByUserId=args['CreatedByUserId'],
                UpdatedByUserId=args.get('UpdatedByUserId'),
                InActiveByUserId=args.get('InActiveByUserId'),
                HouseRent=args.get('HouseRent'),
                MedicalAllowance=args.get('MedicalAllowance'),
                UtilityAllowance=args.get('UtilityAllowance'),
                IncomeTax=args.get('IncomeTax'),
                Toil=args.get('Toil'),
                ConveyanceAllowance=args.get('ConveyanceAllowance'),
                StaffLunch=args.get('StaffLunch'),
                CasualLeaves=args.get('CasualLeaves'),
                SickLeaves=args.get('SickLeaves'),
                RemainingCasualLeaves=args['RemainingCasualLeaves'],
                RemainingSickLeaves=args['RemainingSickLeaves'],
                StudyLeaves=args.get('StudyLeaves'),
                RemainingStudyLeaves=args['RemainingStudyLeaves'],
                Loan=args['Loan'],
                Arrears=args['Arrears']
            )

            db.session.add(new_salary)
            db.session.commit()
            return {"message": "Salary record created successfully", "salary": new_salary.to_dict()}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500


            salary.UpdatedOn = datetime.utcnow() + timedelta(hours=5)

            db.session.commit()
            return {"message": "Salary record updated successfully", "salary": salary.to_dict()}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, salary_id):
        """
        Handles deleting a salary record by its ID.
        """
        try:
            salary = Salaries.query.get(salary_id)
            if not salary:
                return {'message': 'Salary record not found'}, 404

            db.session.delete(salary)
            db.session.commit()
            return {"message": "Salary record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class MarkDayOffDepsResource(Resource):
    
    def get(self, id=None):
        """
        Retrieve a single MarkDayOffDeps record by ID or all records if no ID is provided.
        """
        if id:
            mark_day_off = MarkDayOffDeps.query.get(id)
            if mark_day_off:
                return mark_day_off.to_dict(), 200
            return {'message': 'MarkDayOffDeps record not found'}, 404
        else:
            mark_days_off = MarkDayOffDeps.query.all()
            return [mark_day_off.to_dict() for mark_day_off in mark_days_off], 200

    def post(self):
        """
        Create a new MarkDayOffDeps record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Date', type=str, required=True, help='Date is required')
        parser.add_argument('Staff_Id', type=int, required=True, help='Staff ID is required')
        parser.add_argument('Description', type=str, required=False)
        parser.add_argument('CreatorId', type=int, required=True, help='Creator ID is required')
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        parser.add_argument('AcademicYearId', type=int, required=False)
        
        args = parser.parse_args()

        try:
            mark_day_off = MarkDayOffDeps(
                Date=datetime.fromisoformat(args['Date']),
                Staff_Id=args['Staff_Id'],
                Description=args.get('Description'),
                CreatorId=args['CreatorId'],
                CreateDate=datetime.utcnow() + timedelta(hours=5),
                status=args.get('status'),
                CampusId=args.get('CampusId'),
                AcademicYearId=args.get('AcademicYearId')
            )

            db.session.add(mark_day_off)
            db.session.commit()

            return {"message": "MarkDayOffDeps record created successfully"}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self):
        """
        Update existing MarkDayOffDeps records for multiple staff members.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Date', type=str, required=False)
        parser.add_argument('Staff_Ids', type=int, action='append', required=True, help='Staff IDs are required')
        parser.add_argument('Description', type=str, required=False)
        parser.add_argument('UpdatorId', type=int, required=True, help='Updator ID is required')
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        parser.add_argument('AcademicYearId', type=int, required=False)
        
        args = parser.parse_args()

        try:
            
            updated_records = []
            for staff_id in args['Staff_Ids']:
                
                mark_day_off = MarkDayOffDeps.query.filter_by(Staff_Id=staff_id).first()
                
                if not mark_day_off:
                    continue  # Skip if the record does not exist

                if args['Date']:
                    mark_day_off.Date = datetime.fromisoformat(args['Date'])
                if args['Description']:
                    mark_day_off.Description = args['Description']
                if args['status'] is not None:
                    mark_day_off.status = args['status']
                if args['CampusId']:
                    mark_day_off.CampusId = args['CampusId']
                if args['AcademicYearId']:
                    mark_day_off.AcademicYearId = args['AcademicYearId']

                mark_day_off.UpdatorId = args['UpdatorId']
                mark_day_off.UpdateDate = datetime.utcnow() + timedelta(hours=5)

                updated_records.append(mark_day_off.to_dict())
            
            db.session.commit()

            return {"message": "MarkDayOffDeps records updated successfully", "MarkDayOffDeps": updated_records}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete a MarkDayOffDeps record by ID.
        """
        try:
            mark_day_off = MarkDayOffDeps.query.get(id)
            if not mark_day_off:
                return {'message': 'MarkDayOffDeps record not found'}, 404

            db.session.delete(mark_day_off)
            db.session.commit()

            return {"message": "MarkDayOffDeps record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class MarkDayOffHRsResource(Resource):
    def get(self, id=None):
        """
        Retrieve a single MarkDayOffHRs record by ID or all records if no ID is provided.
        """
        if id:
            mark_day_off = MarkDayOffHRs.query.get(id)
            if mark_day_off:
                return mark_day_off.to_dict(), 200
            return {'message': 'MarkDayOffHRs record not found'}, 404
        else:
            mark_days_off = MarkDayOffHRs.query.all()
            return [mark_day_off.to_dict() for mark_day_off in mark_days_off], 200

    def post(self):
        """
        Create new MarkDayOffHRs records for multiple campuses.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Date', type=str, required=True, help='Date is required')
        parser.add_argument('CampusIds', type=int, action='append', required=True, help='Campus IDs are required')
        parser.add_argument('Description', type=str, required=False)
        parser.add_argument('CreatorId', type=int, required=True, help='Creator ID is required')
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('AcademicYearId', type=int, required=False)
        
        args = parser.parse_args()

        try:
            created_records = []
            for campus_id in args['CampusIds']:
                mark_day_off = MarkDayOffHRs(
                    Date=datetime.fromisoformat(args['Date']),
                    CampusIds=campus_id,
                    Description=args.get('Description'),
                    CreatorId=args['CreatorId'],
                    CreateDate=datetime.utcnow() + timedelta(hours=5),
                    Status=args.get('Status'),
                    AcademicYearId=args.get('AcademicYearId')
                )
                db.session.add(mark_day_off)
                created_records.append(mark_day_off.to_dict())
            
            db.session.commit()

            return {"message": "MarkDayOffHRs records created successfully"}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self):
        """
        Update existing MarkDayOffHRs records for multiple campuses.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Date', type=str, required=False)
        parser.add_argument('CampusIds', type=int, action='append', required=True, help='Campus IDs are required')
        parser.add_argument('Description', type=str, required=False)
        parser.add_argument('UpdatorId', type=int, required=True, help='Updator ID is required')
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('AcademicYearId', type=int, required=False)
        
        args = parser.parse_args()

        try:
            updated_records = []
            for campus_id in args['CampusIds']:
                mark_day_off = MarkDayOffHRs.query.filter_by(CampusIds=campus_id).first()
                if not mark_day_off:
                    continue  # Skip if the record does not exist

                if args['Date']:
                    mark_day_off.Date = datetime.fromisoformat(args['Date'])
                if args['Description']:
                    mark_day_off.Description = args['Description']
                if args['Status'] is not None:
                    mark_day_off.status = args['status']
                if args['AcademicYearId']:
                    mark_day_off.AcademicYearId = args['AcademicYearId']

                mark_day_off.UpdatorId = args['UpdatorId']
                mark_day_off.UpdateDate = datetime.utcnow() + timedelta(hours=5)

                updated_records.append(mark_day_off.to_dict())
            
            db.session.commit()

            return {"message": "MarkDayOffHRs records updated successfully", "MarkDayOffHRs": updated_records}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete a MarkDayOffHRs record by ID.
        """
        try:
            mark_day_off = MarkDayOffHRs.query.get(id)
            if not mark_day_off:
                return {'message': 'MarkDayOffHRs record not found'}, 404

            db.session.delete(mark_day_off)
            db.session.commit()

            return {"message": "MarkDayOffHRs record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class AllowanceHeadResource(Resource):
    def get(self, id=None):
        """
        Retrieve a single AllowanceHead record by ID or all records if no ID is provided.
        """
        if id:
            allowance_head = AllowanceHead.query.get(id)
            if allowance_head:
                return allowance_head.to_dict(), 200
            return {'message': 'AllowanceHead record not found'}, 404
        else:
            allowance_heads = AllowanceHead.query.all()
            return [allowance_head.to_dict() for allowance_head in allowance_heads], 200

    def post(self):
        """
        Create a new AllowanceHead record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('AllowanceHead_Name', type=str, required=True, help='AllowanceHead Name is required')
        args = parser.parse_args()

        try:
            allowance_head = AllowanceHead(
                AllowanceHead_Name=args['AllowanceHead_Name']
            )
            db.session.add(allowance_head)
            db.session.commit()

            return {"message": "AllowanceHead record created successfully", "AllowanceHead_Id": allowance_head.AllowanceHead_Id}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, id):
        """
        Update an existing AllowanceHead record by ID.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('AllowanceHead_Name', type=str, required=True, help='AllowanceHead Name is required')
        args = parser.parse_args()

        try:
            allowance_head = AllowanceHead.query.get(id)
            if not allowance_head:
                return {'message': 'AllowanceHead record not found'}, 404

            allowance_head.AllowanceHead_Name = args['AllowanceHead_Name']
            db.session.commit()

            return {"message": "AllowanceHead record updated successfully", "AllowanceHead": allowance_head.to_dict()}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete an AllowanceHead record by ID.
        """
        try:
            allowance_head = AllowanceHead.query.get(id)
            if not allowance_head:
                return {'message': 'AllowanceHead record not found'}, 404

            db.session.delete(allowance_head)
            db.session.commit()

            return {"message": "AllowanceHead record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class OneTimeAllowanceResource(Resource):

    def get(self, id=None):
        """
        Retrieve a single OneTimeAllowance record by ID or all records if no ID is provided.
        """
        if id:
            one_time_allowance = OneTimeAllowance.query.get(id)
            if one_time_allowance:
                return one_time_allowance.to_dict(), 200
            return {'message': 'OneTimeAllowance record not found'}, 404
        else:
            one_time_allowances = OneTimeAllowance.query.all()
            return [one_time_allowance.to_dict() for one_time_allowance in one_time_allowances], 200

    def post(self):
        """
        Create a new OneTimeAllowance record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('OneTimeAllowance_StaffId', type=int, required=True, help='Staff ID is required')
        parser.add_argument('OneTimeAllowance_AllowanceHeadId', type=int, required=True, help='Allowance Head ID is required')
        parser.add_argument('OneTimeAllowance_Amount', type=float, required=True, help='Amount is required')
        parser.add_argument('OneTimeAllowance_PamentMonth', type=str, required=True, help='Payment Month is required')
        parser.add_argument('OneTimeAllowance_ApprovedBy', type=int, required=True, help='Approved By is required')
        parser.add_argument('OneTimeAllowance_Taxable', type=bool, required=True, help='Taxable is required')
        parser.add_argument('CreatorId', type=int, required=True, help='Creator ID is required')
        args = parser.parse_args()

        try:
            one_time_allowance = OneTimeAllowance(
                OneTimeAllowance_StaffId=args['OneTimeAllowance_StaffId'],
                OneTimeAllowance_AllowanceHeadId=args['OneTimeAllowance_AllowanceHeadId'],
                OneTimeAllowance_Amount=args['OneTimeAllowance_Amount'],
                OneTimeAllowance_PamentMonth=args['OneTimeAllowance_PamentMonth'],
                OneTimeAllowance_ApprovedBy=args['OneTimeAllowance_ApprovedBy'],
                OneTimeAllowance_Taxable=args['OneTimeAllowance_Taxable'],
                CreatorId=args['CreatorId'],
                CreateDate=datetime.utcnow() + timedelta(hours=5)
            )
            db.session.add(one_time_allowance)
            db.session.commit()

            return {"message": "OneTimeAllowance record created successfully", "OneTimeAllowance": one_time_allowance.to_dict()}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, id):
        """
        Update an existing OneTimeAllowance record by ID.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('OneTimeAllowance_StaffId', type=int, required=True, help='Staff ID is required')
        parser.add_argument('OneTimeAllowance_AllowanceHeadId', type=int, required=True, help='Allowance Head ID is required')
        parser.add_argument('OneTimeAllowance_Amount', type=float, required=True, help='Amount is required')
        parser.add_argument('OneTimeAllowance_PamentMonth', type=str, required=True, help='Payment Month is required')
        parser.add_argument('OneTimeAllowance_ApprovedBy', type=int, required=True, help='Approved By is required')
        parser.add_argument('OneTimeAllowance_Taxable', type=bool, required=True, help='Taxable is required')
        parser.add_argument('UpdatorId', type=int, required=True, help='Updator ID is required')
        args = parser.parse_args()

        try:
            one_time_allowance = OneTimeAllowance.query.get(id)
            if not one_time_allowance:
                return {'message': 'OneTimeAllowance record not found'}, 404
            
            try:
                one_time_allowance = OneTimeAllowance(
                    OneTimeAllowanceHistory_OneTimeAllowance_Id = id,
                    OneTimeAllowanceHistory_StaffId= one_time_allowance.OneTimeAllowance_StaffId,
                    OneTimeAllowanceHistory_AllowanceHeadId= one_time_allowance.OneTimeAllowance_AllowanceHeadId,
                    OneTimeAllowanceHistory_Amount= one_time_allowance.OneTimeAllowance_Amount,
                    OneTimeAllowanceHistory_PamentMonth= one_time_allowance.OneTimeAllowance_PamentMonth,
                    OneTimeAllowanceHistory_ApprovedBy= one_time_allowance.OneTimeAllowance_ApprovedBy,
                    OneTimeAllowanceHistory_Taxable= one_time_allowance.OneTimeAllowance_Taxable,
                    CreatorId= one_time_allowance.CreatorId,
                    CreateDate= one_time_allowance.CreateDate,
                    UpdatorId= args['UpdatorId'],
                    UpdateDate = datetime.utcnow() + timedelta(hours=5),
                    InActive = 0
                )
                db.session.add(one_time_allowance)
                db.session.commit()

                # return {"message": "OneTimeAllowance record created successfully", "OneTimeAllowance": one_time_allowance.to_dict()}, 201
            except SQLAlchemyError as e:
                db.session.rollback()
                return {'error': f"Database error occurred: {str(e)}"}, 500
            except Exception as e:
                db.session.rollback()
                return {'error': f"An unexpected error occurred: {str(e)}"}, 500

            one_time_allowance.OneTimeAllowance_StaffId = args['OneTimeAllowance_StaffId']
            one_time_allowance.OneTimeAllowance_AllowanceHeadId = args['OneTimeAllowance_AllowanceHeadId']
            one_time_allowance.OneTimeAllowance_Amount = args['OneTimeAllowance_Amount']
            one_time_allowance.OneTimeAllowance_PamentMonth = args['OneTimeAllowance_PamentMonth']
            one_time_allowance.OneTimeAllowance_ApprovedBy = args['OneTimeAllowance_ApprovedBy']
            one_time_allowance.OneTimeAllowance_Taxable = args['OneTimeAllowance_Taxable']
            one_time_allowance.UpdatorId = args['UpdatorId']
            one_time_allowance.UpdateDate = datetime.utcnow() + timedelta(hours=5)

            db.session.commit()

            return {"message": "OneTimeAllowance record updated successfully", "OneTimeAllowance": one_time_allowance.to_dict()}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete a OneTimeAllowance record by ID.
        """
        try:
            one_time_allowance = OneTimeAllowance.query.get(id)
            if not one_time_allowance:
                return {'message': 'OneTimeAllowance record not found'}, 404

            db.session.delete(one_time_allowance)
            db.session.commit()

            return {"message": "OneTimeAllowance record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class ScheduledAllowanceResource(Resource):

    def get(self, id=None):
        """
        Retrieve a single ScheduledAllowance record by ID or all records if no ID is provided.
        """
        if id:
            scheduled_allowance = ScheduledAllowance.query.get(id)
            if scheduled_allowance:
                return scheduled_allowance.to_dict(), 200
            return {'message': 'ScheduledAllowance record not found'}, 404
        else:
            scheduled_allowances = ScheduledAllowance.query.all()
            return [scheduled_allowance.to_dict() for scheduled_allowance in scheduled_allowances], 200

    def post(self):
        """
        Create a new ScheduledAllowance record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('ScheduledAllowance_StaffId', type=int, required=True, help='Staff ID is required')
        parser.add_argument('ScheduledAllowance_AllowanceHeadId', type=int, required=True, help='Allowance Head ID is required')
        parser.add_argument('ScheduledAllowance_AmountPerMonth', type=float, required=True, help='Amount Per Month is required')
        parser.add_argument('ScheduledAllowance_StartDate', type=str, required=True, help='Start Date is required')
        parser.add_argument('ScheduledAllowance_EndDate', type=str, required=True, help='End Date is required')
        parser.add_argument('ScheduledAllowance_ApprovedBy', type=int, required=True, help='Approved By is required')
        parser.add_argument('CreatorId', type=int, required=True, help='Creator ID is required')
        parser.add_argument('ScheduledAllowance_Taxable', type=bool, required=True, help='Taxable is required')
        args = parser.parse_args()

        try:
            scheduled_allowance = ScheduledAllowance(
                ScheduledAllowance_StaffId=args['ScheduledAllowance_StaffId'],
                ScheduledAllowance_AllowanceHeadId=args['ScheduledAllowance_AllowanceHeadId'],
                ScheduledAllowance_AmountPerMonth=args['ScheduledAllowance_AmountPerMonth'],
                ScheduledAllowance_StartDate=datetime.fromisoformat(args['ScheduledAllowance_StartDate']),
                ScheduledAllowance_EndDate=datetime.fromisoformat(args['ScheduledAllowance_EndDate']),
                ScheduledAllowance_ApprovedBy=args['ScheduledAllowance_ApprovedBy'],
                CreatorId=args['CreatorId'],
                CreateDate=datetime.utcnow() + timedelta(hours=5),
                ScheduledAllowance_Taxable=args['ScheduledAllowance_Taxable']
            )
            db.session.add(scheduled_allowance)
            db.session.commit()

            return {"message": "ScheduledAllowance record created successfully", "ScheduledAllowance": scheduled_allowance.to_dict()}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, id):
        """
        Update an existing ScheduledAllowance record by ID.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('ScheduledAllowance_StaffId', type=int, required=True, help='Staff ID is required')
        parser.add_argument('ScheduledAllowance_AllowanceHeadId', type=int, required=True, help='Allowance Head ID is required')
        parser.add_argument('ScheduledAllowance_AmountPerMonth', type=float, required=True, help='Amount Per Month is required')
        parser.add_argument('ScheduledAllowance_StartDate', type=str, required=True, help='Start Date is required')
        parser.add_argument('ScheduledAllowance_EndDate', type=str, required=True, help='End Date is required')
        parser.add_argument('ScheduledAllowance_ApprovedBy', type=int, required=True, help='Approved By is required')
        parser.add_argument('UpdatorId', type=int, required=True, help='Updator ID is required')
        parser.add_argument('ScheduledAllowance_Taxable', type=bool, required=True, help='Taxable is required')
        args = parser.parse_args()

        try:
            scheduled_allowance = ScheduledAllowance.query.get(id)
            if not scheduled_allowance:
                return {'message': 'ScheduledAllowance record not found'}, 404

            scheduled_allowance.ScheduledAllowance_StaffId = args['ScheduledAllowance_StaffId']
            scheduled_allowance.ScheduledAllowance_AllowanceHeadId = args['ScheduledAllowance_AllowanceHeadId']
            scheduled_allowance.ScheduledAllowance_AmountPerMonth = args['ScheduledAllowance_AmountPerMonth']
            scheduled_allowance.ScheduledAllowance_StartDate = datetime.fromisoformat(args['ScheduledAllowance_StartDate'])
            scheduled_allowance.ScheduledAllowance_EndDate = datetime.fromisoformat(args['ScheduledAllowance_EndDate'])
            scheduled_allowance.ScheduledAllowance_ApprovedBy = args['ScheduledAllowance_ApprovedBy']
            scheduled_allowance.UpdatorId = args['UpdatorId']
            scheduled_allowance.UpdateDate = datetime.utcnow() + timedelta(hours=5)
            scheduled_allowance.ScheduledAllowance_Taxable = args['ScheduledAllowance_Taxable']

            db.session.commit()

            return {"message": "ScheduledAllowance record updated successfully", "ScheduledAllowance": scheduled_allowance.to_dict()}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete a ScheduledAllowance record by ID.
        """
        try:
            scheduled_allowance = ScheduledAllowance.query.get(id)
            if not scheduled_allowance:
                return {'message': 'ScheduledAllowance record not found'}, 404

            db.session.delete(scheduled_allowance)
            db.session.commit()

            return {"message": "ScheduledAllowance record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class StaffIncrementResource(Resource):
    def get(self, staff_increment_id=None):
        if staff_increment_id:
            staff_increment = StaffIncrement.query.get(staff_increment_id)
            if staff_increment:
                return jsonify(staff_increment.to_dict())
            else:
                return {'error': 'StaffIncrement not found'}, 404
        else:
            staff_increments = StaffIncrement.query.all()
            return jsonify([si.to_dict() for si in staff_increments])

    """
        def post(self):
            data = request.get_json()
            try:
                new_staff_increment = StaffIncrement(
                    StaffIncrement_StaffId=data['StaffIncrement_StaffId'],
                    StaffIncrement_CurrentSalary=data['StaffIncrement_CurrentSalary'],
                    StaffIncrement_Date=datetime.strptime(data['StaffIncrement_Date'], '%Y-%m-%dT%H:%M:%S'),
                    StaffIncrement_Reason=data['StaffIncrement_Reason'],
                    StaffIncrement_Others=data.get('StaffIncrement_Others'),
                    StaffIncrement_NewSalary=data['StaffIncrement_NewSalary'],
                    StaffIncrement_PercentageIncrease=data['StaffIncrement_PercentageIncrease'],
                    StaffIncrement_InitiatedBy=data['StaffIncrement_InitiatedBy'],
                    StaffIncrement_Approval=data['StaffIncrement_Approval'],
                    StaffIncrement_Remarks=data['StaffIncrement_Remarks'],
                    CreatedBy=data['CreatedBy'],
                    CreatedDate=datetime.utcnow() + timedelta(hours=5),
                    InActive=0
                )
                db.session.add(new_staff_increment)
                db.session.commit()
                
                self.create_employee_salary(new_staff_increment.StaffIncrement_StaffId, new_staff_increment.StaffIncrement_NewSalary)
                return jsonify(new_staff_increment.to_dict()), 201
            except SQLAlchemyError as e:
                db.session.rollback()
                return {'error': str(e)}, 500

        def create_employee_salary(self, staff_id, total_salary):
            
            # Creates a new salary record for the given staff ID.
            
            try:
                staff_info = StaffInfo.query.get(staff_id)
                if not staff_info:
                    return {
                        "error": "Unsuccessful",
                        "message": "No record found"
                    }

                salary_info = Salaries.query.filter(EmployeeId=staff_id)
                
                if not salary_info:
                    return {
                        "error": "Unsuccessful",
                        "message": "No record found"
                    }
                salary_info.InActive = 1
                db.session.commit()
                
                is_non_teacher = staff_info.IsNonTeacher
                basic = total_salary / 2

                new_salary = Salaries(
                    BasicAmount=basic,
                    AllowancesAmount=basic,
                    TotalAmount=total_salary,
                    AnnualLeaves=10,
                    RemainingAnnualLeaves=10,
                    DailyHours=8,
                    PFAmount=basic / 12,
                    EOBIAmount=basic / 12,
                    SESSIAmount=basic / 12,
                    SalaryMode=1,
                    IsProbationPeriod=False,
                    From=datetime.utcnow() + timedelta(hours=5),
                    To=datetime.utcnow() + timedelta(hours=5),
                    EmployeeId=staff_id,
                    CreatedOn=datetime.utcnow() + timedelta(hours=5),
                    CreatedByUserId=get_jwt_identity(),
                    HouseRent=basic / 2,
                    MedicalAllowance=basic / 10,
                    UtilityAllowance=basic / 5,
                    IncomeTax=0,
                    Toil=0,
                    ConveyanceAllowance=basic / 5,
                    StaffLunch=0,
                    CasualLeaves=12 if is_non_teacher else 10,
                    SickLeaves=7,
                    RemainingCasualLeaves=12 if is_non_teacher else 10,
                    RemainingSickLeaves=7,
                    StudyLeaves=5,
                    RemainingStudyLeaves=5,
                    Loan=0,
                    Arrears=0
                )

                db.session.add(new_salary)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error creating employee salary: {str(e)}")
        def put:
            data = request.get_json()
        try:
            staff_increment = StaffIncrement.query.get(staff_increment_id)
            if staff_increment:
                staff_increment.StaffIncrement_StaffId = data.get('StaffIncrement_StaffId', staff_increment.StaffIncrement_StaffId)
                staff_increment.StaffIncrement_CurrentSalary = data.get('StaffIncrement_CurrentSalary', staff_increment.StaffIncrement_CurrentSalary)
                staff_increment.StaffIncrement_Date = datetime.strptime(data['StaffIncrement_Date'], '%Y-%m-%dT%H:%M:%S') if 'StaffIncrement_Date' in data else staff_increment.StaffIncrement_Date
                staff_increment.StaffIncrement_Reason = data.get('StaffIncrement_Reason', staff_increment.StaffIncrement_Reason)
                staff_increment.StaffIncrement_Others = data.get('StaffIncrement_Others', staff_increment.StaffIncrement_Others)
                staff_increment.StaffIncrement_NewSalary = data.get('StaffIncrement_NewSalary', staff_increment.StaffIncrement_NewSalary)
                staff_increment.StaffIncrement_PercentageIncrease = data.get('StaffIncrement_PercentageIncrease', staff_increment.StaffIncrement_PercentageIncrease)
                staff_increment.StaffIncrement_InitiatedBy = data.get('StaffIncrement_InitiatedBy', staff_increment.StaffIncrement_InitiatedBy)
                staff_increment.StaffIncrement_Approval = data.get('StaffIncrement_Approval', staff_increment.StaffIncrement_Approval)
                staff_increment.StaffIncrement_Remarks = data.get('StaffIncrement_Remarks', staff_increment.StaffIncrement_Remarks)
                staff_increment.UpdatedBy = data.get('UpdatedBy', staff_increment.UpdatedBy)
                staff_increment.UpdatedDate = datetime.utcnow() + timedelta(hours=5)
                staff_increment.InActive = data.get('InActive', staff_increment.InActive)
                
                db.session.commit()
                return jsonify(staff_increment.to_dict()), 200
            else:
                return {'error': 'StaffIncrement not found'}, 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    """

    def post(self):
        data = request.get_json()
        flag = False
        try:
            # Check if the Staff ID exists
            staff_info = StaffInfo.query.get(data['StaffIncrement_StaffId'])
            if not staff_info:
                return jsonify({"error": "Staff not found."}), 404

            staff_increment_info = StaffIncrement.query.filter_by(StaffIncrement_StaffId=data['StaffIncrement_StaffId'], InActive=False).first()
        
            if staff_increment_info:
                staff_increment_info.InActive = 1
                db.session.commit()
                flag = True
                
            new_staff_increment = StaffIncrement(
                StaffIncrement_StaffId=data['StaffIncrement_StaffId'],
                StaffIncrement_CurrentSalary=data['StaffIncrement_CurrentSalary'],
                StaffIncrement_Date=datetime.strptime(data['StaffIncrement_Date'], '%Y-%m-%dT%H:%M:%S'),
                StaffIncrement_Reason=data['StaffIncrement_Reason'],
                StaffIncrement_Others=data.get('StaffIncrement_Others'),
                StaffIncrement_NewSalary=data['StaffIncrement_NewSalary'],
                StaffIncrement_PercentageIncrease=data['StaffIncrement_PercentageIncrease'],
                StaffIncrement_InitiatedBy=data['StaffIncrement_InitiatedBy'],
                StaffIncrement_Approval=data['StaffIncrement_Approval'],
                StaffIncrement_Remarks=data['StaffIncrement_Remarks'],
                CreatedBy=data['CreatedBy'],
                CreatedDate=datetime.utcnow() + timedelta(hours=5),
                InActive=0
            )
            db.session.add(new_staff_increment)
            db.session.commit()

            if flag:
                new_salary_Id = self.update_employee_salary(new_staff_increment.StaffIncrement_StaffId, new_staff_increment.StaffIncrement_NewSalary, data['CreatedBy'])    
            else:
                new_salary_Id = self.create_employee_salary(new_staff_increment.StaffIncrement_StaffId, new_staff_increment.StaffIncrement_NewSalary, data['CreatedBy'])
                
            return {'status': 'success',
                'message': 'Records inserted into `StaffIncrement` successfully'}, 201
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    def create_employee_salary(self, staff_id, total_salary, user_id):
        try:
            staff_info = StaffInfo.query.get(staff_id)
            if not staff_info:
                return {"error": "Unsuccessful", "message": "No record found"}

            salary_info = Salaries.query.filter_by(EmployeeId=staff_id, IsActive=1).all()
            print(salary_info)
            if not salary_info:
                is_non_teacher = staff_info.IsNonTeacher
                basic = total_salary / 2

                new_salary = Salaries(
                    BasicAmount=basic,
                    AllowancesAmount=basic,
                    TotalAmount=total_salary,
                    AnnualLeaves=10,
                    RemainingAnnualLeaves=10,
                    DailyHours=8,
                    PFAmount=basic / 12,
                    EOBIAmount=basic / 12,
                    SESSIAmount=basic / 12,
                    SalaryMode=1,
                    IsProbationPeriod=False,
                    From=datetime.utcnow() + timedelta(hours=5),
                    To=datetime.utcnow() + timedelta(hours=5),
                    EmployeeId=staff_id,
                    CreatedOn=datetime.utcnow() + timedelta(hours=5),
                    CreatedByUserId=user_id,
                    HouseRent=basic / 2,
                    MedicalAllowance=basic / 10,
                    UtilityAllowance=basic / 5,
                    IncomeTax=0,
                    Toil=0,
                    ConveyanceAllowance=basic / 5,
                    StaffLunch=0,
                    CasualLeaves=12 if is_non_teacher else 10,
                    SickLeaves=7,
                    RemainingCasualLeaves=12 if is_non_teacher else 10,
                    RemainingSickLeaves=7,
                    StudyLeaves=5,
                    RemainingStudyLeaves=5,
                    Loan=0,
                    Arrears=0,
                    IsActive=1
                )

                db.session.add(new_salary)
                db.session.commit()

                return new_salary.Id
            else:
                new_salary_Id = self.update_employee_salary(staff_id, total_salary, user_id)
                return new_salary_Id
        except Exception as e:
            db.session.rollback()
            print(f"Error creating employee salary: {str(e)}")
            return {"error": "Error creating employee salary", "message": str(e)}

    def put(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('StaffIncrement_Id', type=int, required=True, help='StaffIncrement_Id is required')
        self.parser.add_argument('StaffIncrement_StaffId', type=int, required=True, help='StaffIncrement_StaffId is required')
        self.parser.add_argument('StaffIncrement_CurrentSalary', type=float, required=True, help='StaffIncrement_CurrentSalary is required')
        self.parser.add_argument('StaffIncrement_Date', type=str, required=True, help='StaffIncrement_Date is required')
        self.parser.add_argument('StaffIncrement_Reason', type=int, required=True, help='StaffIncrement_Reason is required')
        self.parser.add_argument('StaffIncrement_Others', type=str)
        self.parser.add_argument('StaffIncrement_NewSalary', type=float, required=True, help='StaffIncrement_NewSalary is required')
        self.parser.add_argument('StaffIncrement_PercentageIncrease', type=float, required=True, help='StaffIncrement_PercentageIncrease is required')
        self.parser.add_argument('StaffIncrement_InitiatedBy', type=int, required=True, help='StaffIncrement_InitiatedBy is required')
        self.parser.add_argument('StaffIncrement_Approval', type=int, required=True, help='StaffIncrement_Approval is required')
        self.parser.add_argument('StaffIncrement_Remarks', type=str, required=True, help='StaffIncrement_Remarks is required')
        self.parser.add_argument('CreatedBy', type=int, required=True, help='CreatedBy is required')
        
        args = self.parser.parse_args()
        staff_increment_date = datetime.strptime(args['StaffIncrement_Date'], '%Y-%m-%dT%H:%M:%S')

        staff_increment_info = StaffIncrement.query.filter_by(StaffIncrement_Id=args['StaffIncrement_Id'], InActive=False).first()
        
        if not staff_increment_info:
            return {"error": "Staff increment record not found"}

        staff_increment_info.InActive = 1
        db.session.commit()
        
        try:
            """
            new_staff_increment = StaffIncrement(
                StaffIncrement_StaffId=args['StaffIncrement_StaffId'],
                StaffIncrement_CurrentSalary=args['StaffIncrement_CurrentSalary'],
                StaffIncrement_Date=staff_increment_date,
                StaffIncrement_Reason=args['StaffIncrement_Reason'],
                StaffIncrement_Others=args.get('StaffIncrement_Others'),
                StaffIncrement_NewSalary=args['StaffIncrement_NewSalary'],
                StaffIncrement_PercentageIncrease=args['StaffIncrement_PercentageIncrease'],
                StaffIncrement_InitiatedBy=args['StaffIncrement_InitiatedBy'],
                StaffIncrement_Approval=args['StaffIncrement_Approval'],
                StaffIncrement_Remarks=args['StaffIncrement_Remarks'],
                CreatedBy=args['CreatedBy'],
                CreatedDate=datetime.utcnow() + timedelta(hours=5),
                InActive=0
            )
            db.session.add(new_staff_increment)
            db.session.commit()
            """
            new_staff_increment = StaffIncrement(
                StaffIncrement_StaffId=args['StaffIncrement_StaffId'],
                StaffIncrement_CurrentSalary=args['StaffIncrement_CurrentSalary'],
                StaffIncrement_Date=datetime.strptime(args['StaffIncrement_Date'], '%Y-%m-%dT%H:%M:%S'),
                StaffIncrement_Reason=args['StaffIncrement_Reason'],
                StaffIncrement_Others=args['StaffIncrement_Others'],
                StaffIncrement_NewSalary=args['StaffIncrement_NewSalary'],
                StaffIncrement_PercentageIncrease=args['StaffIncrement_PercentageIncrease'],
                StaffIncrement_InitiatedBy=args['StaffIncrement_InitiatedBy'],
                StaffIncrement_Approval=args['StaffIncrement_Approval'],
                StaffIncrement_Remarks=args['StaffIncrement_Remarks'],
                CreatedBy=args['CreatedBy'],
                CreatedDate=datetime.utcnow() + timedelta(hours=5),
                InActive=0
            )
            db.session.add(new_staff_increment)
            db.session.commit()
            
            new_salary_Id = self.update_employee_salary(new_staff_increment.StaffIncrement_StaffId, new_staff_increment.StaffIncrement_NewSalary, args['CreatedBy'])

            return {"data": [new_staff_increment.to_dict()], "new_salary_Id": new_salary_Id}, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def update_employee_salary(self, staff_id, total_salary, userId):
        """
        Updates the existing active salary record for the given staff ID.
        """
        try:
            salary = Salaries.query.filter_by(EmployeeId=staff_id, IsActive=True).first()
            
            if not salary:
                new_salary_Id = self.create_employee_salary(staff_id, total_salary, userId)
                return new_salary_Id

            print("salary found")
            basic = total_salary / 2

            salary.BasicAmount = basic
            salary.AllowancesAmount = basic
            salary.TotalAmount = total_salary
            salary.PFAmount = basic / 12
            salary.EOBIAmount = basic / 12
            salary.SESSIAmount = basic / 12
            salary.From = datetime.utcnow() + timedelta(hours=5)
            salary.To = datetime.utcnow() + timedelta(hours=5)
            salary.HouseRent = basic / 2
            salary.MedicalAllowance = basic / 10
            salary.UtilityAllowance = basic / 5
            salary.ConveyanceAllowance = basic / 5
            salary.UpdatedOn = datetime.utcnow() + timedelta(hours=5)
            salary.UpdatedByUserId = userId

            print(salary.to_dict())
            # db.session.add(salary)
            db.session.commit()
            return salary.Id
        except Exception as e:
            db.session.rollback()
            print(f"Error updating employee salary: {str(e)}")
            return {"error": "Error updating employee salary", "message": str(e)}

    def delete(self, staff_increment_id):
        try:
            staff_increment = StaffIncrement.query.get(staff_increment_id)
            if staff_increment:
                db.session.delete(staff_increment)
                db.session.commit()
                return {'message': 'StaffIncrement deleted successfully'}, 200
            else:
                return {'error': 'StaffIncrement not found'}, 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

class StaffPromotionResource(Resource):
    def get(self, promotion_id=None):
        if promotion_id:
            promotion = StaffPromotions.query.get(promotion_id)
            if promotion:
                return jsonify(promotion.to_dict())
            else:
                return {'error': 'StaffPromotions not found'}, 404
        else:
            promotions = StaffPromotions.query.all()
            return jsonify([p.to_dict() for p in promotions])

    def post(self):
        data = request.get_json()
        try:
            new_promotion = StaffPromotions(
                StaffPromotion_StaffId=data['StaffPromotion_StaffId'],
                StaffPromotion_SalaryHold=data['StaffPromotion_SalaryHold'],
                StaffPromotion_NewDesignationId=data['StaffPromotion_NewDesignationId'],
                StaffPromotion_NewDepartmentId=data['StaffPromotion_NewDepartmentId'],
                StaffPromotion_Date=datetime.strptime(data['StaffPromotion_Date'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffPromotion_Date') else None,
                StaffPromotion_Reason=data['StaffPromotion_Reason'],
                StaffPromotion_InitiatedBy=data['StaffPromotion_InitiatedBy'],
                StaffPromotion_ApprovedBy=data['StaffPromotion_ApprovedBy'],
                StaffPromotion_NewSalary=data['StaffPromotion_NewSalary'],
                StaffPromotion_NewSalaryEffectiveDate=datetime.strptime(data['StaffPromotion_NewSalaryEffectiveDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffPromotion_NewSalaryEffectiveDate') else None,
                StaffPromotion_Remarks=data['StaffPromotion_Remarks'],
                CreatedBy=data['CreatedBy'],
                CreatedDate=datetime.utcnow(),
                UpdatedBy=data.get('UpdatedBy'),
                UpdatedDate=datetime.strptime(data['UpdatedDate'], '%Y-%m-%dT%H:%M:%S') if data.get('UpdatedDate') else None,
                InActive=data['InActive']
            )
            db.session.add(new_promotion)
            db.session.commit()
            return jsonify(new_promotion.to_dict()), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def put(self, promotion_id):
        data = request.get_json()
        try:
            promotion = StaffPromotions.query.get(promotion_id)
            if promotion:
                promotion.StaffPromotion_StaffId = data.get('StaffPromotion_StaffId', promotion.StaffPromotion_StaffId)
                promotion.StaffPromotion_SalaryHold = data.get('StaffPromotion_SalaryHold', promotion.StaffPromotion_SalaryHold)
                promotion.StaffPromotion_NewDesignationId = data.get('StaffPromotion_NewDesignationId', promotion.StaffPromotion_NewDesignationId)
                promotion.StaffPromotion_NewDepartmentId = data.get('StaffPromotion_NewDepartmentId', promotion.StaffPromotion_NewDepartmentId)
                promotion.StaffPromotion_Date = datetime.strptime(data['StaffPromotion_Date'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffPromotion_Date') else promotion.StaffPromotion_Date
                promotion.StaffPromotion_Reason = data.get('StaffPromotion_Reason', promotion.StaffPromotion_Reason)
                promotion.StaffPromotion_InitiatedBy = data.get('StaffPromotion_InitiatedBy', promotion.StaffPromotion_InitiatedBy)
                promotion.StaffPromotion_ApprovedBy = data.get('StaffPromotion_ApprovedBy', promotion.StaffPromotion_ApprovedBy)
                promotion.StaffPromotion_NewSalary = data.get('StaffPromotion_NewSalary', promotion.StaffPromotion_NewSalary)
                promotion.StaffPromotion_NewSalaryEffectiveDate = datetime.strptime(data['StaffPromotion_NewSalaryEffectiveDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffPromotion_NewSalaryEffectiveDate') else promotion.StaffPromotion_NewSalaryEffectiveDate
                promotion.StaffPromotion_Remarks = data.get('StaffPromotion_Remarks', promotion.StaffPromotion_Remarks)
                promotion.CreatedBy = data.get('CreatedBy', promotion.CreatedBy)
                promotion.CreatedDate = promotion.CreatedDate
                promotion.UpdatedBy = data.get('UpdatedBy', promotion.UpdatedBy)
                promotion.UpdatedDate = datetime.utcnow()
                promotion.InActive = data.get('InActive', promotion.InActive)

                db.session.commit()
                return jsonify(promotion.to_dict()), 200
            else:
                return {'error': 'StaffPromotions not found'}, 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self, promotion_id):
        try:
            promotion = StaffPromotions.query.get(promotion_id)
            if promotion:
                db.session.delete(promotion)
                db.session.commit()
                return {'message': 'StaffPromotions deleted successfully'}, 200
            else:
                return {'error': 'StaffPromotions not found'}, 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

class StaffSeparationResource(Resource):
    def get(self, separation_id=None):
        if separation_id:
            separation = StaffSeparation.query.get(separation_id)
            if separation:
                return jsonify(separation.to_dict())
            else:
                return {'error': 'StaffSeparation not found'}, 404
        else:
            separations = StaffSeparation.query.all()
            return jsonify([s.to_dict() for s in separations])

    def post(self):
        data = request.get_json()
        try:
            new_separation = StaffSeparation(
                StaffSeparation_StaffId=data['StaffSeparation_StaffId'],
                StaffSeparation_Type=data['StaffSeparation_Type'],
                StaffSeparation_Reason=data['StaffSeparation_Reason'],
                StaffSeparation_Details=data['StaffSeparation_Details'],
                StaffSeparation_ReleventDocumentReceived=data['StaffSeparation_ReleventDocumentReceived'],
                StaffSeparation_ResignationDate=datetime.strptime(data['StaffSeparation_ResignationDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffSeparation_ResignationDate') else None,
                StaffSeparation_LastWorkingDate=datetime.strptime(data['StaffSeparation_LastWorkingDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffSeparation_LastWorkingDate') else None,
                StaffSeparation_NoticePeriod=data['StaffSeparation_NoticePeriod'],
                StaffSeparation_ResignationApproved=data['StaffSeparation_ResignationApproved'],
                StaffSeparation_SalaryHoldMonth=data['StaffSeparation_SalaryHoldMonth'],
                StaffSeparation_ClearanceDone=data['StaffSeparation_ClearanceDone'],
                StaffSeparation_ClearanceDate=datetime.strptime(data['StaffSeparation_ClearanceDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffSeparation_ClearanceDate') else None,
                StaffSeparation_ExitInterview=data['StaffSeparation_ExitInterview'],
                StaffSeparation_ExitInterviewDate=datetime.strptime(data['StaffSeparation_ExitInterviewDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffSeparation_ExitInterviewDate') else None,
                StaffSeparation_FinalSettlementDone=data['StaffSeparation_FinalSettlementDone'],
                StaffSeparation_FinalSettlementDate=datetime.strptime(data['StaffSeparation_FinalSettlementDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffSeparation_FinalSettlementDate') else None,
                CreatedBy=data['CreatedBy'],
                CreatedDate=datetime.utcnow() + timedelta(hours=5),
                InActive=0
            )
            db.session.add(new_separation)
            db.session.commit()
            return jsonify(new_separation.to_dict()), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def put(self, separation_id):
        data = request.get_json()
        try:
            separation = StaffSeparation.query.get(separation_id)
            if separation:
                separation.StaffSeparation_StaffId = data.get('StaffSeparation_StaffId', separation.StaffSeparation_StaffId)
                separation.StaffSeparation_Type = data.get('StaffSeparation_Type', separation.StaffSeparation_Type)
                separation.StaffSeparation_Reason = data.get('StaffSeparation_Reason', separation.StaffSeparation_Reason)
                separation.StaffSeparation_Details = data.get('StaffSeparation_Details', separation.StaffSeparation_Details)
                separation.StaffSeparation_ReleventDocumentReceived = data.get('StaffSeparation_ReleventDocumentReceived', separation.StaffSeparation_ReleventDocumentReceived)
                separation.StaffSeparation_ResignationDate = datetime.strptime(data['StaffSeparation_ResignationDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffSeparation_ResignationDate') else separation.StaffSeparation_ResignationDate
                separation.StaffSeparation_LastWorkingDate = datetime.strptime(data['StaffSeparation_LastWorkingDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffSeparation_LastWorkingDate') else separation.StaffSeparation_LastWorkingDate
                separation.StaffSeparation_NoticePeriod = data.get('StaffSeparation_NoticePeriod', separation.StaffSeparation_NoticePeriod)
                separation.StaffSeparation_ResignationApproved = data.get('StaffSeparation_ResignationApproved', separation.StaffSeparation_ResignationApproved)
                separation.StaffSeparation_SalaryHoldMonth = data.get('StaffSeparation_SalaryHoldMonth', separation.StaffSeparation_SalaryHoldMonth)
                separation.StaffSeparation_ClearanceDone = data.get('StaffSeparation_ClearanceDone', separation.StaffSeparation_ClearanceDone)
                separation.StaffSeparation_ClearanceDate = datetime.strptime(data['StaffSeparation_ClearanceDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffSeparation_ClearanceDate') else separation.StaffSeparation_ClearanceDate
                separation.StaffSeparation_ExitInterview = data.get('StaffSeparation_ExitInterview', separation.StaffSeparation_ExitInterview)
                separation.StaffSeparation_ExitInterviewDate = datetime.strptime(data['StaffSeparation_ExitInterviewDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffSeparation_ExitInterviewDate') else separation.StaffSeparation_ExitInterviewDate
                separation.StaffSeparation_FinalSettlementDone = data.get('StaffSeparation_FinalSettlementDone', separation.StaffSeparation_FinalSettlementDone)
                separation.StaffSeparation_FinalSettlementDate = datetime.strptime(data['StaffSeparation_FinalSettlementDate'], '%Y-%m-%dT%H:%M:%S') if data.get('StaffSeparation_FinalSettlementDate') else separation.StaffSeparation_FinalSettlementDate
                separation.CreatedBy = data.get('CreatedBy', separation.CreatedBy)
                separation.CreatedDate = separation.CreatedDate
                separation.UpdatedBy = data.get('UpdatedBy', separation.UpdatedBy)
                separation.UpdatedDate = datetime.utcnow()
                separation.InActive = data.get('InActive', separation.InActive)

                db.session.commit()
                return jsonify(separation.to_dict()), 200
            else:
                return {'error': 'StaffSeparation not found'}, 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self, separation_id):
        try:
            separation = StaffSeparation.query.get(separation_id)
            if separation:
                db.session.delete(separation)
                db.session.commit()
                return {'message': 'StaffSeparation deleted successfully'}, 200
            else:
                return {'error': 'StaffSeparation not found'}, 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

class StaffLeaveRequestTempResource(Resource):
    leave_config = {}

    @classmethod
    def load_leave_config(cls):
        # Load the leave configurations from the database
        leave_configs = db.session.query(LeaveConfiguration).all()  # Load all configs from the database
        cls.leave_config = {config.key_name: config.value for config in leave_configs}

    def __init__(self):
        if not self.leave_config:
            self.load_leave_config()

    def get_leave_type_id(self, key):
        return int(self.leave_config.get(key, 0))  # Default to 0 if not found

    def get_leave_limit(self, key):
        return int(self.leave_config.get(key, 0))  # Default to 0 if not found

    def post(self):
        try:
            if request.content_type.startswith('application/json'):
                leave_request_data = request.json
            elif request.content_type.startswith('multipart/form-data'):
                leave_request_data = request.form.to_dict()
            else:
                return {"status": "error", "message": f"Unsupported Media Type {request.content_type}"}, 415

            if not leave_request_data:
                return {"status": "error", "message": "No input data provided"}, 400

            staff_id = leave_request_data.get('StaffId')
            from_date = leave_request_data.get('FromDate')
            to_date = leave_request_data.get('ToDate')
            leave_type_id = leave_request_data.get('LeaveTypeId')
            reason = leave_request_data.get('Reason')
            leave_status_id = leave_request_data.get('LeaveStatusId')

            if not (staff_id and from_date and to_date and leave_type_id and reason and leave_status_id):
                return {"status": "error", "message": "Missing required fields"}, 400

            try:
                leave_type_id = int(leave_type_id)
                leave_status_id = int(leave_status_id)
            except ValueError:
                return {"status": "error", "message": "LeaveTypeId and LeaveStatusId must be valid integers"}, 400

            try:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
            except ValueError:
                return {"status": "error", "message": "Invalid date format. Dates must be in YYYY-MM-DD format."}, 400

            if from_date > to_date:
                return {"status": "error", "message": "The To Date must be later than the From Date."}, 400

            staff_group = self.get_staff_group(staff_id)

            if leave_type_id == self.get_leave_type_id('CASUAL_LEAVE_TYPE_ID'):
                casual_leave_limit = self.get_leave_limit('CASUAL_LEAVE_YEARLY_LIMIT')

                casual_leave_count = self.check_casual_leave(staff_id, leave_type_id, from_date, to_date)
                if casual_leave_count >= casual_leave_limit:
                    return {"status": "error", "message": "Casual leave limit exceeded for the year."}, 400

                month_data = {
                    'StartDate': from_date.replace(day=1),
                    'EndDate': (from_date.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
                }
                monthly_casual_leave_limit = self.get_leave_limit('AEN_CASUAL_LEAVE_LIMIT') if staff_group == 'AEN' else self.get_leave_limit('CAMPUS_CASUAL_LEAVE_LIMIT')
                monthly_casual_leave_count = self.check_casual_leave(staff_id, leave_type_id, from_date, to_date, month_data)

                leave_days = (to_date - from_date).days + 1

                if leave_days > monthly_casual_leave_limit or monthly_casual_leave_count >= monthly_casual_leave_limit:
                    return {"status": "error", "message": f"Casual leave limit exceeded for the month (Max {monthly_casual_leave_limit})."}, 400

            if leave_type_id == self.get_leave_type_id('SICK_LEAVE_TYPE_ID'):
                sick_leave_limit = self.get_leave_limit('SICK_LEAVE_LIMIT')

                sick_leave_count = self.check_sick_leave(staff_id, leave_type_id, from_date, to_date)
                leave_days = (to_date - from_date).days + 1

                if leave_days > sick_leave_limit:
                    return {"status": "error", "message": "Sick leave limit exceeded for the year."}, 400

                if sick_leave_count > sick_leave_limit:
                    return {"status": "error", "message": "Sick leave limit exceeded for the year."}, 400

            academic_year = AcademicYear.query.filter_by(IsActive=True, status=True).first()
            academic_year_id = academic_year.academic_year_Id if academic_year else None
            if leave_type_id == self.get_leave_type_id('ANNUAL_LEAVE_TYPE_ID'):
                total_annual_leave_taken = self.get_annual_leave_taken(staff_id, academic_year_id)
                annual_leave_limit = self.get_leave_limit('ANNUAL_LEAVE_LIMIT')

                if total_annual_leave_taken + (to_date - from_date).days + 1 > annual_leave_limit:
                    return {"status": "error", "message": "Annual leave limit exceeded."}, 400

            if leave_type_id == self.get_leave_type_id('MATERNITY_LEAVE_TYPE_ID'):
                employment_duration = self.get_employment_duration(staff_id)
                if employment_duration < timedelta(days=365):
                    return {"status": "error", "message": "Not eligible for maternity leave."}, 400

            if leave_type_id == self.get_leave_type_id('PATERNITY_LEAVE_TYPE_ID'):
                paternity_leave_taken = self.get_paternity_leave_taken(staff_id)
                if paternity_leave_taken > 3:
                    return {"status": "error", "message": "Paternity leave limit exceeded."}, 400
                if (to_date - from_date).days + 1 > 3:
                    return {"status": "error", "message": "Paternity leave cannot exceed 3 days."}, 400

            if leave_type_id == self.get_leave_type_id('COMPENSATORY_LEAVE_TYPE_ID'):
                if not self.verify_compensatory_leave_eligibility(staff_id, CampusIds=leave_request_data.get('CampusId') ,from_date=from_date, to_date=to_date):
                    return {"status": "error", "message": "Not eligible for compensatory leave."}, 400

            check_attendance = db.session.query(StaffAttendanceTemp.CreateDate).filter(
                StaffAttendanceTemp.staff_Id == staff_id,
                StaffAttendanceTemp.time_In.isnot(None),
                StaffAttendanceTemp.CreateDate >= from_date,
                StaffAttendanceTemp.CreateDate <= to_date
            ).first()

            if check_attendance:
                return {"status": "error", "message": (
                    f"Your leave request from {from_date.strftime('%d-%b-%Y')} to {to_date.strftime('%d-%b-%Y')} has not been approved. "
                    f"You were marked as Present on {check_attendance.CreateDate.strftime('%d-%b-%Y')}."
                )}, 409

            check_duplicate_leave = StaffLeaveRequest.query.filter(
                StaffLeaveRequest.status == 1,
                StaffLeaveRequest.StaffId == staff_id,
                StaffLeaveRequest.LeaveStatusId != 2,
                ((StaffLeaveRequest.FromDate >= from_date) & (StaffLeaveRequest.FromDate <= to_date)) |
                ((StaffLeaveRequest.ToDate >= from_date) & (StaffLeaveRequest.ToDate <= to_date))
            ).first()

            if check_duplicate_leave:
                return {"status": "error", "message": (
                    f"Your leave request from {from_date.strftime('%d-%b-%Y')} to {to_date.strftime('%d-%b-%Y')} has not been approved. "
                    f"You already have an existing leave scheduled."
                )}, 409

            leave_days = (to_date - from_date).days + 1
            leave_request_data['AcademicYearId'] = academic_year_id
            leave_request_data['status'] = True

            leave_request = StaffLeaveRequest(
                StaffId=staff_id,
                FromDate=from_date,
                ToDate=to_date,
                Reason=reason,
                Remarks=leave_request_data.get('Remarks'),
                LeaveStatusId=leave_status_id,
                ApprovedBy=leave_request_data.get('ApprovedBy'),
                LeaveApplicationPath=leave_request_data.get('LeaveApplicationPath'),
                AcademicYearId=academic_year_id,
                status=True,
                UpdaterId=leave_request_data.get('UpdaterId') if leave_request_data.get('UpdaterId') else None,
                UpdateDate=datetime.utcnow(),
                CreatorId=leave_request_data.get('CreatorId'),
                CreateDate=datetime.utcnow(),
                CampusId=leave_request_data.get('CampusId'),
                LeaveTypeId=leave_type_id
            )

            db.session.add(leave_request)
            db.session.commit()

            self.staff_leave_date_range_entry(from_date, to_date)

            return {"status": "success", "message": "Leave request created successfully."}, 201

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            db.session.rollback()
            return {"status": "error", "message": "A database error occurred, please try again later."}, 500

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            db.session.rollback()
            return {"status": "error", "message": "An unexpected error occurred, please try again later."}, 500

    def check_casual_leave(self, staff_id, leave_type_id, from_date, to_date, month_data=None):
        casual_leave_count = 0
        if month_data:
            casual_leave_count = StaffLeaveRequest.query.filter(
                StaffLeaveRequest.status == 1,
                StaffLeaveRequest.StaffId == staff_id,
                StaffLeaveRequest.LeaveTypeId == leave_type_id,
                StaffLeaveRequest.LeaveStatusId != 2,
                (
                    (StaffLeaveRequest.FromDate >= month_data['StartDate']) &
                    (StaffLeaveRequest.FromDate <= month_data['EndDate'])
                ) |
                (
                    (StaffLeaveRequest.ToDate >= month_data['StartDate']) &
                    (StaffLeaveRequest.ToDate <= month_data['EndDate'])
                )
            ).count()
        else:
            casual_leave_count = StaffLeaveRequest.query.filter(
                StaffLeaveRequest.status == 1,
                StaffLeaveRequest.StaffId == staff_id,
                StaffLeaveRequest.LeaveTypeId == leave_type_id,
                StaffLeaveRequest.LeaveStatusId != 2,
                (
                    (extract('month', StaffLeaveRequest.FromDate) == from_date.month) &
                    (extract('year', StaffLeaveRequest.FromDate) == from_date.year)
                ) |
                (
                    (extract('month', StaffLeaveRequest.ToDate) == to_date.month) &
                    (extract('year', StaffLeaveRequest.ToDate) == to_date.year)
                )
            ).count()

        return casual_leave_count

    def check_sick_leave(self, staff_id, leave_type_id, from_date, to_date):
        sick_leave_count = StaffLeaveRequest.query.filter(
            StaffLeaveRequest.status == 1,
            StaffLeaveRequest.StaffId == staff_id,
            StaffLeaveRequest.LeaveTypeId == leave_type_id,
            StaffLeaveRequest.LeaveStatusId != 2,
            (
                (extract('year', StaffLeaveRequest.FromDate) == from_date.year) |
                (extract('year', StaffLeaveRequest.ToDate) == to_date.year)
            )
        ).count()

        return sick_leave_count

    def get_annual_leave_taken(self, staff_id, academic_year_id):
        annual_leave_count = StaffLeaveRequest.query.filter(
            StaffLeaveRequest.status == 1,
            StaffLeaveRequest.StaffId == staff_id,
            StaffLeaveRequest.LeaveTypeId == self.get_leave_type_id('ANNUAL_LEAVE_TYPE_ID'),
            StaffLeaveRequest.AcademicYearId == academic_year_id
        ).count()

        return annual_leave_count

    def get_employment_duration(self, staff_id):
        employment_start_date = db.session.query(StaffInfo.S_JoiningDate).filter_by(Staff_ID=staff_id).first()
        if employment_start_date:
            return datetime.utcnow() - employment_start_date[0]
        return timedelta(days=0)

    def verify_compensatory_leave_eligibility(self, staff_id, CampusIds, from_date, to_date):
        # Query to filter records between the given date range
        worked_on_off_days = db.session.query(MarkDayOffDeps).filter(
            MarkDayOffDeps.Staff_Id == staff_id,
            MarkDayOffDeps.Date.between(from_date, to_date)).count()
        
        if not worked_on_off_days:
            worked_on_off_days = db.session.query(MarkDayOffHRs).filter(
                MarkDayOffHRs.CampusIds == CampusIds,
                MarkDayOffHRs.Date.between(from_date, to_date)).count()

        return worked_on_off_days > 0

    def get_staff_group(self, staff_id):
        staff_group = db.session.query(StaffInfo.IsAEN).filter_by(Staff_ID=staff_id).first()
        staff_group = staff_group[0] if staff_group else None
        try:
            staff_group = "AEN" if staff_group == 1 else 'Campus'
            return staff_group
        except:
            return None

    def get_paternity_leave_taken(self, staff_id):
        paternity_leave_count = StaffLeaveRequest.query.filter(
            StaffLeaveRequest.status == 1,
            StaffLeaveRequest.StaffId == staff_id,
            StaffLeaveRequest.LeaveTypeId == self.get_leave_type_id('PATERNITY_LEAVE_TYPE_ID')
        ).count()

        return paternity_leave_count

    def staff_leave_date_range_entry(self, from_date, to_date):
        try:
            from_date_str = from_date.strftime('%Y-%m-%d')
            to_date_str = to_date.strftime('%Y-%m-%d')
            sql = text("EXEC sp_StaffLeaveDateRangeEntry :from_date, :to_date")
            db.session.execute(sql, {'from_date': from_date_str, 'to_date': to_date_str})
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

class SalaryTransferDetailsResource(Resource):
    def get(self, transfer_id=None):
        if transfer_id:
            transfer = SalaryTransferDetails.query.get(transfer_id)
            if transfer:
                return jsonify(transfer.to_dict())
            else:
                return {'error': 'SalaryTransferDetails not found'}, 404
        else:
            transfers = SalaryTransferDetails.query.all()
            return jsonify([t.to_dict() for t in transfers])

    def post(self):
        data = request.get_json()
        try:
            new_transfer = SalaryTransferDetails(
                SalaryTransferDetails_StaffId=data['SalaryTransferDetails_StaffId'],
                SalaryTransferDetails_TransferMethod=data['SalaryTransferDetails_TransferMethod'],
                SalaryTransferDetails_BankName=data.get('SalaryTransferDetails_BankName'),
                SalaryTransferDetails_BankAccountNumber=data.get('SalaryTransferDetails_BankAccountNumber'),
                SalaryTransferDetails_BankBranch=data.get('SalaryTransferDetails_BankBranch'),
                SalaryTransferDetails_BankOrChequeTitle=data['SalaryTransferDetails_BankOrChequeTitle'],
                SalaryTransferDetails_ReasonForChequeIssuance=data.get('SalaryTransferDetails_ReasonForChequeIssuance'),
                SalaryTransferDetails_EffectiveDate=datetime.strptime(data['SalaryTransferDetails_EffectiveDate'], '%Y-%m-%dT%H:%M:%S') if data.get('SalaryTransferDetails_EffectiveDate') else None,
                SalaryTransferDetails_Remarks=data['SalaryTransferDetails_Remarks'],
                CreatedBy=data['CreatedBy'],
                CreatedDate=datetime.utcnow(),
                UpdatedBy=data.get('UpdatedBy'),
                UpdatedDate=datetime.strptime(data['UpdatedDate'], '%Y-%m-%dT%H:%M:%S') if data.get('UpdatedDate') else None,
                InActive=0
            )
            db.session.add(new_transfer)
            db.session.commit()
            return jsonify(new_transfer.to_dict()), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def put(self, transfer_id):
        data = request.get_json()
        try:
            transfer = SalaryTransferDetails.query.get(transfer_id)
            if transfer:
                transfer.SalaryTransferDetails_StaffId = data.get('SalaryTransferDetails_StaffId', transfer.SalaryTransferDetails_StaffId)
                transfer.SalaryTransferDetails_TransferMethod = data.get('SalaryTransferDetails_TransferMethod', transfer.SalaryTransferDetails_TransferMethod)
                transfer.SalaryTransferDetails_BankName = data.get('SalaryTransferDetails_BankName', transfer.SalaryTransferDetails_BankName)
                transfer.SalaryTransferDetails_BankAccountNumber = data.get('SalaryTransferDetails_BankAccountNumber', transfer.SalaryTransferDetails_BankAccountNumber)
                transfer.SalaryTransferDetails_BankBranch = data.get('SalaryTransferDetails_BankBranch', transfer.SalaryTransferDetails_BankBranch)
                transfer.SalaryTransferDetails_BankOrChequeTitle = data.get('SalaryTransferDetails_BankOrChequeTitle', transfer.SalaryTransferDetails_BankOrChequeTitle)
                transfer.SalaryTransferDetails_ReasonForChequeIssuance = data.get('SalaryTransferDetails_ReasonForChequeIssuance', transfer.SalaryTransferDetails_ReasonForChequeIssuance)
                transfer.SalaryTransferDetails_EffectiveDate = datetime.strptime(data['SalaryTransferDetails_EffectiveDate'], '%Y-%m-%dT%H:%M:%S') if data.get('SalaryTransferDetails_EffectiveDate') else transfer.SalaryTransferDetails_EffectiveDate
                transfer.SalaryTransferDetails_Remarks = data.get('SalaryTransferDetails_Remarks', transfer.SalaryTransferDetails_Remarks)
                transfer.CreatedBy = data.get('CreatedBy', transfer.CreatedBy)
                transfer.CreatedDate = transfer.CreatedDate
                transfer.UpdatedBy = data.get('UpdatedBy', transfer.UpdatedBy)
                transfer.UpdatedDate = datetime.utcnow() + timedelta(hours=5)
                transfer.InActive = data.get('InActive', transfer.InActive)

                db.session.commit()
                return jsonify(transfer.to_dict()), 200
            else:
                return {'error': 'SalaryTransferDetails not found'}, 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self, transfer_id):
        try:
            transfer = SalaryTransferDetails.query.get(transfer_id)
            if transfer:
                db.session.delete(transfer)
                db.session.commit()
                return {'message': 'SalaryTransferDetails deleted successfully'}, 200
            else:
                return {'error': 'SalaryTransferDetails not found'}, 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

class PayrollCloseResource(Resource):
    def get(self, payroll_close_id=None):
        if payroll_close_id:
            payroll_close = PayrollClose.query.get(payroll_close_id)
            if payroll_close:
                return jsonify(payroll_close.to_dict())
            else:
                return {'error': 'PayrollClose not found'}, 404
        else:
            payroll_closes = PayrollClose.query.all()
            return jsonify([pc.to_dict() for pc in payroll_closes])

    def post(self):
        data = request.get_json()
        try:
            new_payroll_close = PayrollClose(
                PayrollClose_StaffId=data['PayrollClose_StaffId'],
                PayrollClose_Period=data['PayrollClose_Period'],
                PayrollClose_CloseDate=datetime.strptime(data['PayrollClose_CloseDate'], '%Y-%m-%dT%H:%M:%S') if data.get('PayrollClose_CloseDate') else None,
                PayrollClose_ProcessedBy=data['PayrollClose_ProcessedBy'],
                PayrollClose_ReceivedBy=data['PayrollClose_ReceivedBy'],
                PayrollClose_ApprovedBy=data['PayrollClose_ApprovedBy'],
                PayrollClose_Remarks=data['PayrollClose_Remarks'],
                CreatedBy=data['CreatedBy'],
                CreatedDate=datetime.utcnow() + timedelta(hours=5),
                # UpdatedBy=data.get('UpdatedBy'),
                # UpdatedDate=datetime.strptime(data['UpdatedDate'], '%Y-%m-%dT%H:%M:%S') if data.get('UpdatedDate') else None,
                InActive=0
            )
            db.session.add(new_payroll_close)
            db.session.commit()
            return jsonify(new_payroll_close.to_dict()), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def put(self, payroll_close_id):
        data = request.get_json()
        try:
            payroll_close = PayrollClose.query.get(payroll_close_id)
            if payroll_close:
                
                try:                    
                    new_payroll_close = PayrollCloseHistory(
                        PayrollCloseHistory_PayrollClose_Id = payroll_close_id,
                        PayrollCloseHistory_Period= payroll_close.PayrollClose_Period,
                        PayrollCloseHistory_CloseDate= payroll_close.PayrollClose_CloseDate,
                        PayrollCloseHistory_ProcessedBy= payroll_close.PayrollClose_ProcessedBy,
                        PayrollCloseHistory_ReviewedBy= payroll_close.PayrollClose_ReceivedBy,
                        PayrollCloseHistory_ApprovedBy= payroll_close.PayrollClose_ApprovedBy,
                        PayrollCloseHistory_Remarks= payroll_close.PayrollClose_Remarks,
                        CreatedBy= payroll_close.CreatedBy,
                        CreatedDate= payroll_close.CreatedDate,
                        UpdatedBy= data.get('UpdatedBy'),
                        UpdatedDate= datetime.utcnow() + timedelta(hours=5),
                        InActive=0
                    )
                    db.session.add(new_payroll_close)
                    db.session.commit()
                except SQLAlchemyError as e:
                    db.session.rollback()
                    return {'error': str(e)}, 500
                
                payroll_close.PayrollClose_StaffId = data.get('PayrollClose_StaffId', payroll_close.PayrollClose_StaffId)
                payroll_close.PayrollClose_Period = data.get('PayrollClose_Period', payroll_close.PayrollClose_Period)
                payroll_close.PayrollClose_CloseDate = datetime.strptime(data['PayrollClose_CloseDate'], '%Y-%m-%dT%H:%M:%S') if data.get('PayrollClose_CloseDate') else payroll_close.PayrollClose_CloseDate
                payroll_close.PayrollClose_ProcessedBy = data.get('PayrollClose_ProcessedBy', payroll_close.PayrollClose_ProcessedBy)
                payroll_close.PayrollClose_ReceivedBy = data.get('PayrollClose_ReceivedBy', payroll_close.PayrollClose_ReceivedBy)
                payroll_close.PayrollClose_ApprovedBy = data.get('PayrollClose_ApprovedBy', payroll_close.PayrollClose_ApprovedBy)
                payroll_close.PayrollClose_Remarks = data.get('PayrollClose_Remarks', payroll_close.PayrollClose_Remarks)
                payroll_close.CreatedBy = data.get('CreatedBy', payroll_close.CreatedBy)
                payroll_close.CreatedDate = payroll_close.CreatedDate
                payroll_close.UpdatedBy = data.get('UpdatedBy', payroll_close.UpdatedBy)
                payroll_close.UpdatedDate = datetime.utcnow()
                payroll_close.InActive = data.get('InActive', payroll_close.InActive)

                db.session.commit()
                return jsonify(payroll_close.to_dict()), 200
            else:
                return {'error': 'PayrollClose not found'}, 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self, payroll_close_id):
        try:
            payroll_close = PayrollClose.query.get(payroll_close_id)
            if payroll_close:
                db.session.delete(payroll_close)
                db.session.commit()
                return {'message': 'PayrollClose deleted successfully'}, 200
            else:
                return {'error': 'PayrollClose not found'}, 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500

import re

class EmailSendingResource(Resource):

    def generate_dynamic_email(self, template, **kwargs):
        """
        Generates an email by replacing placeholders in the template with actual values.

        :param template: The email template with placeholders.
        :param kwargs: The key-value pairs to replace in the template.
        :return: The formatted email string.
        """
        return template.format(**kwargs)

    def strip_html_tags(self, text):
        """
        Strips HTML tags from the given text.

        :param text: The text potentially containing HTML.
        :return: The text without HTML tags.
        """
        clean_text = re.sub(r'<.*?>', '', text)  # Remove anything between < and >
        return clean_text

    def get_email_template(self, id):
        email = EmailStorageSystem.query.get(id)
        if email is None:
            abort(404, message=f"EmailStorageSystem {id} doesn't exist")
        
        return email.Email_Body, email.Email_Subject

    def post(self):
        # Get data from the request
        data = request.get_json()
        template_id = data.get('template_id')
        parameters = data.get('parameters', {})
        recipients = data.get('recipients', [])
        cc = data.get('cc', [])
        employee_cnic = data.get('Employee_Cnic')
        creator_id = data.get('CreatorId') 
        create_date = data.get('CreateDate')
        attachment = data.get('attachment')

        if not template_id or not parameters or not recipients:
            return {"error": "template_id, parameters, and recipients are required"}, 400

        # Fetch template and subject
        template, subject = self.get_email_template(template_id)
        if not template:
            return {"error": "Template not found"}, 404

        try:
            # Generate dynamic email content
            email_content = self.generate_dynamic_email(template, **parameters)
            email_subject = self.generate_dynamic_email(subject, **parameters)
            email_subject = self.strip_html_tags(email_subject)
        except KeyError as e:
            return {"error": f"Missing parameter: {e}"}, 400
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}, 500

        try:
            # Create the email message
            msg = Message(subject=email_subject,
                          sender=os.environ.get('MAIL_USERNAME'),
                          recipients=recipients,
                          cc=cc)
            msg.html = email_content  # Set the email body

            # Handle attachment (if provided)
            if attachment:
                file = attachment
                file_data = file.get('data')  # This will be the base64-encoded file data
                filename = file.get('name')
                file_type = file.get('type')

                # Decode the base64-encoded file data
                file_binary = base64.b64decode(file_data)

                # Attach file to email
                msg.attach(filename, file_type, file_binary)

            # Send the email
            mail.send(msg)

            # Log the sent email
            self.log_email(template_id, email_subject, email_content, employee_cnic, creator_id, create_date)

            return {"message": f"Email sent successfully to {recipients}"}, 200
        except Exception as e:
            return {"error": f"Failed to send email: {e}"}, 500

    def handle_attachment(self, file):
        """Helper function to encode file to base64 (if needed)"""
        filename = secure_filename(file.filename)
        file_type = file.mimetype
        file_data = file.read()

        # Base64 encode the file data
        file_base64 = base64.b64encode(file_data).decode('utf-8')

        return filename, file_type, file_base64

    def log_email(self, email_id, subject, content, employee_cnic, creator_id, create_date):
        # Create a new EmailLog_HR entry with template_id as EmailId
        email_log = EmailLog_HR(
            EmailId=email_id,  # Use the template_id here
            Email_Title=subject,  # Log the subject as the title
            Email_Subject=subject,
            Email_Body=content,
            Employee_Cnic=employee_cnic,
            CreatorId=creator_id,
            CreateDate=create_date  # Set the creation date to now
        )
        db.session.add(email_log)
        db.session.commit()



class UserDetails(Resource):
    
    def post(self, id):
        try:
            try:
                user = USERS.query.get_or_404(id)
            except SQLAlchemyError as e:
                logger.error(f"Database query error: {e}")
                return {"data": {'status': 400, 'message': 'Database error'}}, 500

            if not user:
                logger.warning("Invalid username or password")
                return {"data": {'status': 400, 'message': 'Invalid username or password'}}, 401

            if not user.Status:
                logger.warning("User account is inactive")
                return {"data": {'status': 400, 'message': 'Account is inactive'}}, 403
            
            # staff_info_alias = db.aliased(StaffInfo)

            staffInfo = db.session.query(StaffInfo).join(UserCampus, UserCampus.StaffId == StaffInfo.Staff_ID).filter(UserCampus.UserId == 10139).first()
            countryName = country.query.filter_by(country_id=staffInfo.CountryId).first().country
            cityName = cities.query.filter_by(cityId=staffInfo.CityId).first().city
            campus = db.session.query(Campus).join(USERS, USERS.CampusId == Campus.Id).filter(USERS.User_Id == user.User_Id).first()


            try:
                user_roles = Roles.query.join(LNK_USER_ROLE, Roles.Role_id == LNK_USER_ROLE.Role_Id)\
                    .filter(LNK_USER_ROLE.User_Id == user.User_Id).all()

                user_rights = db.session.query(FormDetails.Action, Form.Controller)\
                    .join(FormDetailPermissions, FormDetails.Id == FormDetailPermissions.FormDetailId)\
                    .join(Form, FormDetails.FormId == Form.FormId)\
                    .join(Roles, FormDetailPermissions.RoleId == Roles.Role_id)\
                    .join(LNK_USER_ROLE, Roles.Role_id == LNK_USER_ROLE.Role_Id)\
                    .filter(LNK_USER_ROLE.User_Id == user.User_Id, FormDetailPermissions.Status == True)\
                    .all()

                user_type = UserType.query.filter_by(UserTypeId=user.UserType_Id).first()
            except SQLAlchemyError as e:
                logger.error(f"Database query error: {e}")
                return {"data": {'status': 400, 'message': 'Database error'}}, 500

            firstName = user.Firstname if user.Firstname else ''
            lastName = user.Lastname if user.Lastname else ''
            
            user_details = {
                'user': {
                    'id': user.User_Id,
                    'displayName': firstName + " " + lastName,
                    'email': user.EMail,
                    'campusId': user.CampusId,
                    'Campus': campus.Name if campus else None,
                    'userType': user_type.UserTypeName if user_type else 'Unknown',
                    'roles': [role.RoleName for role in user_roles],
                    'city': cityName,
                    'country': countryName,
                    'isPublic': True,
                    'address': staffInfo.PresentAddress if staffInfo else None,
                    'phoneNumber': staffInfo.S_ContactNo,
                    "photoURL": staffInfo.PhotoPath if staffInfo else None,
                    'rights': [{'Controller': right.Controller, 'Action': right.Action} for right in user_rights],
                    "schoolDetails": [],
                    "currentAcademicYear": [],
                    "studentCount": 0
                }
            }

            try:
                school_info = SchoolDetails.query.filter_by(status=True).first()
                if school_info:
                    user_details["user"]["schoolDetails"].append({
                        "schoolName": school_info.SchoolName,
                        "mobileNo": school_info.MobileNo,
                        "miniLogo": school_info.MiniLogo,
                        "reportLogo": school_info.ReportLogo,
                        "address": school_info.Address
                    })

                academic_year = AcademicYear.query.filter_by(IsActive=True, status=True).first()
                if academic_year:
                    user_details["user"]["currentAcademicYear"] = academic_year.to_dict()

                if user_type and user_type.UserTypeId == 7:
                    user_details["user"]["studentCount"] = StudentInfo.query.filter_by(UserId=user.User_Id, Stud_Active=True).count()
            except SQLAlchemyError as e:
                logger.error(f"Database query error: {e}")
                return {"data": {'status': 400, 'message': f'Database error: {e}'}}, 500

            return {"data": user_details, "status": 200}, 200
        except SQLAlchemyError as e:
            return {"data": {'status': 400, 'message': f"Database error occurred: {str(e)}"}}, 500
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return {"data": {'status': 400, 'message': f'Internal server error: {e}'}}, 500

class StaffDetailsResource(Resource):
    def get(self, id=None):
        
        try:
            staff_detail = db.session.query(StaffInfo).filter(StaffInfo.IsActive == True, StaffInfo.Staff_ID == id).all()
            if staff_detail:
                obj = {
                    'studentName': staff_detail[0].S_Name,
                    'FatherName': staff_detail[0].S_FName if staff_detail[0].S_FName else "None"
                }
            else:
                obj = {}
            return jsonify(obj)
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class EmployeeCreationResource(Resource):

    def post(self):
        try:
            logging.info("Received request to create employee record.")

            # Ensure that both form data and files are present in the request
            if not request.files and not request.form:
                logging.warning("No file or form data found in the request.")
                return {'message': 'No file or form data in the request'}, 400

            # Process form data
            form_data = request.form.to_dict(flat=False)  # Use flat=False for multi-valued keys
            # logging.info(f"Form data received: {form_data}")

            inserted_ids = {}  # To store IDs of inserted records for foreign key relationships
            file_data = {}

            # Step 1: Loop through form data and insert records into the appropriate tables
            for table_name, fields in form_data.items():

                # Step 2: Handle JSON string data (the fields contain lists of JSON strings)
                if isinstance(fields, list) and len(fields) == 1:
                    try:
                        # Parse the JSON string into a Python dictionary or list
                        fields = json.loads(fields[0])
                        
                        if table_name in ['StaffEducation', 'StaffExperience', 'StaffOther']:
                            for items in fields:
                                try:
                                    items.pop("Filename")
                                except:
                                    pass
                        
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON decoding error for table {table_name}: {str(e)}")
                        return {'status': 'error', 'message': f'Invalid JSON data for {table_name}'}, 400

                # Step 3: Handle both single dictionary entries and list of dictionaries
                if isinstance(fields, dict):
                    fields = [fields]  # Convert single dictionary to list for uniformity

                # Step 4: Insert each record in the list into the respective table
                model_class = self.get_model_by_tablename(table_name)
                if not model_class:
                    logging.error(f"Table {table_name} does not exist.")
                    return {'status': 'error', 'message': f'Table {table_name} does not exist'}, 400

                for record_fields in fields:
                    # Step 5: Handle foreign key relationships based on previously inserted IDs
                    self.apply_foreign_keys(table_name, record_fields, inserted_ids)

                    if table_name == "StaffInfo":
                        # Check if the S_CNIC exists in the StaffInfo table
                        existing_record = db.session.query(model_class).filter_by(S_CNIC=record_fields.get('S_CNIC')).first()

                        if existing_record:
                            # Determine active or inactive status based on the 'inactive' property
                            status = "Active" if existing_record.IsActive == 1 else "Inactive"
                            campus = existing_record.CampusId
                            campus_record = db.session.query(Campus).filter_by(Id=campus).first()  # Assuming 'id' is the column name in Campus table
                            if campus_record:
                                campus_name = campus_record.Name  # Assuming 'name' is the column storing the campus name
                            else:
                                campus_name = "Unknown"

                            EmployeeCode = existing_record.Staff_ID

                            # Construct the professional message
                            message = (f"A record with CNIC {record_fields.get('S_CNIC')} already exists at the {campus_name} campus with the EmployeeCode {EmployeeCode}. The record is currently {status}.")
                            
                            # Log the message
                            logging.info(message)
                            
                            # Return a structured response
                            return {'status': 'failed', 'message': message}, 200
                        else:
                            # Proceed with barcode generation and insertion if the record doesn't exist
                            max_barcode_id = db.session.query(db.func.max(model_class.BarcodeId)).scalar()
                            logging.info(f"max_barcode_id: {max_barcode_id} for new StaffInfo record")
                            
                            if max_barcode_id is None:
                                new_barcode_id = 1  # If the table is empty, start from 1
                            else:
                                new_barcode_id = int(max_barcode_id) + 1  # Otherwise, increment by 1

                            # Add BarcodeId to the record_fields before inserting
                            record_fields['BarcodeId'] = str(new_barcode_id)  # Ensure BarcodeId is a string
                            logging.info(f"Assigned BarcodeId: {record_fields['BarcodeId']} for new StaffInfo record")


                    # Step 6: Try inserting the record into the table
                    try:
                        record = model_class(**record_fields)
                        db.session.add(record)
                        db.session.commit()

                        # Step 7: Capture the inserted record's ID for future foreign key relationships
                        if table_name == "StaffInfo":                            
                            inserted_ids[table_name] = record.Staff_ID   

                            # Updating EmpId in StaffInfo
                            record = db.session.query(model_class).filter_by(Staff_ID=record.Staff_ID).first()
                            setattr(record, "EmpId", record.Staff_ID)
                            db.session.commit()
                            
                            logging.info(f"Inserted StaffInfo with ID: {record.Staff_ID}")
                        elif table_name == "USERS":
                            inserted_ids[table_name] = record.User_Id
                            logging.info(f"Inserted USERS with ID: {record.User_Id}")
                        elif table_name == "Shifts":
                            inserted_ids[table_name] = record.Id
                            logging.info(f"Inserted Shifts with ID: {record.Id}")
                        else:
                            try:
                                inserted_ids[str(table_name)+f"_{record.Id}"] = record.Id
                                logging.info(f"Inserted {table_name} with ID: {record.Id}")
                            except:
                                pass

                    except SQLAlchemyError as e:
                        db.session.rollback()
                        logging.error(f"Database error: {str(e)}")
                        return {'status': 'error', 'message': str(e)}, 500
                    except Exception as e:
                        db.session.rollback()
                        logging.error(f"Error inserting into {table_name}: {str(e)}")
                        return {'status': 'error', 'message': str(e)}, 500

            if request.files:
                # Process files after records are inserted
                file_data = self.process_files(request.files)
            
            # Step 8: Process file uploads and associate them with the inserted records
            for file_key, file_info in file_data.items():
                _ , table_name, field_name, _ = file_info['key'].split('_')
                file_path = file_info['path']
                # Optimized code to simulate LIKE behavior and return both key and value
                result = next(((key, value) for key, value in inserted_ids.items() if table_name in key), None)

                if result is not None:
                # if record_id:
                    try:
                        key, record_id = result
                        # Update the record with the file path
                        self.update_file_path(table_name, record_id, field_name, file_path)
                        if not table_name == 'StaffCnic':
                            inserted_ids.pop(key)

                    except Exception as e:
                        db.session.rollback()
                        logging.error(f"File association error for {table_name}: {str(e)}")
                        return {'status': 'error', 'message': f'File association error: {str(e)}'}, 500

            logging.info("Employee record created successfully.")
            return {'status': 'success', 'message': 'Records inserted successfully', 'inserted_ids': inserted_ids}, 201

        except Exception as e:
            logging.error(f"Unexpected error in processing request: {str(e)}")
            return {'status': 'error', 'message': str(e)}, 500

    def get_model_by_tablename(self, table_name):
        """
        Dynamically fetches the SQLAlchemy model class based on the table name.
        """
        return globals().get(table_name)

    def apply_foreign_keys(self, table_name, record_fields, inserted_ids):
        """
        Applies the foreign key relationships based on inserted_ids.
        """
        if table_name in ["StaffCnic", "StaffChild", "StaffEducation", "StaffExperience", "StaffOther"]:
            record_fields["StaffId"] = inserted_ids.get('StaffInfo')
        elif table_name == "Salaries":
            record_fields["EmployeeId"] = inserted_ids.get('StaffInfo')
        elif table_name == "UserCampus":
            record_fields["UserId"] = inserted_ids.get('USERS')
            record_fields["StaffId"] = inserted_ids.get('StaffInfo')
        elif table_name == "ShiftMonthlySchedules":
            record_fields["ShiftId"] = inserted_ids.get('Shifts')
        elif table_name == "ShiftSchedules":
            record_fields["ShiftId"] = inserted_ids.get('Shifts')
        elif table_name == "StaffShifts":
            record_fields["StaffId"] = inserted_ids.get('StaffInfo')
            record_fields["ShiftId"] = inserted_ids.get('Shifts')
        elif table_name == "USERS":
            record_fields["Teacher_Id"] = str(inserted_ids.get('StaffInfo'))
            record_fields["Username"] = encrypt(str(inserted_ids.get('StaffInfo')) + "." + str(record_fields["Firstname"]).lower() + "@alpha.edu.pk")
            record_fields["Password"] = encrypt(str(inserted_ids.get('StaffInfo')))
    
    def process_files(self, files):
        # Handles the file uploads and saves them to the appropriate locations.
        
        file_data = {}
        BASE_UPLOAD_FOLDER = 'uploads\\'
        
        for key, file in files.items():
            
            logging.info(f"fileName: {key}")
            
            if file.filename == '':
                continue

            filename = secure_filename(file.filename)
            key_parts = key.split('_')

            table_name = key_parts[1]
            field_name = key_parts[2]
            filename = key_parts[3]
            
            # MAIN_UPLOAD_FOLDER = MAIN_UPLOAD_FOLDER + table_name
            MAIN_UPLOAD_FOLDER = os.path.join(BASE_UPLOAD_FOLDER, table_name)
            UPLOAD_FOLDER = os.path.join(MAIN_UPLOAD_FOLDER, field_name)

            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            file_data[key] = {'key': key, 'path': file_path}

        return file_data
    
    def update_file_path(self, table_name, record_id, field_name, file_path):
        """
        Updates the record in the database with the file path.
        """
        model_class = self.get_model_by_tablename(table_name)
        if model_class:
            record_field = 'Staff_ID' if table_name == 'StaffInfo' else 'Id'
            record = db.session.query(model_class).filter_by(**{record_field: record_id}).first()
            print ("Record",record)
            if record:
                setattr(record, field_name, file_path)
                db.session.commit()
    
    def put(self):
        try:
            logging.info("Received request to update employee record.")

            # Validate form data or files
            if not request.files and not request.form:
                return {'message': 'No file or form data in the request'}, 400

            # Process form data
            form_data = request.form.to_dict(flat=False)
            updated_ids = {}
            allowed_tables = ['StaffChild', 'StaffEducation', 'StaffExperience', 'StaffOther', 'StaffInfo', 'StaffCnic']

            # Process form data for each table
            for table_name, fields in form_data.items():
                model_class = self.get_model_by_tablename(table_name)
                if not model_class:
                    logging.error(f"Table {table_name} does not exist.")
                    return {'status': 'error', 'message': f'Table {table_name} does not exist'}, 400

                fields = self._parse_fields(fields)

                if table_name in allowed_tables:
                    for record_fields in fields:
                        record_id = record_fields.get('Staff_ID') if table_name == 'StaffInfo' else record_fields.get('Id')
                        if record_id:
                            existing_record = self._fetch_existing_record(model_class, table_name, record_id)
                            if existing_record:
                                # Handle EducationDocumentPath
                                if 'EducationDocumentPath' in record_fields:
                                    setattr(existing_record, 'EducationDocumentPath', record_fields['EducationDocumentPath'])
                                
                                # Handle ExperienceDocumentPath
                                if 'ExperienceDocumentPath' in record_fields:
                                    setattr(existing_record, 'ExperienceDocumentPath', record_fields['ExperienceDocumentPath'])
                                
                                # Handle OtherDocumentPath
                                if 'OtherDocumentPath' in record_fields:
                                    setattr(existing_record, 'OtherDocumentPath', record_fields['OtherDocumentPath'])
                                    
                                self._update_record(existing_record, record_fields)
                                updated_ids[f"{table_name}_{record_id}"] = record_id
                            else:
                                # If no record is found, create a new record
                                logging.warning(f"No existing record found with ID {record_id}. Creating a new record.")
                                new_record = model_class(**record_fields)
                                db.session.add(new_record)
                                db.session.commit()  # Commit here to get the ID for the new record
                                new_record_id = getattr(new_record, 'Id', None)
                                updated_ids[f"{table_name}_{new_record_id}"] = new_record_id

                        else:
                            new_record = model_class(**record_fields)
                            db.session.add(new_record)
                            db.session.commit()  # Commit here to get the ID for the new record
                            new_record_id = getattr(new_record, 'Id', None)
                            updated_ids[f"{table_name}_{new_record_id}"] = new_record_id

                else:
                    record_id = fields[0].get('User_Id')
                    existing_record = db.session.query(model_class).filter_by(User_Id=record_id).first()
                    if existing_record:
                        for key, value in record_fields.items():
                            setattr(existing_record, key, value)
                        logging.info(f"Updated {table_name} record with ID {existing_record.User_Id}")
                    else:
                        return {'status': 'error', 'message': f'Record with ID {record_id} not found in {table_name}'}, 404

                db.session.commit()  # Final commit after all updates for this table

            # Step 5: Process file uploads if available
            if request.files:
                file_data = self.process_files(request.files)

                for file_key, file_info in file_data.items():
                    _, table_name, field_name, _ = file_info['key'].split('_')
                    file_path = file_info['path']

                    # Find a matching record in updated_ids for the current table
                    for key, record_id in list(updated_ids.items()):  # Use list() to iterate safely while removing items
                        if table_name in key:
                            try:
                                # Update file path for 'StaffInfo' or 'StaffCnic'
                                if table_name == 'StaffInfo' or table_name == 'StaffCnic':
                                    self.update_file_path(table_name, record_id, field_name, file_path)

                                # If it's not 'StaffCnic', remove the key directly after updating
                                if table_name != 'StaffCnic':
                                    del updated_ids[key]
                            except Exception as e:
                                db.session.rollback()
                                logging.error(f"File association error for {table_name}: {str(e)}")
                                return {'status': 'error', 'message': f'File association error: {str(e)}'}, 500

            logging.info("Employee record updated successfully.")
            return {'status': 'success', 'message': 'Records updated successfully', 'updated_ids': updated_ids}, 200

        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error in processing request: {str(e)}")
            return {'status': 'error', 'message': str(e)}, 500






    def _parse_fields(self, fields):
        """Helper to parse and clean JSON fields, removing 'Filename' key if present."""
        # Check if fields is a list containing a single JSON string
        if isinstance(fields, list) and len(fields) == 1 and isinstance(fields[0], str):
            try:
                # Parse JSON string into a list of dictionaries
                fields = json.loads(fields[0])

                # Ensure fields is a list of dictionaries
                if isinstance(fields, dict):
                    fields = [fields]
                
                # Remove 'Filename' from each item if it exists
                for item in fields:
                    if isinstance(item, dict):
                        item.pop("Filename", None)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decoding error: {str(e)}")
                raise ValueError("Invalid JSON data format")
        
        # Handle case where fields is a single dictionary, not a list
        elif isinstance(fields, dict):
            fields = [fields]
        
        return fields

    def _fetch_existing_record(self, model_class, table_name, record_id):
        """Helper to fetch an existing record by ID."""
        filter_field = 'Staff_ID' if table_name == 'StaffInfo' else 'Id'
        return db.session.query(model_class).filter(getattr(model_class, filter_field) == record_id).first()

    def _update_record(self, record, fields):
        """Helper to update an existing record."""
        for key, value in fields.items():
            setattr(record, key, value)
        logging.info(f"Updated record with ID {fields.get('Staff_ID') or fields.get('Id')}")



class TrainingPostResource(Resource):
    def post(self):
        data = request.get_json()

        # Ensure that the 'Data' key exists
        insert_data = data.get('Data')
        if not insert_data:
            return {'status': 'error', 'message': 'Data is required'}, 400

        # Validate that insert_data is a list of dictionaries
        if not isinstance(insert_data, list) or not all(isinstance(item, dict) for item in insert_data):
            return {'status': 'error', 'message': 'Data should be a list of dictionaries'}, 400

        try:
            # Loop through each record in insert_data
            for item in insert_data:
                # Handle nullable fields by providing default values if not present
                training_record = Training(
                    Training_Trainer=item.get('Training_Trainer'),
                    Training_Location=item.get('Training_Location'),
                    Training_TotalCost=item.get('Training_TotalCost'),
                    Training_FromDate=item.get('Training_FromDate') if item.get('Training_FromDate') else None,  # Allow null for Training_Date
                    Training_ToDate=item.get('Training_ToDate') if item.get('Training_ToDate') else None,  # Allow null for Training_Date
                    Training_CompletionStatus=item.get('Training_CompletionStatus'),  # Allow null for Training_Date
                    Training_Remarks=item.get('Training_Remarks', None),  # Default to None if missing
                    Training_StaffContributionPercentage=item.get('Training_StaffContributionPercentage'),
                    CreatedBy=item.get('CreatedBy'),
                    CreatedDate=item.get('CreatedDate') if item.get('CreatedDate') else datetime.utcnow(),  # Default to current time if missing
                    UpdatedBy=item.get('UpdatedBy'),
                    UpdatedDate=item.get('UpdateDate'),
                    InActive=item.get('InActive', False)  # Default to False if missing
                )
                db.session.add(training_record)
                db.session.flush()  # Flush to get the `Training_Id` after insertion

                # Extract and process the related TrainingStaff data
                training_staff_data = item.get('TrainingStaff', [])
                num_staff = len(training_staff_data)  # Get the number of staff in the current Training record

                if num_staff > 0:
                    # Calculate the contribution amount per staff based on the formula
                    total_cost = training_record.Training_TotalCost
                    staff_percentage = training_record.Training_StaffContributionPercentage
                    contribution_per_staff = (total_cost / 100 * staff_percentage) / num_staff

                    # Loop through each staff record and assign the calculated values
                    for staff_item in training_staff_data:
                        staff_record = TrainingStaff(
                            TrainingStaff_TrainingId=training_record.Training_Id,  # Linking to the Training record
                            TrainingStaff_StaffId=staff_item.get('TrainingStaff_StaffId'),
                            TrainingStaff_ContributionAmount=contribution_per_staff,
                            TrainingStaff_Survey=staff_item.get('TrainingStaff_Survey', None),  # Default to None if missing
                            TrainingStaff_Bond=staff_item.get('TrainingStaff_Bond', None),  # Default to None if missing
                            TrainingStaff_BondStartDate=staff_item.get('TrainingStaff_BondStartDate', None),  # Allow null
                            TrainingStaff_BondEndDate=staff_item.get('TrainingStaff_BondEndDate', None),  # Allow null
                            TrainingStaff_RemainingAmount=contribution_per_staff  # Set the remaining amount equal to the contribution
                        )
                        db.session.add(staff_record)

                else:
                    # If there are no staff, raise an error
                    return {'status': 'error', 'message': 'At least one staff member is required in the TrainingStaff'}, 400

            # Commit the transaction to save both the Training and TrainingStaff records
            db.session.commit()

            return {'status': 'success', 
                    # 'message': f'{len(insert_data)} Training records and {num_staff} TrainingStaff records inserted successfully'}, 201
                    'message': f'{len(insert_data)} records inserted into Training successfully'}, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {'status': 'error', 'message': f'SQLAlchemy Error: {str(e)}'}, 500
        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': f'Error: {str(e)}'}, 500

    def put(self):
        data = request.get_json()

        # Validate input
        update_data = data.get('Data')
        if not update_data:
            return {'status': 'error', 'message': 'Data is required'}, 400

        if not isinstance(update_data, list) or not all(isinstance(item, dict) for item in update_data):
            return {'status': 'error', 'message': 'Data should be a list of dictionaries'}, 400

        try:
            for item in update_data:
                training_id = item.get('Training_Id')
                if not training_id:
                    return {'status': 'error', 'message': 'Training_Id is required for update'}, 400

                # Find the existing training record
                training_record = Training.query.filter_by(Training_Id=training_id).first()

                if training_record:
                    # Update fields for the training record
                    training_record.Training_Trainer = item.get('Training_Trainer', training_record.Training_Trainer)
                    training_record.Training_Location = item.get('Training_Location', training_record.Training_Location)
                    training_record.Training_TotalCost = item.get('Training_TotalCost', training_record.Training_TotalCost)
                    training_record.Training_FromDate = item.get('Training_FromDate', training_record.Training_FromDate)
                    training_record.Training_ToDate = item.get('Training_ToDate', training_record.Training_ToDate)
                    training_record.Training_CompletionStatus = item.get('Training_CompletionStatus', training_record.Training_CompletionStatus)
                    training_record.Training_Remarks = item.get('Training_Remarks', training_record.Training_Remarks)
                    training_record.Training_StaffContributionPercentage = item.get('Training_StaffContributionPercentage', training_record.Training_StaffContributionPercentage)
                    training_record.UpdatedBy = item.get('UpdatedBy', training_record.UpdatedBy)
                    training_record.UpdatedDate = datetime.utcnow()
                    training_record.InActive = item.get('InActive', training_record.InActive)

                    # Handle TrainingStaff records
                    existing_staff_records = TrainingStaff.query.filter_by(TrainingStaff_TrainingId=training_id).all()
                    existing_staff_ids = {record.TrainingStaff_StaffId for record in existing_staff_records}

                    # Process new staff records
                    training_staff_data = item.get('TrainingStaff', [])
                    new_staff_ids = {staff.get('TrainingStaff_StaffId') for staff in training_staff_data}
                    num_staff = len(training_staff_data)

                    if num_staff > 0:
                        total_cost = training_record.Training_TotalCost
                        staff_percentage = training_record.Training_StaffContributionPercentage
                        contribution_per_staff = (total_cost / 100 * staff_percentage) / num_staff

                        # Update existing staff records
                        for staff in training_staff_data:
                            staff_id = staff.get('TrainingStaff_StaffId')
                            if staff_id in existing_staff_ids:
                                staff_record = next((r for r in existing_staff_records if r.TrainingStaff_StaffId == staff_id), None)
                                staff_record.TrainingStaff_Survey = staff.get('TrainingStaff_Survey', staff_record.TrainingStaff_Survey)
                                staff_record.TrainingStaff_Bond = staff.get('TrainingStaff_Bond', staff_record.TrainingStaff_Bond)
                                staff_record.TrainingStaff_BondStartDate = staff.get('TrainingStaff_BondStartDate', staff_record.TrainingStaff_BondStartDate)
                                staff_record.TrainingStaff_BondEndDate = staff.get('TrainingStaff_BondEndDate', staff_record.TrainingStaff_BondEndDate)
                                staff_record.TrainingStaff_ContributionAmount = contribution_per_staff
                                staff_record.TrainingStaff_RemainingAmount = contribution_per_staff

                        # Add new staff records
                        for staff in training_staff_data:
                            if staff.get('TrainingStaff_StaffId') not in existing_staff_ids:
                                new_staff_record = TrainingStaff(
                                    TrainingStaff_TrainingId=training_id,
                                    TrainingStaff_StaffId=staff.get('TrainingStaff_StaffId'),
                                    TrainingStaff_ContributionAmount=contribution_per_staff,
                                    TrainingStaff_Survey=staff.get('TrainingStaff_Survey', None),
                                    TrainingStaff_Bond=staff.get('TrainingStaff_Bond', None),
                                    TrainingStaff_BondStartDate=staff.get('TrainingStaff_BondStartDate', None),
                                    TrainingStaff_BondEndDate=staff.get('TrainingStaff_BondEndDate', None),
                                    TrainingStaff_RemainingAmount=contribution_per_staff
                                )
                                db.session.add(new_staff_record)

                        # Remove staff records not in the updated list
                        for existing_record in existing_staff_records:
                            if existing_record.TrainingStaff_StaffId not in new_staff_ids:
                                db.session.delete(existing_record)

                    else:
                        return {'status': 'error', 'message': 'At least one staff member is required in the TrainingStaff'}, 400

                else:
                    return {'status': 'error', 'message': f'Training record with Training_Id {training_id} not found'}, 404

            # Commit all changes
            db.session.commit()
            return {'status': 'success', 'message': 'Training and TrainingStaff records updated successfully'}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {'status': 'error', 'message': f'SQLAlchemy Error: {str(e)}'}, 500
        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': f'Error: {str(e)}'}, 500

class CampusWiseUser(Resource):
    def post(self):
        try:
            if request.content_type == 'application/json':
                # Parse the JSON body
                data = request.get_json()
                # raw_data = request.data
                # data = json.loads(raw_data)
                # print(request.json)
                # print(request.content_type)

                # Validate that all required fields are present
                if 'User' not in data or 'campus_id' not in data or 'User_Id' not in data:
                    raise BadRequest("User and campus are required fields")

                User = data.get('User')
                User_Id = data.get('User_Id')
                campus_id = data.get('campus_id')
                student_id = data.get('student_id', None)

            else:
                # Handle query parameters using reqparse for non-JSON requests
                parser = reqparse.RequestParser()
                parser.add_argument('User', type=int, location='args', required=True, help='User is required')
                parser.add_argument('User_Id', type=int, location='args')
                parser.add_argument('campus_id', type=int, location='args', required=True, help='campus_id is required')
                parser.add_argument('student_id', type=int, location='args', default=None)

                # Parse arguments
                args = parser.parse_args()
                User = args['User']
                User_Id = args['User_Id']
                campus_id = args['campus_id']
                student_id = args['student_id']

            # Fetching user IDs from the CampusWiseUsersAENTable
            user_ids_query = CampusWiseUsersAEN.query.with_entities(CampusWiseUsersAEN.AEN_user_ids).all()
            userid = [user.AEN_user_ids for user in user_ids_query]

            excluded_user_ids = [2, 16471, 16472, 18203]

            # Fetching based on campus_id and user_type
            if campus_id == 11:
                if User == 1:  # Staffs/Teachers
                    # Get all user type IDs excluding 3 and 7
                    excluded_user_types = [3, 7]
                    user_types = UserType.query.filter(UserType.UserTypeId.notin_(excluded_user_types)).all()
                    UserTypeId = [user_type.UserTypeId for user_type in user_types]

                    if User_Id in [2, 16471, 16472, 18203]:  # Check if user_id matches any of these
                        query = (
                            USERS.query
                            .filter(
                                USERS.Inactive == False,USERS.Status == True,USERS.IsAEN == 1,USERS.UserType_Id.in_(UserTypeId),
                                USERS.Firstname != None                               
                            )
                            .join(Campus, Campus.Id == USERS.CampusId)
                            .join(UserType, UserType.UserTypeId  == USERS.UserType_Id)  # Join the UserType table to get the UserTypeName
                            .add_columns(
                                USERS.User_Id.label('id'),
                                USERS.Firstname.label('Name'),
                                Campus.Name.label('CampusName'),
                                USERS.Status.label('Status'),
                                UserType.UserTypeName.label('UserType'),  # Select UserTypeName from UserType table
                                USERS.Username,
                                USERS.Password
                            )
                        )
                        # Collect the query result into a list of dictionaries
                        users_data = [
                            {
                                'id': user.id,
                                'Name': user.Name,
                                'CampusName': user.CampusName,
                                'Status': "Unblocked" if user.Status else "Blocked", 
                                'UserType': user.UserType,
                                'Username': decrypt(user.Username),
                                'Password': decrypt(user.Password),
                            }
                            for user in query.all()
                        ]

                        # Add password visibility flag
                        return {"data": users_data, "password_hide": False}, 200

                    else:  # If user_id is not in the list [2, 16471, 16472, 18203]
                        query = (
                            USERS.query
                            .filter(
                                USERS.Inactive == False,USERS.Status == True,USERS.IsAEN == 1,
                                USERS.UserType_Id.in_(UserTypeId),
                                USERS.Firstname != None,
                                USERS.User_Id.notin_(userid) # Fetch users whose IDs are not in the user_ids list
                            )
                            .join(Campus, Campus.Id == USERS.CampusId)
                            .join(UserType, UserType.UserTypeId  == USERS.UserType_Id)  # Join the UserType table to get the UserTypeName
                            .add_columns(
                                USERS.User_Id.label('id'),
                                Campus.Name.label('CampusName'),
                                USERS.Status.label('Status'),
                                USERS.Firstname.label('Name'),
                                UserType.UserTypeName.label('UserType'),  # Select UserTypeName from UserType table
                                USERS.Username,
                                literal('Not applicable').label('Password') # Set Password to "Not Applicable"
                            )
                        )
                        # Collect the query result into a list of dictionaries
                        users_data = [
                            {
                                'id': user.id,
                                'Name': user.Name,
                                'UserType': user.UserType,
                                'CampusName': user.CampusName,
                                'Status': "Unblocked" if user.Status else "Blocked",
                                'Username': decrypt(user.Username),
                                'Password': user.Password,
                            }
                            for user in query.all()
                        ]

                        # Add password visibility flag
                        return {"data": users_data, "password_hide": True}, 200

                elif User == 2:
                      # Parent Users
                    # Get all Parent user types (assumed to be UserTypeId = 3)
                    query = (
                        USERS.query
                        .filter(
                            USERS.Inactive == False,USERS.Status == True, USERS.IsAEN == 1,USERS.UserType_Id == 3,  # Assuming 3 is Parent
                            USERS.Firstname != None,
                            USERS.User_Id.notin_(userid)  # Exclude specific user_ids
                        )
                        .join(Campus, Campus.Id == USERS.CampusId)
                        .join(UserType, UserType.UserTypeId  == USERS.UserType_Id)
                        .add_columns(
                            USERS.User_Id.label('id'),
                            USERS.Firstname.label('Name'),
                            Campus.Name.label('CampusName'),
                            USERS.Status.label('Status'),
                            UserType.UserTypeName.label('UserType'),
                            USERS.Username,
                            USERS.Password  # Password shown for Parent users
                        )
                    )

                    # Collect the query result into a list of dictionaries
                    users_data = [
                        {
                            'id': user.id,
                            'Name': user.Name,
                            'UserType': user.UserType,
                            'CampusName': user.CampusName,
                            'Status': "Unblocked" if user.Status else "Blocked",
                            'Username': decrypt(user.Username),
                            'Password': decrypt(user.Password),
                        }
                        for user in query.all()
                    ]

                    # Add password visibility flag
                    return {"data": users_data, "password_hide": False,"isparentuser":1}, 200
                
                elif User == 3:  # Student Users
                    # Get all Student user types (assumed to be UserTypeId = 7)
                    query = (
                        USERS.query
                        .filter(
                            USERS.Inactive == False,USERS.Status == True, USERS.IsAEN == 1,USERS.UserType_Id == 7,  # Assuming 7 is for Students
                            USERS.Firstname != None,
                            USERS.User_Id.notin_(userid)  # Exclude specific user_ids
                        )
                        .join(Campus, Campus.Id == USERS.CampusId)
                        .join(UserType, UserType.UserTypeId == USERS.UserType_Id)  # Join the UserType table to get the UserTypeName
                        .join(StudentInfo, StudentInfo.UserId == USERS.User_Id)  # Join with Students table to fetch Student info
                        .add_columns(
                            USERS.User_Id.label('id'),
                            USERS.Firstname.label('Name'),                           
                            Campus.Name.label('CampusName'),
                            USERS.Status.label('Status'),
                            UserType.UserTypeName.label('UserType'),
                            USERS.Username,
                            USERS.Password,  # Password shown for Student users
                            StudentInfo.Student_ID.label('StudentId')
                                # Add the StudentId from StudentsInformations table
                        )
                    )

                    # Collect the query result into a list of dictionaries
                    users_data = [
                        {
                            'id': user.id,
                            'Name': user.Name,
                            'UserType': user.UserType,
                            'CampusName': user.CampusName,
                            'Status': "Unblocked" if user.Status else "Blocked",
                            'Username': decrypt(user.Username),
                            'Password': decrypt(user.Password),
                            'StudentId': user.StudentId if hasattr(user, 'StudentId') else None,  # Include StudentId from Students table
                        }
                        for user in query.all()
                    ]

                    # Add password visibility flag and student user flag
                    return {"data": users_data, "password_hide": False, "isstudentuser": 1}, 200

            else:
                if (User == 1 ):
                    excluded_user_types = [3, 7]
                    user_types = UserType.query.filter(UserType.UserTypeId.notin_(excluded_user_types)).all()
                    UserTypeId = [user_type.UserTypeId for user_type in user_types]

                    

                    if User_Id in [2, 16471, 16472, 18203]:  # Check if user_id matches any of these
                        query = (
                            USERS.query
                            .filter(
                                USERS.Inactive == False,USERS.Status == True,USERS.IsAEN == 0,USERS.CampusId == campus_id,
                                USERS.UserType_Id.in_(UserTypeId),
                                USERS.User_Id.notin_(excluded_user_ids),
                                USERS.Firstname != None                               
                            )
                            .join(Campus, Campus.Id == USERS.CampusId)
                            .join(UserType, UserType.UserTypeId  == USERS.UserType_Id)  # Join the UserType table to get the UserTypeName
                            .add_columns(
                                USERS.User_Id.label('id'),
                                USERS.Firstname.label('Name'),
                                Campus.Name.label('CampusName'),
                                USERS.Status.label('Status'),
                                UserType.UserTypeName.label('UserType'),  # Select UserTypeName from UserType table
                                USERS.Username,
                                USERS.Password
                            )
                        )
                        # Collect the query result into a list of dictionaries
                        users_data = [
                            {
                                'id': user.id,
                                'Name': user.Name,
                                'UserType': user.UserType,
                                'CampusName': user.CampusName,
                                'Status': "Unblocked" if user.Status else "Blocked",
                                'Username': decrypt(user.Username),
                                'Password': decrypt(user.Password),
                            }
                            for user in query.all()
                        ]

                        # Add password visibility flag
                        return {"data": users_data, "password_hide": False}, 200
                    
                    else:  # If user_id is not in the list [2, 16471, 16472, 18203]
                        query = (
                            USERS.query
                            .filter(
                                USERS.Inactive == False,USERS.Status == True,USERS.IsAEN == 0,USERS.CampusId == campus_id,
                                USERS.UserType_Id.in_(UserTypeId),
                                USERS.Firstname != None,
                                USERS.User_Id.notin_(userid)  # Fetch users whose IDs are not in the user_ids list
                            )
                            .join(Campus, Campus.Id == USERS.CampusId)
                            .join(UserType, UserType.UserTypeId  == USERS.UserType_Id)  # Join the UserType table to get the UserTypeName
                            .add_columns(
                                USERS.User_Id.label('id'),
                                Campus.Name.label('CampusName'),
                                USERS.Status.label('Status'),
                                USERS.Firstname.label('Name'),
                                UserType.UserTypeName.label('UserType'),  # Select UserTypeName from UserType table
                                USERS.Username,
                                literal('Not applicable').label('Password')  # Set Password to "Not Applicable"
                            )
                        )
                        # Collect the query result into a list of dictionaries
                        users_data = [
                            {
                                'id': user.id,
                                'Name': user.Name,
                                'UserType': user.UserType,
                                'Username': decrypt(user.Username),
                                'CampusName': user.CampusName,
                                'Status': "Unblocked" if user.Status else "Blocked",
                                'Password': user.Password,
                            }
                            for user in query.all()
                        ]

                        # Add password visibility flag
                        return {"data": users_data, "password_hide": True}, 200

                elif User == 2:
                    if student_id == 0:
                        # Fetch parent users based on CampusId and other filters when student_id is 0
                        query = (
                            USERS.query
                            .filter(
                                USERS.Inactive == False,
                                USERS.Status == True,
                                USERS.CampusId == campus_id,  # Assuming `CampusId` filter is needed
                                USERS.IsAEN == 0,
                                USERS.UserType_Id == 3,  # Assuming 3 is Parent
                                USERS.Firstname != None,
                                USERS.User_Id.notin_(userid)  # Exclude specific user_ids
                            )
                            .join(Campus, Campus.Id == USERS.CampusId)
                            .join(UserType, UserType.UserTypeId  == USERS.UserType_Id)  # Assuming there's a Campus table for CampusName
                            .add_columns(
                                USERS.User_Id.label('id'),
                                USERS.Firstname.label('Name'),
                                UserType.UserTypeName.label('UserType'),
                                USERS.Username,
                                USERS.Password,
                                Campus.Name.label('CampusName'),
                                USERS.Status.label('Status')  # Status will be used to determine "Unblocked" or "Blocked"
                            )
                        )

                        # Collect the query result into a list of dictionaries
                        users_data = [
                            {
                                'id': user.id,
                                'Name': user.Name,
                                'UserType': user.UserType,
                                'Username': decrypt(user.Username),
                                'Password': decrypt(user.Password),
                                'CampusName': user.CampusName,
                                'Status': "Unblocked" if user.Status else "Blocked",  # Map boolean to string
                            }
                            for user in query.all()
                        ]

                        # Return the response
                        return {"data": users_data, "password_hide": False, "isparentuser": 1}, 200

                    else:
                        # Fetch the Father's CNIC from StudentsInformations table using the provided StudentId
                        father_cnic = db.session.query(StudentInfo.Stu_FCNIC).filter(StudentInfo.Student_ID == student_id).scalar()

                        if father_cnic:
                            # Fetch parent users with the matching GuardianCNIC
                            query = (
                                USERS.query
                                .filter(
                                    USERS.GuardianCNIC == father_cnic,
                                    USERS.Inactive == False,
                                    USERS.IsAEN == 0,
                                    USERS.UserType_Id == 3,
                                    USERS.Firstname != None,
                                    USERS.User_Id.notin_(userid)  # Exclude specific user_ids
                                )
                                .join(Campus, Campus.Id == USERS.CampusId)
                                .join(UserType, UserType.UserTypeId  == USERS.UserType_Id)  # Assuming there's a Campus table for CampusName
                                .add_columns(
                                    USERS.User_Id.label('id'),
                                    USERS.Firstname.label('Name'),
                                    UserType.UserTypeName.label('UserType'),
                                    USERS.Username,
                                    USERS.Password,
                                    Campus.Name.label('CampusName'),
                                    USERS.Status.label('Status')
                                )
                            )

                            # Collect the query result into a list of dictionaries
                            users_data = [
                                {
                                    'id': user.id,
                                    'Name': user.Name,
                                    'UserType': user.UserType,
                                    'Username': decrypt(user.Username),
                                    'Password': decrypt(user.Password),
                                    'CampusName': user.CampusName,
                                    'Status': "Unblocked" if user.Status else "Blocked",
                                }
                                for user in query.all()
                            ]

                            # Return the response
                            return {"data": users_data, "password_hide": False, "isparentuser": 1}, 200

                        else:
                            # Handle error when parent is not found
                            return {"error": "Parent not found"}, 404

                elif User == 3:
                    # Get all Student user types (assumed to be UserTypeId = 7)
                    query = (
                        USERS.query
                        .filter(
                            USERS.Inactive == False, 
                            USERS.Status == True, 
                            USERS.IsAEN == 0, 
                            USERS.UserType_Id == 7,  # Assuming 7 is Student
                            USERS.Firstname != None,
                            USERS.User_Id.notin_(userid)  # Exclude specific user_ids
                        )
                        .join(Campus, Campus.Id == USERS.CampusId)
                        .join(UserType, UserType.UserTypeId  == USERS.UserType_Id)
                        .join(StudentInfo, StudentInfo.UserId == USERS.User_Id)  # Join with StudentsInformations table to get StudentId
                        .add_columns(
                            USERS.User_Id.label('id'),
                            USERS.Firstname.label('Name'),
                            UserType.UserTypeName.label('UserType'),
                            USERS.Username,
                            USERS.Password,
                            Campus.Name.label('CampusName'),
                            USERS.Status.label('Status'),
                            StudentInfo.Student_ID.label('StudentId')  # Add the StudentId from StudentsInformations table
                        )
                    )

                    # Collect the query result into a list of dictionaries
                    users_data = [
                        {
                            'id': user.id,
                            'Name': user.Name,
                            'UserType': user.UserType,
                            'Username': decrypt(user.Username),
                            'Password': decrypt(user.Password),
                            'CampusName': user.CampusName,
                            'Status': "Unblocked" if user.Status else "Blocked", 
                            'StudentId': user.StudentId if hasattr(user, 'StudentId') else None,  # Include StudentId from StudentsInformations table
                        }
                        for user in query.all()
                    ]

                    # Add password visibility flag and student user flag
                    return {"data": users_data, "password_hide": False, "isstudentuser": 1}, 200

        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def put(self):
        try:
            # Step 1: Determine content type and extract data
            data = self._extract_data_from_request(request)

            # Step 2: Validate the required fields
            user_id = self._validate_and_get_user_id(data)

            # Step 3: Fetch the user and ensure the user is active
            user = self._fetch_user(user_id)

            # Step 4: Dynamically update user fields
            self._update_user_fields(user, data)

            # Step 5: Handle campus assignments
            self._handle_campus_assignments(user, data)

            # Step 6: Handle roles assignments
            self._handle_roles_assignments(user, data)

            # Step 7: Handle class assignments
            self._handle_class_assignments(user, data)

            # Step 8: Return success response
            return {"message": "User updated successfully"}, 200

        except BadRequest as e:
            return {"error": str(e)}, 400
        except NotFound as e:
            return {"error": str(e)}, 404
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def _extract_data_from_request(self, request):
        """ Extract data from the request depending on its content type. """
        if request.content_type == 'application/json':
            return request.get_json()
        else:
            data = request.form
            print("Received Form Data:", data)  # Log form data for debugging purposes
            return data

    def _validate_and_get_user_id(self, data):
        """ Validate the presence of 'User_Id' and return its value. """
        if 'User_Id' not in data:
            raise BadRequest("User_Id is required")
        return data.get('User_Id')

    def _fetch_user(self, user_id):
        """ Fetch the user from the database and ensure the user is active. """
        user = db.session.query(USERS).options(joinedload(USERS.USERCAMPUS)).filter_by(User_Id=user_id).one_or_none()
        if user is None or not user.Status:
            abort(404)  # User not found or inactive
        return user

    def _update_user_fields(self, user, data):
        """ Update user fields dynamically based on the provided data. """
        user.Firstname = data.get('Firstname', user.Firstname)
        if data.get('Password'):
            user.Password = encrypt(data.get('Password'))
        user.EMail = data.get('EMail', user.EMail)
        user.MobileNo = data.get('MobileNo', user.MobileNo)
        user.UserType_Id = data.get('UserType_Id', user.UserType_Id)

        user.LastModified = datetime.utcnow()
        user.Status = True
        user.Inactive = False  # Assuming activation of the user

        # Commit changes to the database
        db.session.commit()

    def _handle_campus_assignments(self, user, data):
        """ Handle the campus assignments if selected_campus_str is provided. """
        selected_campus_str = data.get('selectedCampus', '[]')
        if selected_campus_str != '[]':
            if data.get('UserType_Id') not in [3, 7]:
                selected_campus = self._parse_and_validate_campus(selected_campus_str)
                self._update_user_campuses(user.User_Id, selected_campus)

    def _parse_and_validate_campus(self, selected_campus_str):
        """ Parse and validate the campus IDs. """
        try:
            selected_campus = ast.literal_eval(selected_campus_str)
        except ValueError:
            raise BadRequest("Invalid campus data format.")
        
        valid_campus_ids = db.session.query(Campus.Id).filter(Campus.Id.in_(selected_campus)).all()
        valid_campus_ids = [campus.Id for campus in valid_campus_ids]
        
        invalid_campuses = [c for c in selected_campus if c not in valid_campus_ids]
        if invalid_campuses:
            raise BadRequest(f"Invalid Campus IDs: {invalid_campuses}")
        
        return selected_campus

    def _update_user_campuses(self, user_id, selected_campus):
        """ Update UserCampus assignments based on selected campuses. """
        user_campuses = db.session.query(UserCampus).filter(UserCampus.UserId == user_id).all()
        existing_campus_ids = {uc.CampusId for uc in user_campuses}

        # Identify new campuses to be added
        new_campuses = [campus_id for campus_id in selected_campus if campus_id not in existing_campus_ids]
        removed_campuses = [uc for uc in user_campuses if uc.CampusId not in selected_campus]

        # Add new UserCampus records
        staff_id = user_campuses[0].StaffId if user_campuses else None
        for campus_id in new_campuses:
            user_campus = UserCampus(
                UserId=user_id,
                StaffId=staff_id,
                CampusId=campus_id,
                Status=True,
                CreateDate=datetime.utcnow(),
                Date=datetime.utcnow()
            )
            db.session.add(user_campus)

        db.session.commit()

        # Remove old UserCampus records
        for user_campus_to_remove in removed_campuses:
            db.session.delete(user_campus_to_remove)

        db.session.commit()

    def _handle_roles_assignments(self, user, data):
        """ Handle the role assignments if selected_role_str is provided. """
        selected_roles_str = data.get('selectedRole', '[]')
        if selected_roles_str != '[]':
            selected_roles = self._parse_and_validate_roles(selected_roles_str)
            self._update_user_roles(user.User_Id, selected_roles)

    def _parse_and_validate_roles(self, selected_roles_str):
        """ Parse and validate the role IDs. """
        try:
            selected_roles = ast.literal_eval(selected_roles_str)
            if not all(isinstance(role, int) for role in selected_roles):
                raise ValueError("All role IDs must be integers.")
        except (ValueError, SyntaxError) as e:
            raise BadRequest(f"Invalid format for selectedRole: {str(e)}")

        return selected_roles

    def _update_user_roles(self, user_id, selected_roles):
        """ Update the user roles based on the selected roles. """
        db.session.query(LNK_USER_ROLE).filter(LNK_USER_ROLE.User_Id == user_id).delete()
        db.session.commit()

        for role_id in selected_roles:
            if not db.session.query(LNK_USER_ROLE).filter(LNK_USER_ROLE.User_Id == user_id, LNK_USER_ROLE.Role_Id == role_id).first():
                new_user_role = LNK_USER_ROLE(User_Id=user_id, Role_Id=role_id)
                db.session.add(new_user_role)

        db.session.commit()

    def _handle_class_assignments(self, user, data):
        """ Handle the class assignments if selected_class_str is provided. """
        selected_class_str = data.get('selectedClass', '[]')
        if selected_class_str != '[]':
            selected_class = self._parse_and_validate_class(selected_class_str)
            self._update_user_classes(user.User_Id, selected_class)

    def _parse_and_validate_class(self, selected_class_str):
        """ Parse and validate class IDs. """
        try:
            selected_class = ast.literal_eval(selected_class_str)
        except ValueError:
            raise BadRequest("Invalid class data format.")
        
        return selected_class

    def _update_user_classes(self, user_id, selected_class):
        """ Update the user class assignments based on the selected classes. """
        db.session.query(UserClassAccess).filter(UserClassAccess.UserId == user_id).delete()
        db.session.commit()

        for class_id in selected_class:
            user_class_access = UserClassAccess(UserId=user_id, ClassId=class_id)
            db.session.add(user_class_access)

        db.session.commit()





   #Testing method
    # def put(self):
    #     try:
    #         # Check the content type of the request (either JSON or form data)
    #         if request.content_type == 'application/json':
    #             data = request.get_json()
    #         else:
    #             data = request.form
    #             print("Received Form Data:", data)  # Add logging to see the raw data

    #         # Validate the required fields in the incoming data
    #         if 'user_Id' not in data:
    #             raise BadRequest("user_Id is required")

    #         # Extract data from the request
    #         user_id = data.get('user_Id')
    #         first_name = data.get('Firstname')  
    #         password = data.get('Password')
    #         email = data.get('EMail', None)
    #         mobile_no = data.get('MobileNo', None)
    #         user_type_id = data.get('UserType_Id', None)
    #         selected_roles_str = data.get('selectedRole', '[]')
    #         selected_campus_str = data.get('selectedCampus', '[]')
    #         selected_class_str = data.get('selectedClass', '[]')

    #         # Fetch the user along with the associated UserCampus
    #         user = db.session.query(USERS).options(joinedload(USERS.USERCAMPUS)).filter_by(User_Id=user_id).one_or_none()
    #         if user is None or not user.Status:
    #             abort(404)  # This raises a 404 error

    #         # Fetch the first associated UserCampus to get the staffId (if available)
    #         staff_id = None
    #         if user.USERCAMPUS and len(user.USERCAMPUS) > 0:
    #             staff_id = user.USERCAMPUS[0].StaffId

    #         # Dynamically update fields only if they are provided in the request
    #         if first_name is not None:  # Ensure the field isn't None before updating
    #             user.Firstname = first_name
    #         if password:
    #             user.Password = encrypt(password)
    #         if email is not None:
    #             user.EMail = email
    #         if mobile_no is not None:
    #             user.MobileNo = mobile_no
    #         if user_type_id is not None:
    #             user.UserType_Id = user_type_id

    #         user.LastModified = datetime.utcnow()  # Set the last modified date to the current time
    #         user.Status = True
    #         user.Inactive = False  # Assuming you want to activate the user

    #         # Commit changes to the database for basic user info
    #         db.session.commit()

    #         # Handle campus assignments only if selected_campus_str is provided and not empty
    #         if selected_campus_str and selected_campus_str != '[]':
    #             if user_type_id not in [3, 7]:  # If the user type is not 3 or 7, proceed with campus updates.

    #                 # Parse the selected_campus string to a list
    #                 try:
    #                     selected_campus = ast.literal_eval(selected_campus_str)
    #                 except ValueError:
    #                     return {"error": "Invalid campus data format."}, 400

    #                 # Fetch valid campus IDs from the Campus table (ensure they exist)
    #                 valid_campus_ids = db.session.query(Campus.Id).filter(Campus.Id.in_(selected_campus)).all()
    #                 valid_campus_ids = [campus.Id for campus in valid_campus_ids]  # List of valid campus IDs

    #                 # Ensure all selected campuses are valid
    #                 invalid_campuses = [c for c in selected_campus if c not in valid_campus_ids]
    #                 if invalid_campuses:
    #                     return {"error": f"Invalid Campus IDs: {invalid_campuses}"}, 400

    #                 # Fetch existing UserCampus records for the user to check which campuses they're currently associated with
    #                 user_campuses = db.session.query(UserCampus).filter(UserCampus.UserId == user_id).all()
    #                 existing_campus_ids = {uc.CampusId for uc in user_campuses}  # Set of existing campus IDs for the user

    #                 # Identify new campuses to be added
    #                 new_campuses = [campus_id for campus_id in valid_campus_ids if campus_id not in existing_campus_ids]

    #                 # Identify campuses to be removed
    #                 removed_campuses = [uc for uc in user_campuses if uc.CampusId not in selected_campus]

    #                 # Add new UserCampus records for new campuses
    #                 for campus_id in new_campuses:
    #                     user_campus = UserCampus(
    #                         UserId=user_id,
    #                         StaffId=staff_id,
    #                         CampusId=campus_id,
    #                         Status=True,
    #                         CreateDate=datetime.utcnow(),
    #                         Date=datetime.utcnow()
    #                     )
    #                     db.session.add(user_campus)

    #                 # Commit after adding new campuses
    #                 db.session.commit()

    #                 # Remove UserCampus records for campuses no longer associated
    #                 for user_campus_to_remove in removed_campuses:
    #                     db.session.delete(user_campus_to_remove)

    #                 # Commit after removing old campuses
    #                 db.session.commit()

    #         # Handle roles only if provided
    #         if selected_roles_str and selected_roles_str != '[]':
    #             try:
    #                 # Parse the string to a list using ast.literal_eval
    #                 selected_roles = ast.literal_eval(selected_roles_str)

    #                 # Ensure selected_roles is a list of integers
    #                 if not all(isinstance(role, int) for role in selected_roles):
    #                     raise ValueError("All role IDs must be integers.")

    #             except (ValueError, SyntaxError) as e:
    #                 return {"error": f"Invalid format for selectedRole. {str(e)}"}, 400

    #             # First, delete old roles that are no longer selected
    #             db.session.query(LNK_USER_ROLE).filter(LNK_USER_ROLE.User_Id == user_id).delete()

    #             # Commit changes (roles deletion)
    #             db.session.commit()

    #             # Add new roles based on selected_roles, but ensure they don't already exist
    #             for role_id in selected_roles:
    #                 # Check if the role already exists for the user
    #                 existing_role = db.session.query(LNK_USER_ROLE).filter(
    #                     LNK_USER_ROLE.User_Id == user_id,
    #                     LNK_USER_ROLE.Role_Id == role_id
    #                 ).first()
                    
    #                 if not existing_role:
    #                     new_user_role = LNK_USER_ROLE(User_Id=user_id, Role_Id=role_id)
    #                     db.session.add(new_user_role)

    #             # Commit changes to the database (add new roles)
    #             db.session.commit()

    #         #Handle class assignments
    #         if selected_class_str and selected_class_str != '[]':

    #             try:
    #                 selected_class = ast.literal_eval(selected_class_str)
    #             except ValueError:
    #                 return {"error": "Invalid campus data format."}, 400
                
    #             # Fetch all UserClassAccess records for the specified user
    #             user_classes = db.session.query(UserClassAccess).filter(UserClassAccess.UserId == user_id).all()

    #             # # Check if there are any records to delete
    #             if user_classes:  # This checks if the list is not empty
    #                 for user_class in user_classes:
    #             #         # Find the UserClassAccess record by its Id
    #                     userclassaccess = db.session.query(UserClassAccess).get(user_class.Id)  # Find by Id
    #                     if userclassaccess:  # Ensure the record exists
    #                         db.session.delete(userclassaccess)  # Mark for deletion

    #             # # Commit changes after deletion
    #             db.session.commit()

    #             # # Add new UserClassAccess records based on selected_class
    #             if selected_class:  # If there are selected classes
    #                 for i in range(len(selected_class)):  # Loop from 0 to len(selected_class) - 1
    #                     class_id = int(selected_class[i])  # Convert class_id to integer (equivalent to Convert.ToInt32)
    #                     userclassaccess = UserClassAccess(UserId=int(user_id), ClassId=class_id)  # Create a new record
    #                     db.session.add(userclassaccess)  # Add the new record to the session

    #                  # Commit changes after adding all new records
    #                     db.session.commit()      
        
                
                   


            

    #         # Return success response
    #         return {"message": "User updated successfully"}, 200

    #     except BadRequest as e:
    #         return {"error": str(e)}, 400
    #     except NotFound as e:
    #         return {"error": str(e)}, 404
    #     except InternalServerError as e:
    #         return {"error": "An internal server error occurred. Please try again later."}, 500
    #     except Exception as e:
    #         return {"error": f"An unexpected error occurred: {str(e)}"}, 500




class DocumentsUploader(Resource):

    def post(self):
        try:
            logging.info("Received request to create/update employee record.")

            # Ensure that both form data and files are present in the request
            if not request.files or not request.form:
                logging.warning("No file or form data found in the request.")
                return {'message': 'No file or form data in the request'}, 400

            # Process form data
            form_data = request.form.to_dict(flat=False)  # Use flat=False for multi-valued keys

            # Handle multiple sections of form data: StaffEducation, StaffExperience, StaffOther, StaffCnic, and StaffInfo
            staff_education_data = form_data.get('StaffEducation')
            staff_experience_data = form_data.get('StaffExperience')
            staff_other_data = form_data.get('StaffOther')
            staff_cnic_data = form_data.get('StaffCnic')
            staff_info_data = form_data.get('StaffInfo')  # New StaffInfo data

            # Initialize the record variables to None initially
            staff_education = None
            staff_experience = None
            staff_other = None
            staff_cnic = None
            staff_info = None  # New variable for StaffInfo
            request_status = None  # To store the RequestStatus

            # Validate StaffEducation data if present
            if staff_education_data:
                logging.info("Processing StaffEducation data.")
                staff_education = self.process_staff_education(staff_education_data[0])

            # Validate StaffExperience data if present
            if staff_experience_data:
                logging.info("Processing StaffExperience data.")
                staff_experience = self.process_staff_experience(staff_experience_data[0])

            # Validate StaffOther data if present
            if staff_other_data:
                logging.info("Processing StaffOther data.")
                staff_other = self.process_staff_other(staff_other_data[0])

            # Validate StaffCnic data if present
            if staff_cnic_data:
                logging.info("Processing StaffCnic data.")
                staff_cnic = self.process_staff_cnic(staff_cnic_data[0])

            # Validate StaffInfo data if present (new case for StaffInfo)
            if staff_info_data:
                logging.info("Processing StaffInfo data.")
                staff_info, request_status = self.process_staff_info(staff_info_data[0])
                if staff_info is None:
                    logging.error("StaffInfo processing failed. Skipping this part of the request.")
                    return {'message': 'Invalid StaffInfo data'}, 400


            # Process files (can be one or more fields)
            file_keys = {
                'StaffEducation-EducationDocumentPath': 'StaffEducation',
                'StaffExperience-ExperienceDocumentPath': 'StaffExperience',
                'StaffOther-OtherDocumentPath': 'StaffOther',
                'StaffCnic-FrontCNICDocumentPath': 'StaffCnic',
                'StaffCnic-BackCNICDocumentPath': 'StaffCnic',
                'StaffInfo-PhotoPath': 'StaffInfo',  # New field for StaffInfo Photo
            }
            file_paths = {}
            for file_key, table in file_keys.items():
                file = request.files.get(file_key)
                if file:
                    # Log which file and table is being processed
                    logging.info(f"Processing file for {table}: {file_key}")

                    # Determine staff_id based on which table is being processed
                    staff_id = None
                    staff_record = None  # This will hold the actual inserted record

                    if table == 'StaffEducation' and staff_education:
                        staff_id = staff_education.StaffId
                        db.session.add(staff_education)
                        db.session.commit()  # Commit to generate the primary key (Id)
                        staff_record = staff_education
                    elif table == 'StaffExperience' and staff_experience:
                        staff_id = staff_experience.StaffId
                        db.session.add(staff_experience)
                        db.session.commit()  # Commit to generate the primary key (Id)
                        staff_record = staff_experience
                    elif table == 'StaffOther' and staff_other:
                        staff_id = staff_other.StaffId
                        db.session.add(staff_other)
                        db.session.commit()  # Commit to generate the primary key (Id)
                        staff_record = staff_other
                    elif table == 'StaffCnic' and staff_cnic:
                        staff_id = staff_cnic.StaffId
                        db.session.add(staff_cnic)
                        db.session.commit()  # Commit to generate the primary key (Id)
                        staff_record = staff_cnic
                    elif table == 'StaffInfo' and staff_info:
                        staff_id = staff_info.Staff_ID
                        staff_record = staff_info
                        # Skip history tracking for StaffInfo, as per requirement

                    if staff_record:
                        # Now get the actual record's primary key (Id) for all other tables except StaffInfo
                        if table != 'StaffInfo':
                            record_id = staff_record.Id  # This is the primary key of the inserted record
                        else:
                            record_id = staff_record.Staff_ID  # Use Staff_ID for StaffInfo

                        # Process the file and save the file path to the record
                        file_path = self.process_files({file_key: file}, staff_id, table)

                        # Assign the file path to the corresponding attribute
                        if table == 'StaffEducation' and staff_education:
                            staff_education.EducationDocumentPath = file_path
                        elif table == 'StaffExperience' and staff_experience:
                            staff_experience.ExperienceDocumentPath = file_path
                        elif table == 'StaffOther' and staff_other:
                            staff_other.OtherDocumentPath = file_path
                        elif table == 'StaffCnic' and staff_cnic:
                            if file_key == 'StaffCnic-FrontCNICDocumentPath':
                                staff_cnic.FrontCNICDocumentPath = file_path
                            elif file_key == 'StaffCnic-BackCNICDocumentPath':
                                staff_cnic.BackCNICDocumentPath = file_path
                        elif table == 'StaffInfo' and staff_info:
                            staff_info.PhotoPath = file_path
                            # Do not insert history for StaffInfo here, as it's excluded

                        # Insert history record after file is processed (skip for StaffInfo)
                        if table != 'StaffInfo':
                            history_record = Employee_Doc_History(
                                RecordId=record_id,  # Use the actual Id of the inserted record
                                FilePath=file_path,  # The path to the uploaded file
                                Type=file_key.split('-')[1],  # The document type (e.g., 'FrontCNIC', 'EducationDocument')
                                TableName=table,  # The table name (e.g., 'StaffEducation', 'StaffCnic')
                                CreatedAt=datetime.utcnow() + timedelta(hours=5)  # The timestamp of when the record is created
                            )
                            db.session.add(history_record)
                    else:
                        logging.warning(f"StaffId not found for {table}.")


            # Handle update logic for StaffInfo PhotoPath
            if staff_info:
                logging.info(f"StaffInfo data processed: {staff_info}")
                if not staff_info.Staff_ID:
                    logging.error("StaffId is missing in StaffInfo.")
                    return {'message': 'StaffId is missing in StaffInfo data'}, 400
                
                # Try to find the existing StaffInfo record
                # existing_staff_info = StaffInfo.query.filter_by(Staff_ID=staff_info.Staff_ID).first()

                # if existing_staff_info:
                #     # If the record exists, update the PhotoPath
                #     existing_staff_info.PhotoPath = staff_info.PhotoPath
                #     existing_staff_info.UpdaterId = staff_info.UpdaterId
                #     existing_staff_info.UpdateDate = staff_info.UpdateDate
                #     db.session.commit()
                #     logging.info(f"Updated PhotoPath for StaffId {staff_info.Staff_ID}")
                # else:
                #     logging.warning(f"No existing StaffInfo record found for StaffId {staff_info.Staff_ID}.")

                # Create StaffInfo_File record (including RequestStatus)
                staff_info_file = StaffInfo_File(
                    StaffId=staff_info.Staff_ID,
                    UpdaterId=staff_info.UpdaterId,  
                    UpdateDate=staff_info.UpdateDate,
                    RequestStatus=request_status,  # Get RequestStatus from form data
                    PhotoPath=staff_info.PhotoPath  # Ensure PhotoPath from the staff_info object
                )
                db.session.add(staff_info_file)

                # # Insert history record for StaffInfo PhotoPath
                # history_record = Employee_Doc_History(
                #     RecordId=staff_info.Staff_ID,
                #     FilePath=staff_info.PhotoPath,
                #     Type='PhotoPath',  # This is the type of the document
                #     TableName='StaffInfo',  # The table name
                #     CreatedAt=datetime.utcnow()
                # )
                # db.session.add(history_record)

            # Commit all other data to the database if the record exists
            if staff_education:
                db.session.add(staff_education)
            if staff_experience:
                db.session.add(staff_experience)
            if staff_other:
                db.session.add(staff_other)
            if staff_cnic:
                db.session.add(staff_cnic)

            db.session.commit()

            logging.info(f"Files saved successfully: {file_paths}")

            return {'message': 'Employee record created successfully'}, 200

        except Exception as e:
            logging.error(f"Error occurred while processing the request: {e}")
            db.session.rollback()  # Rollback any database changes in case of an error
            return {'message': 'An error occurred while processing the request', 'error': str(e)}, 500

    def process_staff_info(self, data):
        try:
            staff_info = json.loads(data)  # Parse the data as a dictionary

            if not isinstance(staff_info, dict):
                logging.error("StaffInfo data is not a valid dictionary.")
                return None, None  # Return None for StaffInfo and RequestStatus

            logging.info(f"Processed StaffInfo data: {staff_info}")

            staff_id = staff_info.get("Staff_ID")
            if not staff_id:
                logging.warning("Missing required StaffId in StaffInfo data.")
                return None, None  # Return None for StaffInfo and RequestStatus

            request_status = staff_info.get("RequestStatus")

            # Creating a new StaffInfo object
            new_staff_info = StaffInfo(
                Staff_ID=staff_id,
                UpdateDate=staff_info.get("UpdateDate"),
                UpdaterId=staff_info.get("UpdaterId"),
                PhotoPath=None  # Placeholder, will be updated later
            )

            return new_staff_info, request_status

        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error: {e} while parsing StaffInfo data: {data}")
            return None, None
        except Exception as e:
            logging.error(f"Unexpected error while processing StaffInfo: {e}")
            return None, None








    def process_staff_education(self, data):
        try:
            staff_education = json.loads(data)
            if isinstance(staff_education, list):
                staff_education = staff_education[0]
            staff_id = staff_education.get("StaffId")
            if not staff_id:
                logging.warning("Missing required StaffId in StaffEducation data.")
                return None

            # Create StaffEducation record
            new_staff_education = StaffEducation(
                StaffId=staff_id,
                Year=staff_education.get("Year"),
                EducationTypeId=staff_education.get("EducationTypeId"),
                FieldName=staff_education.get("FieldName"),
                Institution=staff_education.get("Institution"),
                Grade=staff_education.get("Grade"),
                Status=staff_education.get("Status"),
                CampusId=staff_education.get("CampusId"),
                CreatorId=staff_education.get("CreatorId"),
                CreateDate=staff_education.get("CreateDate"),
                IsFromProfile = staff_education.get("IsFromProfile"),
                RequestStatus = staff_education.get("RequestStatus"),
                EducationDocumentPath=None  # Placeholder, will be updated later
            )
            return new_staff_education

        except Exception as e:
            logging.warning(f"Error parsing StaffEducation data: {e}")
            return None

    def process_staff_experience(self, data):
        try:
            staff_experience = json.loads(data)
            if isinstance(staff_experience, list):
                staff_experience = staff_experience[0]
            staff_id = staff_experience.get("StaffId")
            if not staff_id:
                logging.warning("Missing required StaffId in StaffExperience data.")
                return None

            # Create StaffExperience record
            new_staff_experience = StaffExperience(
                StaffId=staff_id,
                CompanyName=staff_experience.get("CompanyName"),
                Position=staff_experience.get("Position"),
                StartDate=staff_experience.get("StartDate"),
                EndDate=staff_experience.get("EndDate"),
                Status=staff_experience.get("Status"),
                CampusId=staff_experience.get("CampusId"),
                CreatorId=staff_experience.get("CreatorId"),
                CreateDate=staff_experience.get("CreateDate"),
                IsFromProfile=staff_experience.get("IsFromProfile"),
                RequestStatus = staff_experience.get("RequestStatus"),
                ExperienceDocumentPath=None  # Placeholder, will be updated later
            )
            return new_staff_experience

        except Exception as e:
            logging.warning(f"Error parsing StaffExperience data: {e}")
            return None

    def process_staff_other(self, data):
        try:
            staff_other = json.loads(data)
            if isinstance(staff_other, list):
                staff_other = staff_other[0]
            staff_id = staff_other.get("StaffId")
            if not staff_id:
                logging.warning("Missing required StaffId in StaffOther data.")
                return None

            # Create StaffOther record
            new_staff_other = StaffOther(
                StaffId=staff_id,
                Title=staff_other.get("Title"),
                Description=staff_other.get("Description"),
                Status=staff_other.get("Status"),
                CampusId=staff_other.get("CampusId"),
                CreatorId=staff_other.get("CreatorId"),
                CreateDate=staff_other.get("CreateDate"),
                IsFromProfile = staff_other.get("IsFromProfile"),
                RequestStatus = staff_other.get("RequestStatus"),
                OtherDocumentPath=None  # Placeholder, will be updated later
            )
            return new_staff_other

        except Exception as e:
            logging.warning(f"Error parsing StaffOther data: {e}")
            return None

    def process_staff_cnic(self, data):
        try:
            staff_cnic = json.loads(data)
            if isinstance(staff_cnic, list):
                staff_cnic = staff_cnic[0]
            staff_id = staff_cnic.get("StaffId")
            if not staff_id:
                logging.warning("Missing required StaffId in StaffCnic data.")
                return None

            # Create StaffCnic record
            new_staff_cnic = StaffCnic(
                StaffId=staff_id,
                Status=staff_cnic.get("Status"),
                CampusId=staff_cnic.get("CampusId"),
                CreatorId=staff_cnic.get("CreatorId"),
                CreateDate=staff_cnic.get("CreateDate"),
                IsFromProfile = staff_cnic.get("IsFromProfile"),
                RequestStatus = staff_cnic.get("RequestStatus"),
                RequestStatusBack = staff_cnic.get("RequestStatusBack"),
                FrontCNICDocumentPath=None,  # Placeholder, will be updated later
                BackCNICDocumentPath=None   # Placeholder, will be updated later
            )
            return new_staff_cnic

        except Exception as e:
            logging.warning(f"Error parsing StaffCnic data: {e}")
            return None

    def process_files(self, files, staff_id, table_name):
        """
        Handles the file uploads and saves them to the appropriate locations.
        """
        file_data = {}
        BASE_UPLOAD_FOLDER = 'uploads'  # Base folder is temp

        for key, file in files.items():
            logging.info(f"Processing file: {key}")

            if file.filename == '':  # If filename is empty, skip the file
                logging.warning(f"Skipping empty file: {key}")
                continue

            # Sanitize the filename
            filename = secure_filename(file.filename)

            # Use dynamic table and field names for folder structure
            field_name = key.split('-')[-1]  # Extract the document field name
            table_folder = os.path.join(BASE_UPLOAD_FOLDER, table_name)
            column_folder = os.path.join(table_folder, field_name)

            # Ensure the folder structure exists
            if not os.path.exists(column_folder):
                try:
                    os.makedirs(column_folder)
                    logging.info(f"Created directory structure at {column_folder}")
                except Exception as e:
                    logging.error(f"Error creating directory structure at {column_folder}: {e}")
                    raise

            # Construct the file path with the record ID, staff ID, and sanitized filename
            file_path = os.path.join(column_folder, f"{staff_id}_{filename}")

            # Save the file to the disk
            try:
                file.save(file_path)
                logging.info(f"File saved successfully at {file_path}")
            except Exception as e:
                logging.error(f"Error saving file {filename}: {e}")
                raise

            # Store file path in the dictionary
            file_data[key] = {'key': key, 'path': file_path}

        # Return the path of the processed file for the given key
        return file_data[key]['path']

class ChangePasswordPostResource(Resource):
    def post(self):
        data = request.get_json()

        # Ensure that the 'data' key exists
        change_password_data = data.get('data')
        if not change_password_data:
            return {'status': 'error', 'message': 'Data is required'}, 400

        # Validate that the data is a list with exactly one dictionary
        if not isinstance(change_password_data, list) or len(change_password_data) != 1 or not isinstance(change_password_data[0], dict):
            return {'status': 'error', 'message': 'Data should be a list with exactly one dictionary'}, 400

        # Extract the data for the user to update
        item = change_password_data[0]
        userid = item.get('userid')
        old_password = item.get('oldPassword')
        new_password = item.get('newPassword')

        # Validate presence of necessary fields
        if not userid or not old_password or not new_password:
            return {'status': 'error', 'message': 'userid, oldPassword, and newPassword are required'}, 400

        try:
            # Retrieve the user from the database
            user = USERS.query.filter_by(User_Id=userid).first()

            # Check if user exists
            if not user:
                return {'status': 'error', 'message': 'User not found'}, 404

            # Encrypt the incoming old password for comparison
            encrypted_old_password = encrypt(old_password)

            # Check if the encrypted old password matches the stored password
            if encrypted_old_password != user.Password:
                # Log failed password change attempt
                logging.warning(f"Failed password change attempt for user {userid} at {datetime.utcnow()}")
                return {'status': 'failed', 'message': 'Old password is incorrect'}, 200

            # Encrypt the new password
            encrypted_new_password = encrypt(new_password)

            # Update the user's password
            user.Password = encrypted_new_password

            # Commit the transaction to save the updated password
            db.session.commit()

            # Now insert the change into the ChangePassword_History table
            # Create a new record for ChangePassword_History
            history_entry = ChangePassword_History(
                UserId=userid,
                OldPassword=encrypted_old_password,  # Encrypt old password before saving
                NewPassword=encrypted_new_password,  # Encrypt new password before saving
                Date = datetime.utcnow() + timedelta(hours=5)  # Current time
            )

            # Add the history entry to the session and commit
            db.session.add(history_entry)
            db.session.commit()
            logging.info(f"Password changed successfully for user {userid} at {datetime.utcnow()}. History updated.")

            return {'status': 'success', 'message': 'Password changed successfully'}, 200

        except Exception as ex:
            db.session.rollback()
            logging.error(f"Error: {str(ex)}")
            return {'status': 'error', 'message': f'Error: {str(ex)}'}, 500


class ForgotPasswordResource(Resource):
    def post(self):
        data = request.get_json()

        # Ensure that the 'data' key exists
        forgot_password_data = data.get('data')
        if not forgot_password_data:
            return {'status': 'failed', 'message': 'Data is required'}, 400

        # Validate that the data is a list with exactly one dictionary
        if not isinstance(forgot_password_data, list) or len(forgot_password_data) != 1 or not isinstance(forgot_password_data[0], dict):
            return {'status': 'failed', 'message': 'Data should be a list with exactly one dictionary'}, 400

        # Extract the data for the user
        item = forgot_password_data[0]
        email = item.get('username')

        # Validate presence of the email field
        if not email:
            return {'status': 'error', 'message': 'Email is required'}, 400

        try:
            # Encrypt the email to handle potential stored encryption
            encrypted_email = encrypt(email)

            # Find the user by encrypted email
            user = db.session.query(USERS).filter_by(Username=encrypted_email).first()

            # Check if user exists
            if not user:
                return {'status': 'failed', 'message': 'User not found'}, 404

            email_sent = False
            user_email = None

            # Handle user types
            if user.UserType_Id == 7:  # Student ID
                student_info = db.session.query(StudentInfo).filter_by(UserId=user.User_Id).first()
                user_email = student_info.EduEmail if student_info else None

            elif user.UserType_Id == 3:  # Parent ID
                parent_info = db.session.query(StudentInfo).filter_by(ParentUserId=user.User_Id).first()
                user_email = parent_info.Stu_FatherEmail if parent_info else None

            else:  # Staff or other types
                staff_info = db.session.query(UserCampus).filter_by(UserId=user.User_Id).first()
                if staff_info:
                    staff_email = db.session.query(StaffInfo).filter_by(Staff_ID=staff_info.StaffId).first().S_Email
                    user_email = staff_email if staff_email else None

            if user_email:
                email_sent = self.send_password_email(user_email, user.User_Id)

                if email_sent:
                    self.log_forgot_password_attempt(user.User_Id, "Success", "Email sent successfully")
                    return {'status': 'success', 'message': 'Email sent successfully', 'email': user_email}, 200
                else:
                    self.log_forgot_password_attempt(user.User_Id, "Failed", "Failed to send email")
                    return {'status': 'error', 'failed': 'Failed to send email'}, 500
            else:
                self.log_forgot_password_attempt(user.User_Id, "Failed", "User email not found")
                return {'status': 'failed', 'message': 'Email not found'}, 200

        except Exception as ex:
            db.session.rollback()
            logging.error(f"Error: {str(ex)}")
            return {'status': 'error', 'failed': f'Error: {str(ex)}'}, 500

    def send_password_email(self, email, user_id):
        subject = "ALPHA ERP PASSWORD RESET"
        reset_token = str(uuid.uuid4())  # Generate a unique token
        current_time = datetime.utcnow() + timedelta(hours=5)  # Adjusting for timezone (UTC +5)
        expiration_time = current_time + timedelta(minutes=15)  # Adding 15 minutes to the current time

        # Generate 3 random digits before and after the user_id
        random_prefix = str(random.randint(100, 999))  # 3 random digits before user_id
        random_suffix = str(random.randint(100, 999))  # 3 random digits after user_id
        
        # Combine random numbers with the user_id
        modified_user_id = f"{random_prefix}{user_id}{random_suffix}"

        #Live URL
        reset_url = f"http://erp.alpha.edu.pk:86/ForgotPassword/{modified_user_id}?T={reset_token}&E={expiration_time.isoformat()}"
        # reset_url = f"http://localhost:3033/ForgotPassword/{modified_user_id}?T={reset_token}&E={expiration_time.isoformat()}"

        body = f"Hello,\n\nWe received a request to reset your password. Please click the link below to reset your password:\n\n{reset_url}\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nThe ALPHA ERP Team"

        try:
            # Create the MIMEText email message
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = "noreply@alpha.edu.pk"
            msg['To'] = email

            # Sending the email using smtplib
            with smtplib.SMTP('smtp.office365.com', 587) as smtp:
                smtp.starttls()  # Secure the connection
                smtp.login("noreply@alpha.edu.pk", "Alpha123")  # Use correct credentials
                smtp.send_message(msg)  # Send the email

            return True
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            return False

    def log_forgot_password_attempt(self, user_id, status, message):
        try:
            # Fetch the user from the database
            user = db.session.query(USERS).filter_by(User_Id=user_id).first()
            name = user.Firstname if user else "Unknown"

            # Log entry including UserTypeName from the relationship
            log_entry = ForgettPasswordLogs(
                UserId=user_id,
                UserName=name,
                Usertype=user.user_type.UserTypeName if user and user.user_type else "Unknown",  # Access UserTypeName through the relationship
                RequestDate=datetime.utcnow() + timedelta(hours=5),
                RequestType="ForgotPasswordHRIS",
                Status=status,
                Message=message,
                IpAddress=request.remote_addr,  # Get the user's IP address
                CreatorTerminal=request.user_agent.string if request.user_agent else "Unknown"  # Capture the User-Agent string
            )

            # Optionally, you can log specific parts of the user agent for more detail
            user_agent = request.user_agent.string if request.user_agent else "Unknown"
            browser_info = request.user_agent.browser if request.user_agent else "Unknown"
            platform_info = request.user_agent.platform if request.user_agent else "Unknown"

            # Detailed logging for CreatorTerminal (including browser and platform info)
            log_entry.CreatorTerminal = f"Browser: {browser_info}, Platform: {platform_info}, Full User-Agent: {user_agent}"

            # Add log entry to the session and commit
            db.session.add(log_entry)
            db.session.commit()
            
            logging.info(f"Successfully logged forgot password attempt for UserId: {user_id} at {datetime.utcnow()}")

        except Exception as ex:
            logging.error(f"Error in logging forgot password attempt: {str(ex)}")


class ResetPasswordPostResource(Resource):
    def post(self):
        data = request.get_json()

        # Ensure that the 'data' key exists
        change_password_data = data.get('data')
        if not change_password_data:
            return {'status': 'error', 'message': 'Data is required'}, 400

        # Validate that the data is a list with exactly one dictionary
        if not isinstance(change_password_data, list) or len(change_password_data) != 1 or not isinstance(change_password_data[0], dict):
            return {'status': 'error', 'message': 'Data should be a list with exactly one dictionary'}, 400

        # Extract the data for the user to update
        item = change_password_data[0]
        userid = item.get('userid')
        Token = item.get('token')
        new_password = item.get('Password')

        # Validate presence of necessary fields
        if not userid or not new_password:
            return {'status': 'error', 'message': 'userid and newPassword are required'}, 400

        # Remove the 3 random digits before and after the user_id (assuming the length of the random digits is always 3)
        original_userid = userid[3:-3]  # Remove the first 3 digits and last 3 digits

        try:
            user = USERS.query.filter_by(User_Id=original_userid).first()

            # Check if user exists
            if not user:
                return {'status': 'error', 'message': 'User not found'}, 404

            # Encrypt the new password
            encrypted_new_password = encrypt(new_password)

            # Update the user's password
            user.Password = encrypted_new_password
            logging.info(f"Received UserId: {original_userid}, Token: {Token} at {datetime.utcnow()}")

            Token_entry = ForgotPasswordUsedToken(
                UserId=original_userid,
                Token=Token,
                Type="HRIS",
                Date=datetime.utcnow() + timedelta(hours=5)  # Current time
            )
            logging.info(f"Token_entry created: {Token_entry} at {datetime.utcnow()}")  # Add the history entry to the session and commit
            db.session.add(Token_entry)

            # Commit the transaction to save the updated password
            db.session.commit()

            logging.info(f"Password changed successfully for user {original_userid} at {datetime.utcnow()}")

            return {'status': 'success', 'message': 'Password changed successfully'}, 200

        except Exception as ex:
            db.session.rollback()
            logging.error(f"ErrorReset: {str(ex)}")
            return {'status': 'error', 'message': f'Error: {str(ex)}'}, 500


class StudentSubmissions_JotForms(Resource):
    def post(self):
        if request.is_json:
            data = request.get_json()
            logging.info (f"Parameters: {data}")
        else:
            data = request.form

            # Ensure form_id and API_KEY are provided
            if 'form_id' not in data or 'api_key' not in data or 'userid' not in data:
                return Response('{"error": "form_id, api_key and userid are required"}', status=400, content_type='application/json')

            form_id = data['form_id']
            API_KEY = data['api_key']
            user_id = data['userid']

            # Make request to the JotForm API
            url = f"https://api.jotform.com/form/{form_id}/submissions?apiKey={API_KEY}"
            response = requests.get(url)
            data = json.loads(response.text)
            logging.info(f"Data Received:{data}")

            if not data or "content" not in data:
                logging.info("Invalid request data: Missing 'content' key")
                return {"message": "Invalid request data"}, 400

            # Extract the content array from the JSON
            content = data.get('content', [])
            records_added = 0
            records_skipped = 0

            try:
                for submission in content:
                    jotform_id = submission.get('id')
                    logging.info(f"JotFormId: {jotform_id}")
                    # Skip processing if JotFormId already exists
                    existing_record = db.session.query(StudentSubmissions_JotForm).filter_by(JotFromId=jotform_id).first()
                    if existing_record:
                        logging.info(f"Skipping duplicate record for JotFormId: {jotform_id}")
                        records_skipped += 1
                        continue
                    
                    # Safe extraction of 'answers' dictionary
                    answers = submission.get('answers', {})
                    
                    #logging.info(f"answers: {answers}")
                    
                    private_value = answers.get('52', {}).get('answer', None)
                    Private = True if private_value == "Yes" else False if private_value == "No" else None
                    
                    birthdate_str = answers.get('6', {}).get('answer', {}).get('datetime', None)
                    BirthDate = datetime.strptime(birthdate_str, '%Y-%m-%d %H:%M:%S').date() if birthdate_str else None

                    same_as_mineFather = answers.get('81', {}).get('answer', None)
                    SameAsMineFather = True if same_as_mineFather == "Yes" else False if same_as_mineFather == "No" else None

                    same_as_mineMother = answers.get('82', {}).get('answer', None)
                    SameAsMineMother = True if same_as_mineMother == "Yes" else False if same_as_mineMother == "No" else None

                    sports1_desc = answers.get('71', {}).get('answer', None)
                    Sports1Description = sports1_desc.strip().replace("\n", " ") if sports1_desc else None

                    sports2_desc=answers.get('72', {}).get('answer', None)
                    Sports2Description = sports2_desc.strip().replace("\n", " ") if sports2_desc else None

                    sports3_desc=answers.get('73', {}).get('answer', None)
                    Sports3Description = sports3_desc.strip().replace("\n", " ") if sports3_desc else None
                    
                    student_submission = StudentSubmissions_JotForm(
                        FullName=answers.get('85', {}).get('answer', None),
                        SubmissionDate = submission.get('created_at'),
                        Gender=answers.get('86', {}).get('answer', None),
                        Private=Private,
                        IfPrivate=answers.get('56', {}).get('answer', {}).get('first', None),
                        Email=answers.get('8', {}).get('answer', None),
                        PhoneNumber=answers.get('9', {}).get('prettyFormat', None),
                        BirthDate=BirthDate, 
                        Religion=answers.get('87', {}).get('answer', None),
                        PassportSizePhotograph=answers.get('12', {}).get('answer', [None])[0],
                        NameOfCurrentSchool=answers.get('170', {}).get('answer', None),
                        FathersGuardianFullName=answers.get('88', {}).get('answer', None),
                        FathersAddress = answers.get('83', {}).get('answer', None),
                        SameAsMineFather = SameAsMineFather,
                        FatherEmail = answers.get('17', {}).get('answer', None),
                        FatherOccupation = answers.get('149', {}).get('answer', None),
                        FatherCompanyName = answers.get('150', {}).get('answer', None),
                        FatherPhoneNumber=answers.get('18', {}).get('prettyFormat', None),
                        MothersFullName=answers.get('89', {}).get('answer', None),    
                        MothersAddress = answers.get('84', {}).get('answer', None),       
                        SameAsMineMother = SameAsMineMother,
                        MotherEmail=answers.get('21', {}).get('answer', None),
                        MotherPhoneNumber=answers.get('22', {}).get('prettyFormat', None),
                        MotherOccupation = answers.get('151', {}).get('answer', None),
                        MotherCompanyName = answers.get('152', {}).get('answer', None),
                        ASSubject1=answers.get('26', {}).get('answer', None),
                        ASSubject2=answers.get('28', {}).get('answer', None),
                        ASSubject3=answers.get('30', {}).get('answer', None),
                        ASSubject4=answers.get('32', {}).get('answer', None),
                        ASSubject5=answers.get('34', {}).get('answer', None),
                        SubjectTeacherPreference1=answers.get('27', {}).get('answer', None),
                        SubjectTeacherPreference1_2=answers.get('29', {}).get('answer', None),
                        SubjectTeacherPreference1_3=answers.get('31', {}).get('answer', None),
                        SubjectTeacherPreference1_4=answers.get('33', {}).get('answer', None),
                        SubjectTeacherPreference1_5=answers.get('35', {}).get('answer', None),
                        AboutYourself=answers.get('37', {}).get('answer', None),
                        WhyStudyAtAlpha=answers.get('38', {}).get('answer', None),
                        AimInLife=answers.get('39', {}).get('answer', None),
                        CreatedBy=user_id,  
                        CreatedDate=datetime.utcnow() + timedelta(hours=5),
                        JotFromId=submission.get('id'),
                        Address=answers.get('124', {}).get('answer', None),
                        Nationality=answers.get('137', {}).get('answer', None),
                        CNIC_BFormNumber=answers.get('138', {}).get('answer', None),
                        Country=answers.get('139', {}).get('answer', None),
                        PassportNumber=answers.get('140', {}).get('answer', None),
                        FatherCNICNumber=answers.get('141', {}).get('answer', None),
                        MotherCNICNumber=answers.get('142', {}).get('answer', None),
                        Region=answers.get('116', {}).get('answer', None),
                        Other=answers.get('117', {}).get('answer', None),
                        PakStudies=answers.get('90', {}).get('answer', None),
                        Islamiat=answers.get('91', {}).get('answer', None),
                        UrduSyllabusB=answers.get('93', {}).get('answer', None),
                        Other1=answers.get('94', {}).get('answer', None),
                        Other2=answers.get('95', {}).get('answer', None),
                        Other3=answers.get('97', {}).get('answer', None),
                        OLevelGroup=answers.get('122', {}).get('answer', None),
                        ALevelGroup=answers.get('123', {}).get('answer', None),
                        OLevelSubjects=answers.get('169', {}).get('prettyFormat', None),
                        SubjectTeacherPreference2=answers.get('132', {}).get('answer', None),
                        SubjectTeacherPreference2_2=answers.get('133', {}).get('answer', None),
                        SubjectTeacherPreference2_3=answers.get('134', {}).get('answer', None),
                        SubjectTeacherPreference2_4=answers.get('135', {}).get('answer', None),
                        SubjectTeacherPreference2_5=answers.get('136', {}).get('answer', None),
                        Sports1=answers.get('65', {}).get('answer', None),
                        OtherSport1=answers.get('127', {}).get('answer', None),
                        Sports1Level=answers.get('66', {}).get('answer', None),
                        Sports1Description = Sports1Description,
                        Sports2=answers.get('67', {}).get('answer', None),
                        OtherSport2=answers.get('128', {}).get('answer', None),
                        Sports2Level=answers.get('68', {}).get('answer', None),
                        Sports2Description = Sports2Description,
                        Sports3=answers.get('69', {}).get('answer', None),
                        OtherSport3=answers.get('129', {}).get('answer', None),
                        Sports3Level=answers.get('70', {}).get('answer', None),
                        Sports3Description = Sports3Description,
                        Debates=answers.get('74', {}).get('answer', None),
                        DebatesLevel=answers.get('75', {}).get('answer', None),
                        DebatesDescription=answers.get('76', {}).get('answer', None),
                        OtherDebates = answers.get('77', {}).get('answer', None),
                        OtherDescription = answers.get('78', {}).get('answer', None),
                        ReferenceName1 = answers.get('41', {}).get('answer', {}).get('first', None),
                        ReferenceContactNumber1=answers.get('41', {}).get('answer', {}).get('last', None),
                        ReferenceName2=answers.get('42', {}).get('answer', {}).get('first', None),
                        ReferenceContactNumber2=answers.get('42', {}).get('answer', {}).get('last', None),
                        AlphaID=answers.get('49', {}).get('answer', {}).get('middle', None),
                        Question=answers.get('46', {}).get('answer', None),
                        Inactive=0  # Assuming default inactive status
                    )
                    
                    # Save the student submission to the database
                    db.session.add(student_submission)
                    records_added += 1

                # Commit all valid records at once
                db.session.commit()
                logging.info(f"Submission completed: {records_added} records added, {records_skipped} records skipped.")

                return {"message": "Records Inserted Successfully", "records_added": records_added, "records_skipped(duplicate)":records_skipped}, 200

            except SQLAlchemyError as e:
                db.session.rollback()  # Rollback in case of DB error
                logging.info(f"Database error: {str(e)}")
                return {"message": "Database error occurred", "error": str(e)}, 500

            except Exception as e:
                logging.info(f"Unexpected error: {str(e)}")
                return {"message": "An unexpected error occurred", "error": str(e)}, 500

class User_Signup(Resource):
    def post(self):
        
        try:
        # Get data from the request body
            data = request.get_json()

            firstname = data.get('firstname')
            lastname = data.get('lastname')
            Username = data.get('email')
            password = data.get('password')
            mobile_no = data.get('mobile_no')
            cnic = data.get('cnic')

            # Validate the input fields
            if not firstname or not lastname or not Username or not password or not mobile_no or not cnic:
                return {"error": "All fields are required"}, 400

            # Hash the email and password before storing
            hashed_email = encrypt(Username)
            hashed_password = encrypt(password)
            
            # Check if the user already exists by email or CNIC
            existing_user = USERS.query.filter((USERS.Username == hashed_email) | (USERS.GuardianCNIC == cnic)).first()
            if existing_user:
                return {"error": "Email or CNIC already exists"}, 400

            # Create a new user instance
            new_user = USERS(
                Firstname=firstname,
                Lastname=lastname,
                Username=hashed_email,
                Password=hashed_password,
                EMail = Username,
                UserType_Id = 14,
                MobileNo=mobile_no,
                GuardianCNIC=cnic,
                Status = 1,
                ispasswordchanged = 0,
                CreateDate = datetime.utcnow() + timedelta(hours=5),
                Inactive = 0
            )

            # Add the new user to the session and commit to the database
            db.session.add(new_user)
            db.session.commit()

            # Return a success message
            return {"message": "User signed up successfully!"}, 200


        except IntegrityError as e:
            # Catch SQLAlchemy IntegrityError (for example, a duplicate entry)
            db.session.rollback()  
            return {"error": "Database integrity error: " + str(e)}, 500
        except Exception as e:
            # Catch other unexpected errors
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500