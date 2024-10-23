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
from decimal import Decimal
import pandas as pd
from datetime import datetime
import logging

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

class DetailNotificationProcedure(Resource):
    def post(self):
        logging.info("Received a POST request at /detailnotification/procedure")
        # Get JSON data from the request
        data = request.get_json()
        if not data:
            return {"error": "No input data provided"}, 400

        # Log incoming data
        logging.info("Incoming data: %s", data)

        procedure_name = data.get("procedure_name")
        staff_ids = data.get("parameters", {}).get("StaffIds", [])
        notification_id = data.get("parameters", {}).get("NotificationId")

        if not procedure_name or not staff_ids or notification_id is None:
            return {"error": "Missing required parameters"}, 400

        try:
            # Use SQLAlchemy's raw connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()

            # Prepare the SQL command
            sql_command = f"EXEC {procedure_name} @StaffIds = '{staff_ids}', @NotificationId = {notification_id}"
            logging.info("Executing SQL command: %s", sql_command)

            # Execute the stored procedure 
            cursor.execute(sql_command)

            # Commit the transaction
            connection.commit()

            # Close the cursor and connection
            cursor.close()
            connection.close()

            return {"message": "Procedure executed successfully."}, 200

        except SQLAlchemyError as e:
            connection.rollback()
            logging.error("SQLAlchemy error: %s", str(e))
            return {"error": str(e)}, 500
        except Exception as e:
            logging.error("Error executing procedure: %s", str(e))
            return {"error": str(e)}, 500

class CallProcedureResource(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('procedure_name', type=str, required=True, location='json', help='Stored Procedure or Table name must be given')
        parser.add_argument('pageNo', type=int, location='json', help='Page number must be an integer')
        parser.add_argument('per_page', type=int, location='json', help='Page size must be an integer')
        parser.add_argument('parameters', type=dict, default={}, location='json', help='Parameters must be a dictionary')
        
        args = parser.parse_args()
        
        procedure_name = args['procedure_name']
        page = args['pageNo']
        per_page = args['per_page']
        parameters = args['parameters']
        
        
        # procedure_name = data.get('procedure_name')
        # parameters = data.get('parameters', {})
        # page = data.get('pageNo', 1)
        # per_page = data.get('per_page', 10)

        if not procedure_name:
            return {'error': 'Procedure name is required'}, 400

        # Validate that parameters are either absent or a dictionary
        if parameters and not isinstance(parameters, dict):
            return {'error': 'Parameters should be a dictionary if provided'}, 400

        # Prepare the parameters if they exist
        # custom_parameters = [f'@{key} = {value}' for key, value in parameters.items()]
        custom_parameters = [f'@{key} = "{value}"' if isinstance(value, str) else f"@{key} = {value}" for key, value in parameters.items()]
        param_placeholders = ', '.join(custom_parameters)

        print(parameters, custom_parameters, param_placeholders)
        
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

            print(call_procedure_query)
            
            columns = [column[0] for column in cursor.description]
            results = cursor.fetchall()
            cursor.close()
            connection.commit()
            
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
            if page and per_page:
                # Apply pagination
                total = len(result_list)
                start = (page - 1) * per_page
                end = start + per_page
                paginated_results = result_list[start:end]

                return jsonify({
                    'data': paginated_results,
                    'page': page,
                    'per_page': per_page,
                    'total': total
                })
            else:
                return {"data": result_list}

        except SQLAlchemyError as e:
            connection.rollback()
            return {'error': str(e)}, 500
        except Exception as e:
            connection.rollback()
            return {'error': str(e)}, 500
        finally:
            connection.close()

class DynamicPostResource(Resource):
    def post(self):
        data = request.get_json()
        table_name = data.get('Table_Name')
        insert_data = data.get('Data')

        if not table_name or not insert_data:
            return {
                'status': 'error',
                'message': 'Table_Name and Data are required'
            }, 400

        # Get the model class based on the table name
        model_class = get_model_by_tablename(table_name)
        if not model_class:
            return {
                'status': 'error',
                'message': f'Table {table_name} does not exist'
            }, 400

        # Validate that insert_data is a list of dictionaries
        if not isinstance(insert_data, list) or not all(isinstance(item, dict) for item in insert_data):
            return {
                'status': 'error',
                'message': 'Data should be a list of dictionaries'
            }, 400

        # Insert records
        try:
            records = [model_class(**item) for item in insert_data]
            db.session.add_all(records)  # Use add_all to track the objects
            db.session.commit()

            # Collect primary keys of inserted records
            inserted_ids = [record.Id for record in records]
            return {
                'status': 'success',
                'message': f'{len(records)} records inserted into {table_name} successfully',
                'inserted_ids': inserted_ids  # Return the primary keys
            }, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {
                'status': 'error',
                'message': str(e)
            }, 500
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error',
                'message': str(e)
            }, 500

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
            
            if not request.files:
                return {'message': 'No file part in the request'}, 400

            # Process other form data
            form_data = request.form.to_dict()
            
            if not form_data.get('Table_Name'):
                return {'status': 'error',
                        'message': "table name required"}, 400
            
            model_class = get_model_by_tablename(form_data.get('Table_Name'))
            if not model_class:
                return {'status': 'error',
                    'message': f'Table {form_data.get('Table_Name')} does not exist'}, 400
            
            MAIN_UPLOAD_FOLDER = MAIN_UPLOAD_FOLDER + form_data['Table_Name']
            
            uploaded_files = []
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
                uploaded_files.append((filename, file_path, key))
                form_data[key] = file_path
            
            if not uploaded_files:
                return {'message': 'No selected files'}, 400

            # Convert boolean fields from 'true'/'false' to True/False
            for key, value in form_data.items():
                try:
                    if value.lower() == 'true':
                        form_data[key] = True
                    elif value.lower() == 'false':
                        form_data[key] = False
                except:
                    pass
            
            # form_data['CreatedDate'] = datetime.utcnow()  # Add CreatedDate column
            # Insert records
            try:
                Table_Name = form_data['Table_Name']
                form_data.pop("Table_Name")
                record = model_class(**form_data)
                db.session.add(record)
                db.session.commit()
                return {'status': 'success',
                    'message': f'Records inserted into {Table_Name} successfully'}, 201
            except SQLAlchemyError as e:
                db.session.rollback()
                return {'status': 'error',
                    'message': str(e)}, 500
            except Exception as e:
                db.session.rollback()
                return {'status': 'error',
                    'message': str(e)}, 500
        except Exception as e:
            return {'status': 'error', 'message': str(e)}, 500

    def put(self, id):
        
        if id:
            try:
                ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx']
                MAIN_UPLOAD_FOLDER = 'uploads\\'

                # Process other form data
                form_data = request.form.to_dict()
                
                if not form_data.get('Table_Name'):
                    return {'status': 'error',
                            'message': "table name required"}, 400
                
                model_class = get_model_by_tablename(form_data.get('Table_Name'))
                
                if not model_class:
                    return {'status': 'error',
                        'message': f'Table {form_data.get('Table_Name')} does not exist'}, 400
                
                MAIN_UPLOAD_FOLDER = MAIN_UPLOAD_FOLDER + form_data['Table_Name']
                
                if request.files:
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
















