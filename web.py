from flask import Flask, render_template, request
from db_client import DB_Client
import json

db = DB_Client()
app = Flask(__name__)

@app.route('/info')
def info():
    result = db.get_outline_queue()
    print(result)
    db.close_connection()
    return json.dumps(result)

@app.route('/finish/<int:id>')
def finish(id):
    result = {'status':1,'msg':''}
    try:
        db.del_outline_queue(id)
        db.close_connection()
    except Exception as e:
        result['status']=-1
        result['msg']=str(e)
    return json.dumps(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9090)