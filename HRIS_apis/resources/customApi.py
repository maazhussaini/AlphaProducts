from flask_restful import Resource, reqparse, abort
from app import db
from flask import jsonify, request
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import and_
from models.models import *
import pyodbc
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import os
import logging
from decimal import Decimal
import pandas as pd
from datetime import datetime
from werkzeug.datastructures import FileStorage


# Custom function to handle both Decimal and Timestamp objects
def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    elif isinstance(obj, (pd.Timestamp, datetime)):  # Use the correct datetime
        return obj.isoformat()  # Convert Timestamp/datetime to ISO 8601 string format
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def get_model_by_tablename(table_name):
    return globals().get(table_name)

class DynamicGetResource(Resource):
    def get(self, id=None):
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('tableName', type=str, required=True, location='json', help='Table name must be provided')
            parser.add_argument('fieldName', type=str, location='json', help='Field name must be provided')
            parser.add_argument('value', type=str, location='json', help='Values must be provided')
            
            parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
            parser.add_argument('table_id', type=str, default="id", location='json', help='Provide the correct `id` name.')

            args = parser.parse_args()

            table_name = args['tableName']
            field_name = args['fieldName']
            values = args['value']
            page_no = args['pageNo']
            page_size = args['pageSize']
            table_id = args['table_id']
            
            table_name = globals().get(table_name)
            
            if id is None:
                if field_name:
                    # Dynamically filter by field name
                    if not hasattr(table_name, field_name):
                        return jsonify({"error": f"Field {field_name} does not exist in table {table_name}"}), 400
                    
                    query = table_name.query.filter(getattr(table_name, field_name) == values)
                else:
                    query = table_name.query
                
                query = query.order_by(getattr(table_name, table_id))
                total = query.count()
                
                # Apply pagination
                data = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [item.to_dict() for item in data],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size
                }, 200
            else:
                data = table_name.query.get(id)
                if data is None:
                    abort(404, message=f"AvailableJobs {id} doesn't exist")
                return {
                    "data": [data.to_dict()]
                }
        except Exception as e:
            return {'message': str(e)}, 500


class CallProcedureResourceLeave(Resource):
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg','png'}
    UPLOAD_FOLDER = 'uploads/StaffLeaveRequest/'
    logging.basicConfig(level=logging.INFO)     
    logger = logging.getLogger(__name__)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('procedure_name', type=str, required=True, location='form',
                            help='Stored Procedure or Table name must be given')
        parser.add_argument('attachments[]', type=FileStorage, location='files', action='append',
                            help='Attachments must be uploaded as files')

        args = parser.parse_args()
        procedure_name = args['procedure_name']
        attachments = args['attachments[]']

        parameters = {
            'UserId': request.form.get('parameters[UserId]'),
            'LeaveTypeId': request.form.get('parameters[LeaveTypeId]'),
            'FromDate': request.form.get('parameters[FromDate]'),
            'ToDate': request.form.get('parameters[ToDate]'),
            'Reason': request.form.get('parameters[Reason]'),
            'CampusId': request.form.get('parameters[CampusId]')
        }

        logging.info(f"Parameters: {parameters}")

        if not procedure_name:
            return {'error': 'Procedure name is required'}, 400

        param_values = tuple(parameters.values())
        call_procedure_query = f"EXEC {procedure_name} {', '.join(['?'] * len(parameters))};"
        logging.info(f"Executing SQL: {call_procedure_query} with values: {param_values}")

        connection = db.engine.raw_connection()
        last_record_id = None  # Initialize here

        try:
            cursor = connection.cursor()
            cursor.execute(call_procedure_query, param_values)

            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()

                logging.info(f"Raw results: {results}")
                result_list = [dict(zip(columns, row)) for row in results]
                logging.info(f"Structured results: {result_list}")

                results_df = pd.DataFrame(result_list)
                status_message = results_df.loc[0, 'Status'] if not results_df.empty else None
                last_record_id = results_df.loc[0, 'LastRecordId'] if 'LastRecordId' in results_df.columns else None

                # Ensure LastRecordId is correctly fetched from the result set
                last_record_id = int(last_record_id) if last_record_id is not None else None
                logging.info(f"Last record ID: {last_record_id}")

                # If the status is success, proceed with saving attachments
                if status_message.strip() == 'Your Leave request has been submitted successfully.' and last_record_id:
                    # Proceed with file saving and other actions
                    saved_file_paths = []  # Track saved file paths

                    if attachments:
                        for attachment in attachments:
                            current_date = datetime.now().strftime("%y%m%d")
                            new_filename = f"{last_record_id}_{current_date}{os.path.splitext(attachment.filename)[1]}"
                            file_path, error_response, status_code = self.save_attachment(attachment, new_filename)
                            if error_response:  # Stop further processing if any attachment fails
                                return error_response, status_code
                            saved_file_paths.append(file_path)

                    # After saving attachments, update the LeaveApplicationPath in the database
                    if saved_file_paths:
                        for file_path in saved_file_paths:
                            update_query = (
                                "UPDATE StaffLeaveRequest "
                                "SET LeaveApplicationPath = ? "
                                "WHERE Id = ?;"
                            )
                            logging.info(f"Executing update query: {update_query} with params: {file_path}, {last_record_id}")
                            cursor.execute(update_query, (file_path, last_record_id))
                            logging.info(f"Updated file path: {file_path}")

                    return {
                        "data": results_df.to_dict(orient='records')
                    }, 200

                else:
                    logging.error(f"Leave request status failed: {status_message.strip()}"), 400
                    return {
                        "data": results_df.to_dict(orient='records')
                    }, 200


        except SQLAlchemyError as e:
            connection.rollback()
            logging.error(f"Database error while executing {call_procedure_query} with values {param_values}: {e}")
            return {'error': 'Database error occurred.'}, 500
        except Exception as e:
            connection.rollback()
            logging.error(f"General error while executing {call_procedure_query}: {e}")
            return {'error': 'An unexpected error occurred.'}, 500
        finally:
            cursor.close()
            connection.commit()
            connection.close()
    

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('procedure_name', type=str, required=True, location='form',
                            help='Stored Procedure or Table name must be given')
        parser.add_argument('attachments[]', type=FileStorage, location='files', action='append',
                            help='Attachments must be uploaded as files')

        args = parser.parse_args()
        procedure_name = args['procedure_name']
        attachments = args['attachments[]']
        leave_id = request.form.get('parameters[Id]')  # Ensure this is provided

        parameters = {
            'UserId': request.form.get('parameters[UserId]'),
            'LeaveTypeId': request.form.get('parameters[LeaveTypeId]'),
            'FromDate': request.form.get('parameters[FromDate]'),
            'ToDate': request.form.get('parameters[ToDate]'),
            'Reason': request.form.get('parameters[Reason]'),
            'Id': leave_id
        }

        logging.info(f"Parameters: {parameters}")

        if not procedure_name or not leave_id:
            return {'error': 'Procedure name and leave ID are required'}, 400

        param_values = tuple(parameters.values())
        call_procedure_query = f"EXEC {procedure_name} {', '.join(['?'] * len(parameters))};"
        logging.info(f"Executing SQL: {call_procedure_query} with values: {param_values}")

        connection = db.engine.raw_connection()
        saved_file_paths = []  # Initialize the variable here to avoid uninitialized reference

        try:
            cursor = connection.cursor()
            cursor.execute(call_procedure_query, param_values)

            # Fetch results (for the status message)
            columns = [column[0] for column in cursor.description] if cursor.description else []
            results = cursor.fetchall()
            result_list = [dict(zip(columns, row)) for row in results] if results else []

            # Log status message for debugging
            status_message = None
            if result_list:
                status_message = result_list[0].get('Status', None)
            logging.info(f"Status message from procedure: {status_message}")

            # If the status message is not 'Leave request updated successfully.', return the result
            if status_message != 'Leave request updated successfully.':
                return {
                    "data": result_list,
                    "leave_id": leave_id,
                }, 200

            # Check if the leave ID already has an attachment
            cursor.execute("SELECT LeaveApplicationPath FROM StaffLeaveRequest WHERE Id = ?", (leave_id,))
            existing_file_row = cursor.fetchone()
            existing_file_path = existing_file_row[0] if existing_file_row else None

            # # If no attachments are provided, delete existing file and set path to NULL
            # if not attachments:
            #     if existing_file_path:
            #         try:
            #             if os.path.exists(existing_file_path):
            #                 os.remove(existing_file_path)
            #                 logging.info(f"Deleted existing file at: {existing_file_path}")
            #         except Exception as delete_error:
            #             logging.error(f"Error deleting file at {existing_file_path}: {delete_error}")
            #     cursor.execute("UPDATE StaffLeaveRequest SET LeaveApplicationPath = NULL WHERE Id = ?", (leave_id,))
            #     logging.info(f"Updated LeaveApplicationPath to NULL for leave ID: {leave_id}")
            
            # If no attachments are provided, avoid nullifying the existing path
            if not attachments:
                logging.info(f"No new attachments provided. Retaining existing file path: {existing_file_path}")
            # If attachments are provided, update the file path in the database
            else:
                # If there's an existing file, delete it before saving the new one
                if existing_file_path and os.path.exists(existing_file_path):
                    try:
                        os.remove(existing_file_path)
                        logging.info(f"Deleted existing file at: {existing_file_path}")
                    except Exception as delete_error:
                        logging.error(f"Error deleting file at {existing_file_path}: {delete_error}")
                for attachment in attachments:
                    current_date = datetime.now().strftime("%y%m%d")
                    new_filename = f"{leave_id}_{current_date}{os.path.splitext(attachment.filename)[1]}"
                    file_path, error_response, status_code = self.save_attachment(attachment, new_filename)
                    if error_response:
                        return error_response, status_code
                    saved_file_paths.append(file_path)

                # Update the LeaveApplicationPath with the new file(s)
                if saved_file_paths:
                    cursor.execute("UPDATE StaffLeaveRequest SET LeaveApplicationPath = ? WHERE Id = ?", 
                                (saved_file_paths[0], leave_id))  # You could update for multiple files if necessary
                    logging.info(f"Updated LeaveApplicationPath with new file path for leave ID: {leave_id}")

            # Commit changes after file update
            connection.commit()

            # Return success message if leave request is updated successfully
            return {
                "data": result_list,
                "leave_id": leave_id,
            }, 200

        except Exception as e:
            connection.rollback()
            logging.error(f"Error: {e}")
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

    def save_attachment(self, attachment, new_filename):
        if attachment and self.allowed_file(attachment.filename):
            if attachment.filename == '':
                return None, {"error": "No selected file"}, 400

            file_path = os.path.join(self.UPLOAD_FOLDER, new_filename)
            os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)

            try:
                attachment.save(file_path)
                logging.info(f'Saved file: {file_path}')
                return file_path, None, None
            except Exception as e:
                logging.error(f'Failed to save file {new_filename}: {str(e)}')
                return None, {"error": "Failed to save attachment"}, 500
        else:
            return None, {"error": f'Invalid file type for attachment: {attachment.filename}'}, 400

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS










class CallProcedureResource(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('procedure_name', type=str, required=True, location='json', help='Stored Procedure or Table name must be given')
        parser.add_argument('parameters', type=dict, default={}, location='json', help='Parameters must be a dictionary')
        
        args = parser.parse_args()
        
        procedure_name = args['procedure_name']
        parameters = args['parameters']
        
        results = []

        if not procedure_name:
            return {'error': 'Procedure name is required'}, 400

        # Validate that parameters are either absent or a dictionary
        if parameters and not isinstance(parameters, dict):
            return {'error': 'Parameters should be a dictionary if provided'}, 400

        # Prepare the parameters if they exist
        custom_parameters = [f'@{key} = "{value}"' if isinstance(value, str) else f"@{key} = {value}" for key, value in parameters.items()]
        param_placeholders = ', '.join(custom_parameters)
        
        # Connect to the database
        connection = db.engine.raw_connection()
        try:
            cursor = connection.cursor()
            if param_placeholders:
                call_procedure_query = f"EXEC {procedure_name} {param_placeholders}"
                cursor.execute(call_procedure_query)
            else:
                call_procedure_query = f"exec {procedure_name};"
                cursor.execute(call_procedure_query)

            print(f"Executing query: {call_procedure_query}")  # Debugging step to verify the query
            
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
            cursor.close()
            connection.commit()
            
            if results:
                # Convert results to a list of dictionaries for JSON response
                result_list = [dict(zip(columns, row)) for row in results]
                
                # Create a pandas DataFrame from the result
                temp = pd.DataFrame(result_list)

                # Convert DataFrame to a list of dictionaries
                results = temp.to_dict(orient='records')

                # Use json.dumps with the custom decimal-to-float converter
                json_data = json.dumps({"data": results}, default=custom_serializer)

                json_data = json.loads(json_data)

                return json_data
            else:
                return {"data": results}

        except SQLAlchemyError as e:
            connection.rollback()
            return {'error': str(e)}, 500
        except Exception as e:
            connection.rollback()
            return {'error': str(e)}, 500
        finally:
            connection.close()

class DynamicPostResource_With_PKReturn(Resource):
    def post(self):
        data = request.get_json()
        table_name = data.get('Table_Name')
        insert_data = data.get('Data')

        if not table_name or not insert_data:
            return {'status': 'error', 'message': 'Table_Name and Data are required'}, 400

        # Get the model class based on the table name
        model_class = get_model_by_tablename(table_name)
        if not model_class:
            return {'status': 'error', 'message': f'Table {table_name} does not exist'}, 400

        # Validate that insert_data is a list of dictionaries
        if not isinstance(insert_data, list) or not all(isinstance(item, dict) for item in insert_data):
            return {'status': 'error', 'message': 'Data should be a list of dictionaries'}, 400

        # Insert records
        try:
            records = [model_class(**item) for item in insert_data]
            db.session.add_all(records)  # Add the records using add_all
            db.session.commit()

            # Extract the primary key values after commit
            pk_values = [getattr(record, model_class.__mapper__.primary_key[0].name) for record in records]

            return {
                'status': 'success',
                'message': f'{len(records)} records inserted into {table_name} successfully',
                'primary_keys': pk_values
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}, 500


class DynamicPostResource(Resource):
    def post(self):
        data = request.get_json()
        table_name = data.get('Table_Name')
        insert_data = data.get('Data')

        if not table_name or not insert_data:
            return {'status': 'error',
                'message': 'Table_Name and Data are required'}, 400

        # Get the model class based on the table name
        model_class = get_model_by_tablename(table_name)
        if not model_class:
            return {'status': 'error',
                'message': f'Table {table_name} does not exist'}, 400

        # Validate that insert_data is a list of dictionaries
        if not isinstance(insert_data, list) or not all(isinstance(item, dict) for item in insert_data):
            return {'status': 'error',
                'message': 'Data should be a list of dictionaries'}, 400

        # Insert records
        try:
            records = [model_class(**item) for item in insert_data]
            db.session.bulk_save_objects(records)
            db.session.commit()
            return {'status': 'success',
                'message': f'{len(records)} records inserted into {table_name} successfully'}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'status': 'error',
                'message': str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {'status': 'error',
                'message': str(e)}, 500

class DynamicUpdateResource(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Table_Name', type=str, required=True, help='Table Name is required')
        parser.add_argument('history_table', type=str, required=False)
        parser.add_argument('id', type=int, required=True, help='Kindly provide the record ID')
        parser.add_argument('Data', type=dict, required=True, help='Data should be in JSON')
        

        args = parser.parse_args()

        table_name = args['Table_Name']
        history_table = args['history_table']
        record_id = args['id']
        update_data = args['Data']

        if not table_name or not record_id or not update_data:
            return {'status': 'error', 'message': 'Table_Name, id, and Data are required'}, 400

        # Get the model class based on the table name
        model_class = globals().get(table_name)

        if not model_class:
            return {'status': 'error', 'message': f'Table {table_name} does not exist'}, 400

        # Find the record by id and update it with the provided data
        try:
            record = db.session.query(model_class).get(record_id)
            if not record:
                return {'error': f'Record with id {record_id} not found in {table_name}'}, 404
            
            try:
                if history_table:
                    history_model_class = globals().get(history_table)
                    
                    if not history_model_class:
                        return {'status': 'error', 'message': f'History Table {history_table} does not exist'}, 400
                    
                    # Convert the record to a dictionary and insert into the history table
                    history_data = record.__dict__.copy()
                    
                    history_data.pop('_sa_instance_state', None)  # Remove the SQLAlchemy instance state
                    # history_data = {f'History_{key}': value for key, value in record.__dict__.items() if key not in ['_sa_instance_state', 'CreatedDate', 'CreatedBy', 'UpdatedBy', 'UpdatedDate', 'InActive']}
                    # Keys to exclude from prefixing
                    exclude_keys = {'CreatedDate', 'CreatedBy', 'UpdatedBy', 'UpdatedDate', 'InActive'}

                    # Efficiently update dictionary
                    updated_history_data = {
                        (f'History_{key}' if key not in exclude_keys else key): value
                        for key, value in history_data.items()
                    }
                    updated_history_data['CreatedDate'] = datetime.utcnow()  # Add CreatedDate column
                    
                    history_record = history_model_class(**updated_history_data)
                    db.session.add(history_record)
                    db.session.commit()

            except SQLAlchemyError as e:
                db.session.rollback()
                return {'status': 'error', 'message': str(e)}, 500
            except Exception as e:
                db.session.rollback()
                return {'status': 'error', 'message': str(e)}, 500
            
            for key, value in update_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)

            db.session.commit()
            
            if history_table:
                return {'status': 'success', 'message': f'Record in {history_table} added successfully'}, 200
            else:
                return {'status': 'success', 'message': f'Record in {table_name} with id {record_id} updated successfully'}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}, 500

class DynamicInsertOrUpdateResource(Resource):
    def post(self):
        data = request.get_json()
        table_name = data.get('Table_Name')
        insert_data = data.get('Data')
        conditions = data.get('Conditions')

        if not table_name or not insert_data or not conditions:
            return {'error': 'Table_Name, Data, and Conditions are required'}, 400

        # Get the model class based on the table name
        model_class = get_model_by_tablename(table_name)
        if not model_class:
            return {'error': f'Table {table_name} does not exist'}, 400

        # Validate that insert_data is a list of dictionaries
        if not isinstance(insert_data, list) or not all(isinstance(item, dict) for item in insert_data):
            return {'error': 'Data should be a list of dictionaries'}, 400

        # Validate that conditions is a dictionary
        if not isinstance(conditions, dict):
            return {'error': 'Conditions should be a dictionary'}, 400

        """
        # Define max lengths for string fields in OneTimeDeduction
        string_fields_max_length = {
            'OneTimeDeduction_DeductionMonth': 15,
            # Add other fields with their max lengths if needed
        }

        # Validate string lengths
        for item in insert_data:
            for field, max_length in string_fields_max_length.items():
                if field in item and len(item[field]) > max_length:
                    return {'error': f'{field} exceeds maximum length of {max_length}'}, 400
        """
        updated_records = []
        inserted_records = []

        try:
            for item in insert_data:
                # Build the filter conditions dynamically for each item
                query_conditions = []
                for field, value in conditions.items():
                    if hasattr(model_class, field):
                        if isinstance(value, list):
                            query_conditions.append(getattr(model_class, field).in_(value))
                        else:
                            query_conditions.append(getattr(model_class, field) == item.get(field, value))

                existing_record = model_class.query.filter(and_(*query_conditions)).first()

                if existing_record:
                    # Update the existing record with new data from the item
                    for key, value in item.items():
                        if hasattr(existing_record, key):
                            setattr(existing_record, key, value)
                    existing_record.UpdateDate = datetime.utcnow()
                    existing_record.UpdatorId = item.get('CreatorId')
                    updated_records.append(existing_record)
                else:
                    # Insert a new record
                    new_record = model_class(**item)
                    new_record.CreateDate = datetime.utcnow()
                    inserted_records.append(new_record)

            if updated_records:
                db.session.bulk_save_objects(updated_records)
            if inserted_records:
                db.session.bulk_save_objects(inserted_records)
            
            db.session.commit()

            return {
                'status': 'success',
                'message': f'{len(inserted_records)} records inserted, {len(updated_records)} records updated in {table_name} successfully'
            }, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'status': 'error',
                'message': str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {'status': 'error',
                'message': str(e)}, 500

class DynamicDeleteResource(Resource):
    def delete(self, id):
        data = request.get_json()
        table_name = data.get('Table_Name')
        
        if not table_name:
            return {'status': 'error',
                'message': 'Table Name are required'}, 400

        # Get the model class based on the table name
        model_class = get_model_by_tablename(table_name)
        if not model_class:
            return {'status': 'error',
                'message': f'Table {table_name} does not exist'}, 400
        
        try:
            record = db.session.query(model_class).get(id)
            record.InActive = 1
            
            db.session.commit()
            return {'status': 'error',
                'message': 'StaffPromotions deleted successfully'}, 200
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'status': 'error',
                'message': str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {'status': 'error',
                'message': str(e)}, 500

class UploadFileResource(Resource):
    def post(self):
        try:
            ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx']
            MAIN_UPLOAD_FOLDER = 'uploads\\'
            
            # First, initialize form_data from request.form to avoid referencing an uninitialized variable
            form_data = request.form.to_dict()

            # Check if a table name is provided
            if not form_data.get('Table_Name'):
                return {'status': 'error', 'message': "Table name required"}, 400

            # Get the model class based on the table name
            model_class = get_model_by_tablename(form_data.get('Table_Name'))
            if not model_class:
                return {'status': 'error', 'message': f'Table {form_data.get("Table_Name")} does not exist'}, 400

            MAIN_UPLOAD_FOLDER = MAIN_UPLOAD_FOLDER + form_data['Table_Name']
            
            # Process files if provided
            if request.files:
                uploaded_files = []
                for key in request.files:
                    file = request.files[key]
                    
                    if file.filename == '':
                        continue  # Skip empty files

                    # Secure the filename and save the file
                    filename = secure_filename(file.filename)
                    UPLOAD_FOLDER = MAIN_UPLOAD_FOLDER + '\\' + key
                    
                    # Ensure the directory exists
                    if not os.path.exists(UPLOAD_FOLDER):
                        os.makedirs(UPLOAD_FOLDER)
                    
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    uploaded_files.append((filename, file_path, key))
                    # Add the file path to form data
                    form_data[key] = file_path
            else:
                uploaded_files = []

            # Convert boolean fields from 'true'/'false' to True/False
            for key, value in form_data.items():
                try:
                    if value.lower() == 'true':
                        form_data[key] = True
                    elif value.lower() == 'false':
                        form_data[key] = False
                except:
                    pass

            # Insert record into the database after processing files and form data
            try:
                Table_Name = form_data['Table_Name']
                form_data.pop("Table_Name")  # Remove Table_Name from form data for DB model
                
                # Create and insert the record into the database
                record = model_class(**form_data)
                db.session.add(record)
                db.session.commit()
                
                return {'status': 'success', 'message': f'Records inserted into {Table_Name} successfully'}, 201
            except SQLAlchemyError as e:
                db.session.rollback()
                return {'status': 'error', 'message': str(e)}, 500
            except Exception as e:
                db.session.rollback()
                return {'status': 'error', 'message': str(e)}, 500
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500




    # def post(self):
    #     try:
    #         ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx']
    #         MAIN_UPLOAD_FOLDER = 'uploads\\'
            
    #         if not request.files:
    #             return {'message': 'No file part in the request'}, 400

    #         # Process other form data
    #         form_data = request.form.to_dict()
            
    #         if not form_data.get('Table_Name'):
    #             return {'status': 'error',
    #                     'message': "table name required"}, 400
            
    #         model_class = get_model_by_tablename(form_data.get('Table_Name'))
    #         if not model_class:
    #             return {'status': 'error',
    #                 'message': f'Table {form_data.get('Table_Name')} does not exist'}, 400
            
    #         MAIN_UPLOAD_FOLDER = MAIN_UPLOAD_FOLDER + form_data['Table_Name']
            
    #         uploaded_files = []
    #         for key in request.files:
                
    #             file = request.files[key]
    #             if file.filename == '':
    #                 continue

    #             # Secure the filename and save the file
    #             filename = secure_filename(file.filename)
                
    #             UPLOAD_FOLDER = MAIN_UPLOAD_FOLDER + '\\' + key
                
    #             if not os.path.exists(UPLOAD_FOLDER):
    #                 os.makedirs(UPLOAD_FOLDER)
                
    #             file_path = os.path.join(UPLOAD_FOLDER, filename)
    #             file.save(file_path)
    #             uploaded_files.append((filename, file_path, key))
    #             form_data[key] = file_path
            
    #         if not uploaded_files:
    #             return {'message': 'No selected files'}, 400

    #         # Convert boolean fields from 'true'/'false' to True/False
    #         for key, value in form_data.items():
    #             try:
    #                 if value.lower() == 'true':
    #                     form_data[key] = True
    #                 elif value.lower() == 'false':
    #                     form_data[key] = False
    #             except:
    #                 pass
            
    #         # form_data['CreatedDate'] = datetime.utcnow()  # Add CreatedDate column
    #         # Insert records
    #         try:
    #             Table_Name = form_data['Table_Name']
    #             form_data.pop("Table_Name")
    #             record = model_class(**form_data)
    #             db.session.add(record)
    #             db.session.commit()
    #             return {'status': 'success',
    #                 'message': f'Records inserted into {Table_Name} successfully'}, 201
    #         except SQLAlchemyError as e:
    #             db.session.rollback()
    #             return {'status': 'error',
    #                 'message': str(e)}, 500
    #         except Exception as e:
    #             db.session.rollback()
    #             return {'status': 'error',
    #                 'message': str(e)}, 500
    #     except Exception as e:
    #         return {'status': 'error', 'message': str(e)}, 500

    def put(self, id):
        
        if id:
            try:
                ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx']
                MAIN_UPLOAD_FOLDER = 'uploads\\'

                # Process other form data
                form_data = request.form.to_dict()
                print("form_data",form_data)
                
                if not form_data.get('Table_Name'):
                    return {'status': 'error',
                            'message': "table name required"}, 400
                
                model_class = get_model_by_tablename(form_data.get('Table_Name'))
                
                if not model_class:
                    return {'status': 'error',
                        'message': f'Table {form_data.get('Table_Name')} does not exist'}, 400
                
                MAIN_UPLOAD_FOLDER = MAIN_UPLOAD_FOLDER + form_data['Table_Name']
                
                if request.files:
                    print("Request files",request.files)
                    for key in request.files:
                        
                        file = request.files[key]
                        if file.filename == '':
                            continue

                        # Secure the filename and save the file
                        filename = secure_filename(file.filename)
                        
                        UPLOAD_FOLDER = MAIN_UPLOAD_FOLDER + '\\' + key
                        
                        if not os.path.exists(UPLOAD_FOLDER):
                            os.makedirs(UPLOAD_FOLDER)
                        
                        file_path = os.path.join(UPLOAD_FOLDER, filename)
                        file.save(file_path)
                        form_data[key] = file_path

                # Convert boolean fields from 'true'/'false' to True/False
                for key, value in form_data.items():
                    try:
                        if value.lower() == 'true':
                            form_data[key] = True
                        elif value.lower() == 'false':
                            form_data[key] = False
                    except:
                        pass
                
                form_data['UpdatedDate'] = datetime.utcnow()  # Add CreatedDate column
                
                Table_Name = form_data['Table_Name']
                form_data.pop("Table_Name")
                history_table = ""
                
                # Find the record by id and update it with the provided data
                try:
                    record = db.session.query(model_class).get(id)
                    if not record:
                        return {'error': f'Record with id {id} not found in {Table_Name}'}, 404
                    
                    try:
                        history_table = form_data.get('History_Table')
                        
                        if history_table:
                            form_data.pop("History_Table")
                            history_model_class = globals().get(history_table)
                            
                            if not history_model_class:
                                return {'status': 'error', 'message': f'History Table {history_table} does not exist'}, 400
                            
                            # Convert the record to a dictionary and insert into the history table
                            history_data = record.__dict__.copy()
                            
                            history_data.pop('_sa_instance_state', None)  # Remove the SQLAlchemy instance state
                            # history_data = {f'History_{key}': value for key, value in record.__dict__.items() if key not in ['_sa_instance_state', 'CreatedDate', 'CreatedBy', 'UpdatedBy', 'UpdatedDate', 'InActive']}
                            # Keys to exclude from prefixing
                            exclude_keys = {'CreatedDate', 'CreatedBy', 'UpdatedBy', 'UpdatedDate', 'InActive'}

                            # Efficiently update dictionary
                            updated_history_data = {
                                (f'History_{key}' if key not in exclude_keys else key): value
                                for key, value in history_data.items()
                            }
                            updated_history_data['CreatedDate'] = datetime.utcnow()  # Add CreatedDate column
                            
                            history_record = history_model_class(**updated_history_data)
                            db.session.add(history_record)
                            db.session.commit()

                    except SQLAlchemyError as e:
                        db.session.rollback()
                        return {'status': 'error', 'message': str(e)}, 500
                    except Exception as e:
                        db.session.rollback()
                        return {'status': 'error', 'message': str(e)}, 500
                    
                    for key, value in form_data.items():
                        if hasattr(record, key):
                            print(f"Updating field {key} with value {value}")
                            setattr(record, key, value)
                    
                    db.session.commit()
                    
                    if history_table:
                        return {'status': 'success', 'message': f'Record in {history_table} added successfully'}, 200
                    else:
                        return {'status': 'success', 'message': f'Record in {Table_Name} with id {id} updated successfully'}, 200
                except SQLAlchemyError as e:
                    db.session.rollback()
                    return {'status': 'error', 'message': str(e)}, 500
                except Exception as e:
                    db.session.rollback()
                    return {'status': 'error', 'message': str(e)}, 500
            
            except Exception as e:
                    db.session.rollback()
                    return {'status': 'error', 'message': str(e)}, 500

        else:
            return {
                "status": "error",
                "message": "id not found at the endpoint"
            }, 400
















