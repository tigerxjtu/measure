from flask import Flask, render_template, request
from db_client import DB_Client
import json
from main import export_outline_tan

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

@app.route('/get_records')
def get_records():
    skip = int(request.values.get('skip'))
    num = int(request.values.get('num'))
    # print(skip,num)
    result = db.get_recent_outlines(skip,num)
    print(result)
    db.close_connection()
    return json.dumps(result)

@app.route('/outline/update/<int:bbiid>')
def update_outline(bbiid):
    record = db.get_outline_log_record(bbiid)
    flag = export_outline_tan(record['folder'],record['body_id'],record['bbiid'])
    db.update_outline_status(record['id'],flag)
    db.close_connection()
    return json.dumps({'status':flag})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9090)