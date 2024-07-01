from flask_restful import Resource, reqparse, abort
from app import db
from flask import jsonify, request
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import and_
from models.models import *
import pyodbc
from sqlalchemy.exc import SQLAlchemyError

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
        custom_paramters = [f'@{key} = {value}' for key, value in parameters.items()]
        param_placeholders = ', '.join(custom_paramters)

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

            columns = [column[0] for column in cursor.description]
            results = cursor.fetchall()
            cursor.close()
            connection.commit()
            
            # Convert results to a list of dictionaries for JSON response
            result_list = [dict(zip(columns, row)) for row in results]
            
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
                return jsonify(
                    {"data": result_list}
                )

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
            return {'error': 'Table_Name and Data are required'}, 400

        # Get the model class based on the table name
        model_class = get_model_by_tablename(table_name)
        if not model_class:
            return {'error': f'Table {table_name} does not exist'}, 400

        # Validate that insert_data is a list of dictionaries
        if not isinstance(insert_data, list) or not all(isinstance(item, dict) for item in insert_data):
            return {'error': 'Data should be a list of dictionaries'}, 400

        # Insert records
        try:
            records = [model_class(**item) for item in insert_data]
            print(records)
            db.session.bulk_save_objects(records)
            db.session.commit()
            return {'message': f'{len(records)} records inserted into {table_name} successfully'}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

class DynamicUpdateResource(Resource):
    def put(self):
        data = request.get_json()
        table_name = data.get('Table_Name')
        record_id = data.get('id')  # Assuming the primary key field is 'id'
        update_data = data.get('Data')

        if not table_name or not record_id or not update_data:
            return {'error': 'Table_Name, id, and Data are required'}, 400

        # Get the model class based on the table name
        model_class = globals().get(table_name)

        if not model_class:
            return {'error': f'Table {table_name} does not exist'}, 400

        # Find the record by id and update it with the provided data
        try:
            record = db.session.query(model_class).get(record_id)
            if not record:
                return {'error': f'Record with id {record_id} not found in {table_name}'}, 404

            for key, value in update_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)

            db.session.commit()
            return {'message': f'Record in {table_name} with id {record_id} updated successfully'}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

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
                'message': f'{len(inserted_records)} records inserted, {len(updated_records)} records updated in {table_name} successfully'
            }, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

class DynamicDeleteResource(Resource):
    def delete(self, id):
        data = request.get_json()
        table_name = data.get('Table_Name')
        
        if not table_name:
            return {'error': 'Table Name are required'}, 400

        # Get the model class based on the table name
        model_class = get_model_by_tablename(table_name)
        if not model_class:
            return {'error': f'Table {table_name} does not exist'}, 400
        
        try:
            record = db.session.query(model_class).get(id)
            record.InActive = 1
            
            db.session.commit()
            return {'message': 'StaffPromotions deleted successfully'}, 200
    
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500