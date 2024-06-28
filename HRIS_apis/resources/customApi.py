from flask_restful import Resource, reqparse, abort
from app import db
from flask import jsonify, request
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import and_
from models.models import *
import pyodbc

class CustomApiResource(Resource):
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
        data = request.get_json()
        procedure_name = data.get('procedure_name')
        parameters = data.get('parameters', {})
        page = data.get('page', 1)
        per_page = data.get('per_page', 10)

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

        except SQLAlchemyError as e:
            connection.rollback()
            return {'error': str(e)}, 500
        except Exception as e:
            connection.rollback()
            return {'error': str(e)}, 500
        finally:
            connection.close()