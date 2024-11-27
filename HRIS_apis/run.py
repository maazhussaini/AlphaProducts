from app import create_app
from waitress import serve

app = create_app()

if __name__ == '__main__':
    serve(app,host='192.168.9.10',port=8200)
    # serve(app,host='192.168.4.115',port=8200)