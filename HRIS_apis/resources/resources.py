from flask_restful import Resource, reqparse
from models.models import JobApplicationForm, NewJoinerApproval
from datetime import datetime
from app import db

class JobApplicationFormResource(Resource):
    def get(self, id=None, width=150):
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
            job_application_form = JobApplicationForm.query.get_or_404(id)
            job_application_form = job_application_form.to_dict()
            return {"data": job_application_form, "columns": columns}
        else:
            job_application_forms = JobApplicationForm.query.all()
            
            return {
                "data": [form.to_dict() for form in job_application_forms], 
                "columns":columns
            }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('initial_id', required=True)
        parser.add_argument('first_name', required=True)
        parser.add_argument('last_name', required=True)
        parser.add_argument('father_name', required=True)
        parser.add_argument('cnic', required=True)
        parser.add_argument('passport_number')
        parser.add_argument('dob', required=True)
        parser.add_argument('age', required=True, type=int)
        parser.add_argument('gender', required=True)
        parser.add_argument('cell_phone', required=True)
        parser.add_argument('alternate_number')
        parser.add_argument('email', required=True)
        parser.add_argument('residence', required=True)
        parser.add_argument('education_level', required=True)
        parser.add_argument('education_level_others')
        parser.add_argument('degree', required=True)
        parser.add_argument('specialization', required=True)
        parser.add_argument('institute', required=True)
        parser.add_argument('fresh', type=bool)
        parser.add_argument('experienced', type=bool)
        parser.add_argument('total_years_of_experience')
        parser.add_argument('name_of_last_employer')
        parser.add_argument('employment_duration_from')
        parser.add_argument('employment_duration_to')
        parser.add_argument('designation')
        parser.add_argument('reason_for_leaving')
        parser.add_argument('last_drawn_gross_salary')
        parser.add_argument('benefits_if_any')
        parser.add_argument('preferred_campus')
        parser.add_argument('preferred_location')
        parser.add_argument('preferred_job_type')
        parser.add_argument('section')
        parser.add_argument('subject')
        parser.add_argument('expected_salary', required=True)
        parser.add_argument('cv_path', required=True)
        parser.add_argument('coverLetter_Path')
        parser.add_argument('status', type=bool)

        args = parser.parse_args()

        try:
            # Validate inputs
            if not JobApplicationForm.validate_phone_number(args['cell_phone']):
                raise ValueError("Invalid phone number format.")
            if not JobApplicationForm.validate_cnic(args['cnic']):
                raise ValueError("Invalid CNIC format.")
            if args['email'] and not JobApplicationForm.validate_email(args['email']):
                raise ValueError("Invalid email format.")
            if args['passport_number'] and not JobApplicationForm.validate_passport_number(args['passport_number']):
                raise ValueError("Invalid passport number format.")

            employment_duration_from = datetime.strptime(args['employment_duration_from'], '%Y-%m-%d') if args['employment_duration_from'] else None
            employment_duration_to = datetime.strptime(args['employment_duration_to'], '%Y-%m-%d') if args['employment_duration_to'] else None

            job_application_form = JobApplicationForm(
                initial_id=args['initial_id'],
                first_name=args['first_name'],
                last_name=args['last_name'],
                father_name=args['father_name'],
                cnic=args['cnic'],
                passport_number=args['passport_number'],
                dob=datetime.strptime(args['dob'], '%Y-%m-%d'),
                age=args['age'],
                gender=args['gender'],
                cell_phone=args['cell_phone'],
                alternate_number=args['alternate_number'],
                email=args['email'],
                residence=args['residence'],
                education_level=args['education_level'],
                education_level_others=args['education_level_others'],
                degree=args['degree'],
                specialization=args['specialization'],
                institute=args['institute'],
                fresh=args['fresh'],
                experienced=args['experienced'],
                total_years_of_experience=args['total_years_of_experience'],
                name_of_last_employer=args['name_of_last_employer'],
                employment_duration_from=employment_duration_from,
                employment_duration_to=employment_duration_to,
                designation=args['designation'],
                reason_for_leaving=args['reason_for_leaving'],
                last_drawn_gross_salary=args['last_drawn_gross_salary'],
                benefits_if_any=args['benefits_if_any'],
                preferred_campus=args['preferred_campus'],
                preferred_location=args['preferred_location'],
                preferred_job_type=args['preferred_job_type'],
                section=args['section'],
                subject=args['subject'],
                expected_salary=args['expected_salary'],
                cv_path=args['cv_path'],
                coverLetter_Path=args['coverLetter_Path'],
                status=args['status']
            )

            db.session.add(job_application_form)
            db.session.commit()

            return {'message': 'Job application form created successfully'}, 201
        except ValueError as e:
            return {'error': 'Validation Error', 'message': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('initial_id')
        parser.add_argument('first_name')
        parser.add_argument('last_name')
        parser.add_argument('father_name')
        parser.add_argument('cnic')
        parser.add_argument('passport_number')
        parser.add_argument('dob')
        parser.add_argument('age', type=int)
        parser.add_argument('gender')
        parser.add_argument('cell_phone')
        parser.add_argument('alternate_number')
        parser.add_argument('email')
        parser.add_argument('residence')
        parser.add_argument('education_level')
        parser.add_argument('education_level_others')
        parser.add_argument('degree')
        parser.add_argument('specialization')
        parser.add_argument('institute')
        parser.add_argument('fresh', type=bool)
        parser.add_argument('experienced', type=bool)
        parser.add_argument('total_years_of_experience')
        parser.add_argument('name_of_last_employer')
        parser.add_argument('employment_duration_from')
        parser.add_argument('employment_duration_to')
        parser.add_argument('designation')
        parser.add_argument('reason_for_leaving')
        parser.add_argument('last_drawn_gross_salary')
        parser.add_argument('benefits_if_any')
        parser.add_argument('preferred_campus')
        parser.add_argument('preferred_location')
        parser.add_argument('preferred_job_type')
        parser.add_argument('section')
        parser.add_argument('subject')
        parser.add_argument('expected_salary')
        parser.add_argument('cv_path')
        parser.add_argument('coverLetter_Path')
        parser.add_argument('status', type=bool)

        args = parser.parse_args()

        try:
            job_application_form = JobApplicationForm.query.get_or_404(id)

            if args['cell_phone'] and not JobApplicationForm.validate_phone_number(args['cell_phone']):
                raise ValueError("Invalid phone number format.")
            if args['cnic'] and not JobApplicationForm.validate_cnic(args['cnic']):
                raise ValueError("Invalid CNIC format.")
            if args['email'] and not JobApplicationForm.validate_email(args['email']):
                raise ValueError("Invalid email format.")
            if args['passport_number'] and not JobApplicationForm.validate_passport_number(args['passport_number']):
                raise ValueError("Invalid passport number format.")

            employment_duration_from = datetime.strptime(args['employment_duration_from'], '%Y-%m-%d') if args['employment_duration_from'] else None
            employment_duration_to = datetime.strptime(args['employment_duration_to'], '%Y-%m-%d') if args['employment_duration_to'] else None

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
            job_application_form = JobApplicationForm.query.get_or_404(id)
            db.session.delete(job_application_form)
            db.session.commit()
            return {'message': 'Job application form deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

class NewJoinerApprovalResource(Resource):
    def get(self, id=None, width=150):
        columns = [
        {"fields": "newJoinerApproval_StaffId", "headerName": "Staff ID", "width": width},
        {"fields": "newJoinerApproval_Salary", "headerName": "Salary", "width": width},
        {"fields": "newJoinerApproval_HiringApprovedBy", "headerName": "Hiring Approved By", "width": width},
        {"fields": "newJoinerApproval_Remarks", "headerName": "Remarks", "width": width},
        {"fields": "newJoinerApproval_FileVerified", "headerName": "File Verified", "width": width},
        {"fields": "newJoinerApproval_EmpDetailsVerified", "headerName": "Employee Details Verified", "width": width},
        {"fields": "newJoinerApproval_AddToPayrollMonth", "headerName": "Add to Payroll Month", "width": width},
    ]
        if id:
            new_joiner_approval = NewJoinerApproval.query.get_or_404(id)
            new_joiner_approval = new_joiner_approval.to_dict()
            return {"data": new_joiner_approval, "columns": columns}
        else:
            new_joiner_approvals = NewJoinerApproval.query.all()
            return {"data": [approval.to_dict() for approval in new_joiner_approvals], "columns": columns}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('newJoinerApproval_StaffId', required=True, type=int)
        parser.add_argument('newJoinerApproval_Salary', required=True, type=float)
        parser.add_argument('newJoinerApproval_HiringApprovedBy', required=True, type=int)
        parser.add_argument('newJoinerApproval_Remarks')
        parser.add_argument('newJoinerApproval_FileVerified', required=True, type=bool)
        parser.add_argument('newJoinerApproval_EmpDetailsVerified', required=True, type=bool)
        parser.add_argument('newJoinerApproval_AddToPayrollMonth', required=True)
        parser.add_argument('createdBy', required=True, type=int)

        args = parser.parse_args()

        try:
            new_joiner_approval = NewJoinerApproval(
                newJoinerApproval_StaffId=args['newJoinerApproval_StaffId'],
                newJoinerApproval_Salary=args['newJoinerApproval_Salary'],
                newJoinerApproval_HiringApprovedBy=args['newJoinerApproval_HiringApprovedBy'],
                newJoinerApproval_Remarks=args['newJoinerApproval_Remarks'],
                newJoinerApproval_FileVerified=args['newJoinerApproval_FileVerified'],
                newJoinerApproval_EmpDetailsVerified=args['newJoinerApproval_EmpDetailsVerified'],
                newJoinerApproval_AddToPayrollMonth=args['newJoinerApproval_AddToPayrollMonth'],
                createdBy=args['createdBy']
            )

            db.session.add(new_joiner_approval)
            db.session.commit()

            return {'message': 'New joiner approval created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('newJoinerApproval_StaffId', type=int)
        parser.add_argument('newJoinerApproval_Salary', type=float)
        parser.add_argument('newJoinerApproval_HiringApprovedBy', type=int)
        parser.add_argument('newJoinerApproval_Remarks')
        parser.add_argument('newJoinerApproval_FileVerified', type=bool)
        parser.add_argument('newJoinerApproval_EmpDetailsVerified', type=bool)
        parser.add_argument('newJoinerApproval_AddToPayrollMonth')
        parser.add_argument('updatedBy', type=int)
        parser.add_argument('inActive', type=bool)

        args = parser.parse_args()

        try:
            new_joiner_approval = NewJoinerApproval.query.get_or_404(id)

            for key, value in args.items():
                if value is not None:
                    setattr(new_joiner_approval, key, value)

            new_joiner_approval.updatedBy = args['updatedBy']
            new_joiner_approval.updatedDate = datetime.utcnow()

            db.session.commit()
            return {'message': 'New joiner approval updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

    def delete(self, id):
        try:
            new_joiner_approval = NewJoinerApproval.query.get_or_404(id)
            db.session.delete(new_joiner_approval)
            db.session.commit()
            return {'message': 'New joiner approval deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500
