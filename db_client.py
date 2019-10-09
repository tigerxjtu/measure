import pymysql
from Config import config
import re
import os

class DB_Client(object):

    def __init__(self):
        self.db_name = config.db_name
        self.host = config.db_host
        self.db_user = config.db_user
        self.db_passwd = config.db_passwd

        self.db_conn = None
        # print(self.db_name,self.db_user,self.db_passwd,self.host)


    def get_connection(self):
        if self.db_conn:
            return self.db_conn
        db = pymysql.connect(user=self.db_user, db=self.db_name, passwd=self.db_passwd, host=self.host, use_unicode=True, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
        self.db_conn = db
        return db

    def close_connection(self):
        if self.db_conn:
            try:
                self.db_conn.close()
            except:
                pass
        self.db_conn = None

    def get_queue_records(self):
        sql = 'select id,bbiid from none_feature_queue limit 10'
        records =[]

        with self.get_connection().cursor() as cursor:
            cursor.execute(sql)
            for row in cursor:
                records.append(row)
        return records

    def get_pic_file(self,bbiid):
        sql = 'select bbiid,bpf01 pic from none_body_picfile where bbiid = %(bbiid)s'
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, {'bbiid':bbiid})
            for row in cursor:
                return row['pic']
        return None

    def process_result(self, id, data):
        sql = 'update none_body_feature_data set BFD08=%(neck)s, BH11=%(shoulder)s, BFD13=%(tun)s, BFD11=%(xiong)s, BFD12=%(yao)s where id=%(id)s'
        with self.get_connection().cursor() as cursor:
            data['id']=id
            cursor.execute(sql,data)
            self._del_queue(id)
        self.db_conn.commit()

    def insert_outline_queue(self, id, bbiid, folder, body_id, status):
        sql = 'insert into none_outline_queue values(%(id)s, %(bbiid)s, %(folder)s, %(body_id)s, %(status)s)'
        data = {'id':id, 'bbiid':bbiid, 'folder':folder, 'body_id':body_id, 'status': status}
        with self.get_connection().cursor() as cursor:
            data['id']=id
            cursor.execute(sql,data)
        self.db_conn.commit()

    def delete_outline_queue(self, id):
        sql1 = 'insert ignore into none_outline_queue_log select * from  none_outline_queue where id=%(id)s'
        sql2 = 'delete from none_outline_queue where id = %(id)s'
        with self.get_connection().cursor() as cursor:
            key = {'id': id}
            cursor.execute(sql1, key)
            cursor.execute(sql2, key)
        self.db_conn.commit()

    def _del_queue(self, id):
        sql1 = 'insert ignore into none_feature_queue_log select * from  none_feature_queue where id=%(id)s'
        sql2 = 'delete from none_feature_queue where id = %(id)s'
        with self.get_connection().cursor() as cursor:
            key = {'id': id}
            cursor.execute(sql1, key)
            cursor.execute(sql2, key)

    def del_queue(self,id):
        self._del_queue(id)
        self.db_conn.commit()

    def get_user_info(self, person_id):
        sql = 'SELECT id,bbi03 height, bbi04 weight, bbi02 name FROM none_body_baseinfo WHERE id = %(id)s'
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, {'id':person_id})
            for row in cursor:
                return row['height'],row['weight']
        return None

    def get_outline_queue(self):
        sql = '''select a.id, a.bbiid, a.folder, a.body_id, a.status, b.bbi03 height, b.bbi04 weight, b.bbi02 name 
        from none_outline_queue a, none_body_baseinfo b where a.bbiid=b.id limit 1'''
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql)
            result ={'has_record': False, 'data':{}}
            for row in cursor:
                result['has_record']= True
                row['weight'] = float(row['weight'])
                result['data']=row
            return result

    def del_outline_queue(self, id):
        sql1 = 'insert ignore into none_outline_queue_log select * from  none_outline_queue where id=%(id)s'
        sql2 = 'delete from none_outline_queue where id = %(id)s'
        with self.get_connection().cursor() as cursor:
            key = {'id': id}
            cursor.execute(sql1, key)
            cursor.execute(sql2, key)
        self.db_conn.commit()

    #
    #
    # def insert(self, table_name, data):
    #     for key in data:
    #         data[key] = "'" + str(data[key]) + "'"
    #     key = ','.join(data.keys())
    #     value = ','.join(data.values())
    #     real_sql = "INSERT INTO " + table_name + " (" + key + ") VALUES (" + value + ")"
    #     print(real_sql)
    #     with self.connection.cursor() as cursor:
    #         cursor.execute(real_sql)
    #     self.connection.commit()
    #
    # def search(self,ip):
    #     sql = 'select area,company from ip where start_ip<=%(ip)s and end_ip >= %(ip)s'
    #     data = {'ip': ip}
    #     with self.connection.cursor() as cursor:
    #         cursor.execute(sql, data)
    #         for row in cursor:
    #             print("area:%s, company:%s" % row)

def parse_file(file):
    parts = re.split('[/\\\\]',file)
    folder = parts[-2]
    name = parts[-1][:-5]
    return folder,name

def get_file_name(name,tag,*args):
    folder = args[0]
    feature_path = os.path.join(config.txt_dir,folder)
    pic_path = os.path.join(config.pic_dir,folder)
    return os.path.join(feature_path,'%s%s1.txt'%(name,tag)),os.path.join(pic_path,'%s%s.jpg'%(name,tag))


if __name__ == '__main__':
    db = DB_Client()
    records = db.get_queue_records()
    print(str(records))
    data = {}
    for record in records:
        data['neck']=40.0
        data['shoulder']=42.0
        data['tun']=95.0
        db.process_result(record['id'],data)
    db.del_queue(2026)
    file = db.get_pic_file(1002260)
    print(file)
    if file:
        folder, name = parse_file(file)
        print(parse_file(file))
        print(get_file_name(name,'F',folder))
    print(db.get_user_info(1002260))
    db.close_connection()

    # file = 'public/uploads/201909/U1002260190901115100866F.jpg'
    # file1 = 'public\\uploads\\201909\\U1002260190901115100866F.jpg'
    # parts = re.split('[/\\\\]',file1)
    # print(parts)



