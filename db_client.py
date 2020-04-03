import pymysql
from Config import config
import re
import os

#数据库访问客户端
class DB_Client(object):

    def __init__(self):
        self.db_name = config.db_name
        self.host = config.db_host
        self.db_user = config.db_user
        self.db_passwd = config.db_passwd

        self.db_conn = None
        # print(self.db_name,self.db_user,self.db_passwd,self.host)

    #获得数据库连接
    def get_connection(self):
        if self.db_conn:
            return self.db_conn
        db = pymysql.connect(user=self.db_user, db=self.db_name, passwd=self.db_passwd, host=self.host, use_unicode=True, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
        self.db_conn = db
        return db

    #关闭数据库连接
    def close_connection(self):
        if self.db_conn:
            try:
                self.db_conn.close()
            except:
                pass
        self.db_conn = None

    #读取詹新林程序处理后的待处理队列记录
    def get_queue_records(self):
        sql = 'select id,bbiid from none_feature_queue limit 10'
        records =[]

        with self.get_connection().cursor() as cursor:
            cursor.execute(sql)
            for row in cursor:
                records.append(row)
        return records

    def commit(self):
        if self.db_conn:
            self.db_conn.commit()

    #根据人体id读取对应的图片路径，供后续提取图片目录和图片id
    def get_pic_file(self,bbiid):
        sql = 'select bbiid,bpf01 pic from none_body_picfile where bbiid = %(bbiid)s'
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, {'bbiid':bbiid})
            for row in cursor:
                return row['pic']
        return None

    #保存计算尺寸
    def process_result(self, id, data):
        sql = 'update none_body_feature_data set BFD08=%(neck)s, BH11=%(shoulder)s, BFD13=%(tun)s, BFD11=%(xiong)s, BFD12=%(yao)s where id=%(id)s'
        with self.get_connection().cursor() as cursor:
            data['id']=id
            cursor.execute(sql,data)
            self._del_queue(id)
        self.db_conn.commit()

    #生成轮廓处理队列的记录
    def insert_outline_queue(self, id, bbiid, folder, body_id, status):
        sql = 'insert into none_outline_queue(id,bbiid,folder,body_id,STATUS) values(%(id)s, %(bbiid)s, %(folder)s, %(body_id)s, %(status)s)'
        data = {'id':id, 'bbiid':bbiid, 'folder':folder, 'body_id':body_id, 'status': status}
        with self.get_connection().cursor() as cursor:
            data['id']=id
            cursor.execute(sql,data)
        self.db_conn.commit()

    #删除轮廓处理队列的记录，并将处理结果状态保存到none_outline_queue_log表
    def delete_outline_queue(self, id):
        sql1 = 'insert ignore into none_outline_queue_log select * from  none_outline_queue where id=%(id)s'
        sql2 = 'delete from none_outline_queue where id = %(id)s'
        with self.get_connection().cursor() as cursor:
            key = {'id': id}
            cursor.execute(sql1, key)
            cursor.execute(sql2, key)
        self.db_conn.commit()

    #删除待处理队列的记录，并将记录保存到none_feature_queue_log表（不做事务控制）
    def _del_queue(self, id):
        sql1 = 'insert ignore into none_feature_queue_log select * from  none_feature_queue where id=%(id)s'
        sql2 = 'delete from none_feature_queue where id = %(id)s'
        with self.get_connection().cursor() as cursor:
            key = {'id': id}
            cursor.execute(sql1, key)
            cursor.execute(sql2, key)

    def fail_queue(self,id,msg):
        # insert into demo(a,b,c,d,e,f) values(1,1,1,2,2,2) ON DUPLICATE KEY UPDATE a=2,b=2,c=3,d=4,e=5,f=6;
        sql = 'insert into none_feature_queue_fail(id,redo,update_time,msg) values(%(id)s,0,now(),%(msg)s) ON DUPLICATE KEY UPDATE redo=redo+1,update_time=now(),msg=%(msg)s'
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, {'id': id,'msg':msg})
        self.db_conn.commit()


    # 删除待处理队列的记录，并将记录保存到none_feature_queue_log表（做事务控制）
    def del_queue(self,id):
        self._del_queue(id)
        self.db_conn.commit()

    #根据人体id获取人体用户信息
    def get_user_info(self, person_id):
        sql = 'SELECT id,bbi03 height, bbi04 weight, bbi02 name FROM none_body_baseinfo WHERE id = %(id)s'
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, {'id':person_id})
            for row in cursor:
                return row['height'],row['weight']
        return None

#读取轮廓待处理队列，前端轮询用
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

#将轮廓处理队列记录移除到none_outline_queue_log表
    def del_outline_queue(self, id):
        sql1 = 'insert ignore into none_outline_queue_log select * from  none_outline_queue where id=%(id)s'
        sql2 = 'delete from none_outline_queue where id = %(id)s'
        with self.get_connection().cursor() as cursor:
            key = {'id': id}
            cursor.execute(sql1, key)
            cursor.execute(sql2, key)
        self.db_conn.commit()

    #轮廓下载信息接口
    def get_recent_outlines(self,skip,num):
        sql =  '''select a.id, a.bbiid, a.folder, a.body_id, a.status, b.bbi03 height, b.bbi04 weight, b.bbi02 name 
                from none_outline_queue_log a, none_body_baseinfo b where a.bbiid=b.id order by a.id desc limit %(skip)s,%(num)s'''
        params = {"skip":skip, "num":min(num,100)}
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql,params)
            result = []
            for row in cursor:
                row['weight'] = float(row['weight'])
                result.append(row)
            return result

    #根据id查找轮廓下载信息接口
    def get_bbiid_outlines(self,bbiid):
        sql =  '''select -1 as id, b.id as bbiid, -1 as status, b.bbi03 height, b.bbi04 weight, b.bbi02 name 
                from none_body_baseinfo b where b.id=%(bbiid)s'''
        params = {"bbiid":bbiid}
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql,params)
            result = []
            for row in cursor:
                row['weight'] = float(row['weight'])
                result.append(row)
            return result

    #根据人体id查询轮廓处理记录
    def get_outline_log_record(self, bbiid):
        sql = 'select * from none_outline_queue_log where bbiid=%(bbiid)s'
        params = {'bbiid':bbiid}
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql,params)
            for row in cursor:
                return row
            return None

    #保存轮廓记录处理状态
    def update_outline_status(self,id,status):
        sql = 'update none_outline_queue_log set status=%(status)s where id=%(id)s'
        params = {'id':id, 'status':status}
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql,params)
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

    def insert_new_outline(self, bbiid):
        sql = 'insert ignore into new_body_outline(parentid,createtime,status,result,redo) values(%(bbiid)s,now(),0,0,3)'
        params = {'bbiid': bbiid}
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, params)
        # self.db_conn.commit()

    def get_new_outline(self):
        record=self._get_new_outline()
        # if record:
        #     return record
        # return self._get_redo_outline()
        return record

    def _get_new_outline(self):
        #sql='select id,parentid as bbiid,result,redo from new_body_outline where status=0 and result=0 limit 1'# for update'
        sql = 'select id,parentid as bbiid,result,redo from new_body_outline where status=0 and result<redo order by result limit 1'  # for update'
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql)
            for row in cursor:
                id=row['id']
                self._upadte_outline_status(id)
                return row
            return None

    def _get_redo_outline(self):
        sql = 'select id,parentid as bbiid,result,redo from new_body_outline where status=0 and result<redo and result>0 limit 1'# for update'
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql)
            for row in cursor:
                id = row['id']
                self._upadte_outline_status(id)
                return row
            return None

    def _upadte_outline_status(self,id):
        sql='update new_body_outline set starttime=now(),status=1,result=result+1 where id=%(id)s'
        params = {'id': id}
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, params)
        self.db_conn.commit()

    def update_new_outline(self,bbiid,front,side,back,bd01,bd02,bd03):
        sql = 'update new_body_outline set lk01=%(front)s, lk02=%(side)s, lk03=%(back)s,bd01=%(bd01)s,bd02=%(bd02)s,bd03=%(bd03)s where parentid=%(bbiid)s'
        params = {'bbiid': bbiid, 'front': front, 'side': side, 'back':back,'bd01':bd01,'bd02':bd02,'bd03':bd03}
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, params)

    def update_new_outline_result(self,bbiid,status,msg):
        sql = 'update new_body_outline set status=0, endtime=now(),result=%(status)s, message=%(msg)s where parentid=%(bbiid)s'
        params = {'bbiid': bbiid,'status':status,'msg':msg }
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, params)
        self.db_conn.commit()


    def insert_new_feature(self,bbiid):
        sql = 'insert ignore into new_body_feature_point(parentid,createtime,status,result,redo) values(%(bbiid)s,now(),0,0,3)'
        params = {'bbiid': bbiid}
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, params)
        # self.db_conn.commit()

    def get_new_feature(self):
        sql='select id,parentid as bbiid from new_body_feature_point where status=0 and result<redo limit 1'# for update'
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql)
            for row in cursor:
                id=row['id']
                self._upadte_feature_status(id)
                return row
            return None

    def _upadte_feature_status(self,id):
        sql='update new_body_feature_point set starttime=now(),status=1,result=result+1 where id=%(id)s'
        params = {'id': id}
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, params)
        self.db_conn.commit()

    def update_new_feature(self,bbiid,data_cols):
        key_cols = {'parentid':bbiid}
        sql = self._build_update_sql('new_body_feature_point',data_cols,key_cols)
        params = {**data_cols,**key_cols}
        # print(sql)
        # print(params)
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, params)

    def update_new_feature_result(self,bbiid,status,msg):
        sql = 'update new_body_feature_point set status=0, endtime=now(),result=%(status)s, message=%(msg)s where parentid=%(bbiid)s'
        params = {'bbiid': bbiid,'status':status,'msg':msg }
        # print(sql)
        # print(params)
        with self.get_connection().cursor() as cursor:
            cursor.execute(sql, params)
        self.db_conn.commit()

    def _build_update_sql(self,table_name, update_dict, keys_dict):
        return 'update %s set %s where %s'%(table_name, self._join_cols(update_dict), self._join_cols(keys_dict))

    def _join_cols(self,update_dict):
        cols_expr = ['%s=%%(%s)s' % (k, k) for k in update_dict.keys()]
        return ','.join(cols_expr)

def parse_file(file):
    parts = re.split('[/\\\\]',file)
    folder = parts[-2] #相对目录信息，如201910
    name = parts[-1][:-5]#根据命名规则去掉文件名的后5位得到图片id
    return folder,name

#根据图片id，标识（F、S、B），目录得到图片完整路径
def get_file_name(name,tag,*args):
    folder = args[0]
    feature_path = os.path.join(config.txt_dir,folder)
    pic_path = os.path.join(config.pic_dir,folder)
    return os.path.join(feature_path,'%s%s1.txt'%(name,tag)),os.path.join(pic_path,'%s%s.jpg'%(name,tag))


if __name__ == '__main__':
    db = DB_Client()
    # records = db.get_queue_records()
    # print(str(records))
    # data = {}
    # for record in records:
    #     data['neck']=40.0
    #     data['shoulder']=42.0
    #     data['tun']=95.0
    #     db.process_result(record['id'],data)
    # db.del_queue(2026)
    # file = db.get_pic_file(1002260)
    # print(file)
    # if file:
    #     folder, name = parse_file(file)
    #     print(parse_file(file))
    #     print(get_file_name(name,'F',folder))
    # print(db.get_user_info(1002260))

    # bbiid=1002977
    # # db.insert_new_outline(bbiid)
    # db.insert_new_feature(bbiid)
    # db.commit()

    # bbiid=1000177
    # print(db.get_user_info(bbiid))
    # print(db.get_pic_file(bbiid))
    # db.insert_new_feature(bbiid)
    # db.commit()
    db.fail_queue(2,'success')

    db.close_connection()

    # file = 'public/uploads/201909/U1002260190901115100866F.jpg'
    # file1 = 'public\\uploads\\201909\\U1002260190901115100866F.jpg'
    # parts = re.split('[/\\\\]',file1)
    # print(parts)



