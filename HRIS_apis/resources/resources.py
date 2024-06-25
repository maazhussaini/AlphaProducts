from flask_restful import Resource, reqparse, abort
from models.models import JobApplicationForm, NewJoinerApproval, InterviewSchedules, DeductionHead, OneTimeDeduction, ScheduledDeduction, IAR, IAR_Remarks, IAR_Types, EmailTypes, EmailStorageSystem, AvailableJobs
from datetime import datetime
from app import db
from flask import jsonify, request
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

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
                job_application_form = JobApplicationForm.query.get_or_404(id)
                
                return {
                    "data": [job_application_form.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            else:
                query = JobApplicationForm.query.order_by(JobApplicationForm.id)
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
            if JobApplicationForm.validate_phone_number(args['cell_phone']):
                raise ValueError("Invalid phone number format.")
            if JobApplicationForm.validate_cnic(args['cnic']):
                raise ValueError("Invalid CNIC format.")
            if args['email'] and JobApplicationForm.validate_email(args['email']):
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
                return {
                    "data": [new_joiner_approval.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            else:
                
                query = NewJoinerApproval.query.order_by(NewJoinerApproval.newJoinerApproval_Id)
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
                {"field":'interview_type_id', "headerName": "Interview Type ID", "width": width},
                {"field":'date', "headerName": "Date", "width": width},
                {"field":'time', "headerName": "Time", "width": width},
                {"field":'venue', "headerName": "Venue", "width": width},
                {"field":'job_application_form_id', "headerName": "Job Application Form Id", "width": width},
                {"field":'interview_conductor_id', "headerName": "Interview Conductor Id", "width": width},
                {"field":'demo_topic', "headerName": "Demo Topic", "width": width},
                {"field":'position', "headerName": "Position", "width": width},
                {"field":'location', "headerName": "Location", "width": width},
                {"field":'created_by', "headerName": "Created By", "width": width},
                {"field":'create_date', "headerName": "Created Date", "width": width},
                {"field":'campus_id', "headerName": "Campus Id", "width": width}
            ]
            
            if id is None:
                
                query = InterviewSchedules.query.order_by(InterviewSchedules.id)
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
        parser.add_argument('interviewTypeId', type=int, required=True, help="Interview type ID is required")
        parser.add_argument('date', type=str, required=False)
        parser.add_argument('time', type=str, required=False)
        parser.add_argument('venue', type=str, required=False)
        parser.add_argument('jobApplicationFormId', type=int, required=False)
        parser.add_argument('interviewConductorId', type=str, required=False)
        parser.add_argument('demoTopic', type=str, required=False)
        parser.add_argument('position', type=str, required=False)
        parser.add_argument('location', type=str, required=False)
        parser.add_argument('createdBy', type=int, required=False)
        parser.add_argument('createDate', type=str, required=False)
        parser.add_argument('campusId', type=int, required=False)
        args = parser.parse_args()

        try:
            new_schedule = InterviewSchedules(
                interviewTypeId=args['interviewTypeId'],
                date=datetime.strptime(args['date'], '%Y-%m-%d') if args['date'] else None,
                time=datetime.strptime(args['time'], '%H:%M:%S').time() if args['time'] else None,
                venue=args['venue'],
                jobApplicationFormId=args['jobApplicationFormId'],
                interviewConductorId=args['interviewConductorId'],
                demoTopic=args['demoTopic'],
                position=args['position'],
                location=args['location'],
                createdBy=args['createdBy'],
                createDate=datetime.strptime(args['createDate'], '%Y-%m-%d %H:%M:%S') if args['createDate'] else datetime.utcnow(),
                campusId=args['campusId']
            )
            db.session.add(new_schedule)
            db.session.commit()
            return {"message": "Interview schedule created", "id": new_schedule.id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating interview schedule: {str(e)}")
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('interviewTypeId', type=int, required=False)
        parser.add_argument('date', type=str, required=False)
        parser.add_argument('time', type=str, required=False)
        parser.add_argument('venue', type=str, required=False)
        parser.add_argument('jobApplicationFormId', type=int, required=False)
        parser.add_argument('interviewConductorId', type=str, required=False)
        parser.add_argument('demoTopic', type=str, required=False)
        parser.add_argument('position', type=str, required=False)
        parser.add_argument('location', type=str, required=False)
        parser.add_argument('createdBy', type=int, required=False)
        parser.add_argument('createDate', type=str, required=False)
        parser.add_argument('campusId', type=int, required=False)
        args = parser.parse_args()

        schedule = InterviewSchedules.query.get(id)
        if schedule is None:
            abort(404, message=f"Interview schedule {id} doesn't exist")

        try:
            if args['interviewTypeId'] is not None:
                schedule.interviewTypeId = args['interviewTypeId']
            if args['date']:
                schedule.date = datetime.strptime(args['date'], '%Y-%m-%d')
            if args['time']:
                schedule.time = datetime.strptime(args['time'], '%H:%M:%S').time()
            if args['venue']:
                schedule.venue = args['venue']
            if args['jobApplicationFormId'] is not None:
                schedule.jobApplicationFormId = args['jobApplicationFormId']
            if args['interviewConductorId']:
                schedule.interviewConductorId = args['interviewConductorId']
            if args['demoTopic']:
                schedule.demoTopic = args['demoTopic']
            if args['position']:
                schedule.position = args['position']
            if args['location']:
                schedule.location = args['location']
            if args['createdBy'] is not None:
                schedule.createdBy = args['createdBy']
            if args['createDate']:
                schedule.createDate = datetime.strptime(args['createDate'], '%Y-%m-%d %H:%M:%S')
            if args['campusId'] is not None:
                schedule.campusId = args['campusId']
            
            db.session.commit()
            return {"message": "Interview schedule updated", "id": schedule.id}, 200
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
                {"field": "deductionHead_Id", "headerName": "Deduction Head Id", "width": width},
                {"field": "deductionHead_Name", "headerName": "Deduction Head Name", "width": width}
            ]
            
            if id is None:
                query = DeductionHead.query.order_by(DeductionHead.deductionHead_Id)
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
                deductionHeads = DeductionHead.query.all()
                
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
        parser.add_argument('deductionHead_Name', type=str, required=True, help="Deduction head name is required")
        args = parser.parse_args()

        try:
            new_head = DeductionHead(deductionHead_Name=args['deductionHead_Name'])
            db.session.add(new_head)
            db.session.commit()
            return {"message": "Deduction head created", "id": new_head.deductionHead_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating deduction head: {str(e)}")
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('deductionHead_Name', type=str, required=True, help="Deduction head name is required")
        args = parser.parse_args()

        head = DeductionHead.query.get(id)
        if head is None:
            abort(404, message=f"DeductionHead {id} doesn't exist")

        try:
            head.deductionHead_Name = args['deductionHead_Name']
            db.session.commit()
            return {"message": "Deduction head updated", "id": head.deductionHead_Id}, 200
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
                {"field":"oneTimeDeduction_Id", "headername": "Id", "width": width},
                {"field":"oneTimeDeduction_StaffId", "headername": "Staff Id", "width": width},
                {"field":"oneTimeDeduction_DeductionHeadId", "headername": "Deduction Head Id", "width": width},
                {"field":"oneTimeDeduction_Amount", "headername": "Amount", "width": width},
                {"field":"oneTimeDeduction_DeductionMonth", "headername": "Deduction Month", "width": width},
                {"field":"oneTimeDeduction_ApprovedBy", "headername": "Approved By", "width": width},
                {"field":"creatorId", "headername": "Creator Id", "width": width},
                {"field":"createDate", "headername": "Created Date", "width": width},
                {"field":"updatorId", "headername": "Updator Id", "width": width},
                {"field":"updateDate", "headername": "Updated Date", "width": width},
                {"field":"inActive", "headername": "In active", "width": width}
            ]

            if id is None:
                
                query = OneTimeDeduction.query.order_by(OneTimeDeduction.id)
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
        parser.add_argument('oneTimeDeduction_StaffId', type=int, required=True, help="Staff ID is required")
        parser.add_argument('oneTimeDeduction_DeductionHeadId', type=int, required=True, help="Deduction head ID is required")
        parser.add_argument('oneTimeDeduction_Amount', type=float, required=True, help="Amount is required")
        parser.add_argument('oneTimeDeduction_DeductionMonth', type=str, required=True, help="Deduction month is required")
        parser.add_argument('oneTimeDeduction_ApprovedBy', type=int, required=True, help="Approved by is required")
        parser.add_argument('creatorId', type=int, required=True, help="Creator ID is required")
        parser.add_argument('createDate', type=str, required=True, help="Create date is required")
        parser.add_argument('updatorId', type=int, required=False)
        parser.add_argument('updateDate', type=str, required=False)
        parser.add_argument('inActive', type=bool, required=True, help="Inactive status is required")
        args = parser.parse_args()

        try:
            new_deduction = OneTimeDeduction(
                oneTimeDeduction_StaffId=args['oneTimeDeduction_StaffId'],
                oneTimeDeduction_DeductionHeadId=args['oneTimeDeduction_DeductionHeadId'],
                oneTimeDeduction_Amount=args['oneTimeDeduction_Amount'],
                oneTimeDeduction_DeductionMonth=args['oneTimeDeduction_DeductionMonth'],
                oneTimeDeduction_ApprovedBy=args['oneTimeDeduction_ApprovedBy'],
                creatorId=args['creatorId'],
                createDate=datetime.strptime(args['createDate'], '%Y-%m-%d %H:%M:%S'),
                updatorId=args.get('updatorId'),
                updateDate=datetime.strptime(args['updateDate'], '%Y-%m-%d %H:%M:%S') if args['updateDate'] else None,
                inActive=args['inActive']
            )
            db.session.add(new_deduction)
            db.session.commit()
            return {"message": "One-time deduction created", "id": new_deduction.oneTimeDeduction_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating one-time deduction: {str(e)}")
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('oneTimeDeduction_StaffId', type=int, required=False)
        parser.add_argument('oneTimeDeduction_DeductionHeadId', type=int, required=False)
        parser.add_argument('oneTimeDeduction_Amount', type=float, required=False)
        parser.add_argument('oneTimeDeduction_DeductionMonth', type=str, required=False)
        parser.add_argument('oneTimeDeduction_ApprovedBy', type=int, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('createDate', type=str, required=False)
        parser.add_argument('updatorId', type=int, required=False)
        parser.add_argument('updateDate', type=str, required=False)
        parser.add_argument('inActive', type=bool, required=False)
        args = parser.parse_args()

        deduction = OneTimeDeduction.query.get(id)
        if deduction is None:
            abort(404, message=f"OneTimeDeduction {id} doesn't exist")

        try:
            if args['oneTimeDeduction_StaffId'] is not None:
                deduction.oneTimeDeduction_StaffId = args['oneTimeDeduction_StaffId']
            if args['oneTimeDeduction_DeductionHeadId'] is not None:
                deduction.oneTimeDeduction_DeductionHeadId = args['oneTimeDeduction_DeductionHeadId']
            if args['oneTimeDeduction_Amount'] is not None:
                deduction.oneTimeDeduction_Amount = args['oneTimeDeduction_Amount']
            if args['oneTimeDeduction_DeductionMonth']:
                deduction.oneTimeDeduction_DeductionMonth = args['oneTimeDeduction_DeductionMonth']
            if args['oneTimeDeduction_ApprovedBy'] is not None:
                deduction.oneTimeDeduction_ApprovedBy = args['oneTimeDeduction_ApprovedBy']
            if args['creatorId'] is not None:
                deduction.creatorId = args['creatorId']
            if args['createDate']:
                deduction.createDate = datetime.strptime(args['createDate'], '%Y-%m-%d %H:%M:%S')
            if args['updatorId'] is not None:
                deduction.updatorId = args['updatorId']
            if args['updateDate']:
                deduction.updateDate = datetime.strptime(args['updateDate'], '%Y-%m-%d %H:%M:%S')
            if args['inActive'] is not None:
                deduction.inActive = args['inActive']

            db.session.commit()
            return {"message": "One-time deduction updated", "id": deduction.oneTimeDeduction_Id}, 200
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
                {"field":"scheduledDeduction_Id", "headerName": "Id", "width": width},
                {"field":"scheduledDeduction_StaffId", "headerName": "Staff Id", "width": width},
                {"field":"scheduledDeduction_DeductionHeadId", "headerName": "Deduction head Id", "width": width},
                {"field":"scheduledDeduction_AmountPerMonth", "headerName": "Amount Per Month", "width": width},
                {"field":"scheduledDeduction_StartDate", "headerName": "Start Date", "width": width},
                {"field":"scheduledDeduction_EndDate", "headerName": "End Date", "width": width},
                {"field":"scheduledDeduction_ApprovedBy", "headerName": "Approved By", "width": width},
                {"field":"creatorId", "headerName": "Creator Id", "width": width},
                {"field":"createDate", "headerName": "Created Date", "width": width},
                {"field":"updatorId", "headerName": "Updator Id", "width": width},
                {"field":"updateDate", "headerName": "Updated Date", "width": width},
                {"field":"inActive", "headerName": "In Active", "width": width}
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

                query = ScheduledDeduction.query.order_by(ScheduledDeduction.scheduledDeduction_Id)
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
        parser.add_argument('scheduledDeduction_StaffId', type=int, required=True, help="Staff ID is required")
        parser.add_argument('scheduledDeduction_DeductionHeadId', type=int, required=True, help="Deduction Head ID is required")
        parser.add_argument('scheduledDeduction_AmountPerMonth', type=float, required=True, help="Amount Per Month is required")
        parser.add_argument('scheduledDeduction_StartDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help="Start Date is required and must be in ISO format")
        parser.add_argument('scheduledDeduction_EndDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help="End Date is required and must be in ISO format")
        parser.add_argument('scheduledDeduction_ApprovedBy', type=int, required=True, help="Approved By is required")
        parser.add_argument('creatorId', type=int, required=True, help="Creator ID is required")
        parser.add_argument('updatorId', type=int, required=False)
        parser.add_argument('updateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('inActive', type=bool, required=True, help="Inactive status is required")
        args = parser.parse_args()

        new_deduction = ScheduledDeduction(
            scheduledDeduction_StaffId=args['scheduledDeduction_StaffId'],
            scheduledDeduction_DeductionHeadId=args['scheduledDeduction_DeductionHeadId'],
            scheduledDeduction_AmountPerMonth=args['scheduledDeduction_AmountPerMonth'],
            scheduledDeduction_StartDate=args['scheduledDeduction_StartDate'],
            scheduledDeduction_EndDate=args['scheduledDeduction_EndDate'],
            scheduledDeduction_ApprovedBy=args['scheduledDeduction_ApprovedBy'],
            creatorId=args['creatorId'],
            updatorId=args.get('updatorId'),
            updateDate=args.get('updateDate'),
            inActive=args['inActive']
        )

        try:
            db.session.add(new_deduction)
            db.session.commit()
            return {"message": "Scheduled deduction created", "id": new_deduction.scheduledDeduction_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating scheduled deduction: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('scheduledDeduction_StaffId', type=int, required=False)
        parser.add_argument('scheduledDeduction_DeductionHeadId', type=int, required=False)
        parser.add_argument('scheduledDeduction_AmountPerMonth', type=float, required=False)
        parser.add_argument('scheduledDeduction_StartDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('scheduledDeduction_EndDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('scheduledDeduction_ApprovedBy', type=int, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('updatorId', type=int, required=False)
        parser.add_argument('updateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('inActive', type=bool, required=False)
        args = parser.parse_args()

        deduction = ScheduledDeduction.query.get(id)
        if not deduction:
            abort(404, message=f"Scheduled Deduction {id} does not exist")

        try:
            if args.get('scheduledDeduction_StaffId') is not None:
                deduction.scheduledDeduction_StaffId = args['scheduledDeduction_StaffId']
            if args.get('scheduledDeduction_DeductionHeadId') is not None:
                deduction.scheduledDeduction_DeductionHeadId = args['scheduledDeduction_DeductionHeadId']
            if args.get('scheduledDeduction_AmountPerMonth') is not None:
                deduction.scheduledDeduction_AmountPerMonth = args['scheduledDeduction_AmountPerMonth']
            if args.get('scheduledDeduction_StartDate') is not None:
                deduction.scheduledDeduction_StartDate = args['scheduledDeduction_StartDate']
            if args.get('scheduledDeduction_EndDate') is not None:
                deduction.scheduledDeduction_EndDate = args['scheduledDeduction_EndDate']
            if args.get('scheduledDeduction_ApprovedBy') is not None:
                deduction.scheduledDeduction_ApprovedBy = args['scheduledDeduction_ApprovedBy']
            if args.get('creatorId') is not None:
                deduction.creatorId = args['creatorId']
            if args.get('updatorId') is not None:
                deduction.updatorId = args['updatorId']
            if args.get('updateDate') is not None:
                deduction.updateDate = args['updateDate']
            if args.get('inActive') is not None:
                deduction.inActive = args['inActive']

            db.session.commit()
            return {"message": "Scheduled deduction updated", "id": deduction.scheduledDeduction_Id}, 200
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
                query = IAR.query.order_by(IAR.id)
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
        parser.add_argument('form_Id', type=int, required=True, help="Form ID is required")
        parser.add_argument('IAR_Type_Id', type=int, required=True, help="IAR Type ID is required")
        parser.add_argument('status_Check', type=bool, required=True, help="Status Check is required")
        parser.add_argument('remarks', type=str, required=True, help="Remarks are required")
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('createdDate', type=str, required=False)
        args = parser.parse_args()

        try:
            new_iar = IAR(
                form_Id=args['form_Id'],
                IAR_Type_Id=args['IAR_Type_Id'],
                status_Check=args['status_Check'],
                remarks=args['remarks'],
                creatorId=args.get('creatorId'),
                createdDate=datetime.strptime(args['createdDate'], '%Y-%m-%d %H:%M:%S') if args['createdDate'] else None
            )
            db.session.add(new_iar)
            db.session.commit()
            return {"message": "IAR created", "id": new_iar.id}, 200
        except ValueError as ve:
            db.session.rollback()
            return {"error": f"Value error: {str(ve)}"}, 400
        except TypeError as te:
            db.session.rollback()
            return jsonify({"error": f"Type error: {str(te)}"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error creating IAR: {str(e)}"}), 400
        
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('form_Id', type=int, required=False)
        parser.add_argument('IAR_Type_Id', type=int, required=False)
        parser.add_argument('status_Check', type=bool, required=False)
        parser.add_argument('remarks', type=str, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('createdDate', type=str, required=False)
        args = parser.parse_args()

        iar = IAR.query.get(id)
        if iar is None:
            abort(404, message=f"IAR {id} doesn't exist")

        try:
            if args['form_Id'] is not None:
                iar.form_Id = args['form_Id']
            if args['IAR_Type_Id'] is not None:
                iar.IAR_Type_Id = args['IAR_Type_Id']
            if args['status_Check'] is not None:
                iar.status_Check = args['status_Check']
            if args['remarks'] is not None:
                iar.remarks = args['remarks']
            if args['creatorId'] is not None:
                iar.creatorId = args['creatorId']
            if args['createdDate']:
                iar.createdDate = datetime.strptime(args['createdDate'], '%Y-%m-%d %H:%M:%S')

            db.session.commit()
            return {"message": "IAR updated", "id": iar.id}, 200
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
        parser.add_argument('remarks', type=str, required=False)
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('createDate', type=str, required=False)
        args = parser.parse_args()

        try:
            new_remark = IAR_Remarks(
                IAR_Id=args['IAR_Id'],
                remarks=args['remarks'],
                status=args['status'],
                creatorId=args.get('creatorId'),
                createDate=datetime.strptime(args['createDate'], '%Y-%m-%d %H:%M:%S') if args['createDate'] else None
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
        parser.add_argument('remarks', type=str, required=False)
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('createDate', type=str, required=False)
        args = parser.parse_args()

        remark = IAR_Remarks.query.get(id)
        if remark is None:
            abort(404, message=f"IAR_Remarks {id} doesn't exist")

        try:
            if args['IAR_Id'] is not None:
                remark.iar_id = args['iar_id']
            if args['remarks'] is not None:
                remark.remarks = args['remarks']
            if args['status'] is not None:
                remark.status = args['status']
            if args['creatorId'] is not None:
                remark.creator_id = args['creator_id']
            if args['createDate']:
                remark.create_date = datetime.strptime(args['create_date'], '%Y-%m-%d %H:%M:%S')

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
                query = IAR_Types.query.order_by(IAR_Types.id)
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
        parser.add_argument('name', type=str, required=True, help="Name is required")
        args = parser.parse_args()

        try:
            new_type = IAR_Types(name=args['name'])
            db.session.add(new_type)
            db.session.commit()
            return jsonify({"message": "IAR_Types created", "id": new_type.id}), 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating IAR_Types: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False)
        args = parser.parse_args()

        iar_type = IAR_Types.query.get(id)
        if iar_type is None:
            abort(404, message=f"IAR_Types {id} doesn't exist")

        try:
            if args['name'] is not None:
                iar_type.name = args['name']

            db.session.commit()
            return jsonify({"message": "IAR_Types updated", "id": iar_type.id}), 200
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
                query = EmailTypes.query.order_by(EmailTypes.id)
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
        parser.add_argument('name', type=str, required=False)
        args = parser.parse_args()

        try:
            new_email_type = EmailTypes(name=args['name'])
            db.session.add(new_email_type)
            db.session.commit()
            return {"message": "EmailTypes created", "id": new_email_type.id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating EmailTypes: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False)
        args = parser.parse_args()

        email_type = EmailTypes.query.get(id)
        if email_type is None:
            abort(404, message=f"EmailTypes {id} doesn't exist")

        try:
            if args['name'] is not None:
                email_type.name = args['name']
            db.session.commit()
            return {"message": "EmailTypes updated", "id": email_type.id}, 200
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
                {"field":"email_Id", "headerName": "", "width": width},
                {"field":"email_Title", "headerName": "", "width": width},
                {"field":"email_Subject", "headerName": "", "width": width},
                {"field":"email_Body", "headerName": "", "width": width},
                {"field":"status", "headerName": "", "width": width},
                {"field":"creatorId", "headerName": "", "width": width},
                {"field":"createdDate", "headerName": "", "width": width},
                {"field":"updatorId", "headerName": "", "width": width},
                {"field":"updatedDate", "headerName": "", "width": width},
                {"field":"emailType", "headerName": "", "width": width}
            ]
            if id is None:
                
                query = EmailStorageSystem.query.order_by(EmailStorageSystem.email_Id)
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
        parser.add_argument('email_Title', type=str, required=False)
        parser.add_argument('email_Subject', type=str, required=False)
        parser.add_argument('email_Body', type=str, required=False)
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('createdDate', type=str, required=False)
        parser.add_argument('updatorId', type=int, required=False)
        parser.add_argument('updatedDate', type=str, required=False)
        parser.add_argument('emailType', type=int, required=False)
        args = parser.parse_args()

        try:
            new_email = EmailStorageSystem(
                email_Title=args['email_Title'],
                email_Subject=args['email_Subject'],
                email_Body=args['email_Body'],
                status=args['status'],
                creatorId=args.get('creatorId'),
                createdDate=datetime.strptime(args['createdDate'], '%Y-%m-%d %H:%M:%S') if args['createdDate'] else None,
                updatorId=args.get('updatorId'),
                updatedDate=datetime.strptime(args['updatedDate'], '%Y-%m-%d %H:%M:%S') if args['updatedDate'] else None,
                emailType=args.get('emailType')
            )
            db.session.add(new_email)
            db.session.commit()
            return {"message": "EmailStorageSystem created", "Email_Id": new_email.email_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating EmailStorageSystem: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('email_Title', type=str, required=False)
        parser.add_argument('email_Subject', type=str, required=False)
        parser.add_argument('email_Body', type=str, required=False)
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('createdDate', type=str, required=False)
        parser.add_argument('updatorId', type=int, required=False)
        parser.add_argument('updatedDate', type=str, required=False)
        parser.add_argument('emailType', type=int, required=False)
        args = parser.parse_args()

        email = EmailStorageSystem.query.get(id)
        if email is None:
            abort(404, message=f"EmailStorageSystem {id} doesn't exist")

        try:
            if args['email_Title'] is not None:
                email.email_Title = args['email_Title']
            if args['email_Subject'] is not None:
                email.email_Subject = args['email_Subject']
            if args['email_Body'] is not None:
                email.email_Body = args['email_Body']
            if args['status'] is not None:
                email.status = args['status']
            if args['creatorId'] is not None:
                email.creatorId = args['creatorId']
            if args['createdDate']:
                email.createdDate = datetime.strptime(args['createdDate'], '%Y-%m-%d %H:%M:%S')
            if args['updatorId'] is not None:
                email.updatorId = args['updatorId']
            if args['updatedDate']:
                email.updatedDate = datetime.strptime(args['updatedDate'], '%Y-%m-%d %H:%M:%S')
            if args['emailType'] is not None:
                email.emailType = args['emailType']
            db.session.commit()
            return {"message": "EmailStorageSystem updated", "Email_Id": email.email_Id}, 200
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
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
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
        parser.add_argument('createdDate', type=str, required=False)
        parser.add_argument('updatorId', type=int, required=False)
        parser.add_argument('updatedDate', type=str, required=False)
        args = parser.parse_args()

        try:
            new_job = AvailableJobs(
                job_Title=args['job_Title'],
                job_Level=args['job_Level'],
                job_PostedBy=args.get('job_PostedBy'),
                job_Status=args.get('job_Status'),
                creatorId=args.get('creatorId'),
                createdDate=datetime.strptime(args['createdDate'], '%Y-%m-%d %H:%M:%S') if args['createdDate'] else None,
                updatorId=args.get('updatorId'),
                updatedDate=datetime.strptime(args['updatedDate'], '%Y-%m-%d %H:%M:%S') if args['updatedDate'] else None
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
            if args['updatedDate']:
                job.updatedDate = datetime.strptime(args['updatedDate'], '%Y-%m-%d %H:%M:%S')
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

