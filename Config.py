import json

class Config(object):

    def __init__(self):
        # self.httpInfo = 'http://47.100.216.92/admin/app/index.html'
        # self.httpInfo = 'http://47.100.216.92/'
        self.httpInfo = 'http://127.0.0.1:9090/'
        # self.download_base_pic_url = 'http://47.100.216.92/uploads'
        # self.download_base_tan_url = 'http://47.100.216.92/tan'
        self.download_base_pic_url = 'http://127.0.0.1/uploads'
        self.download_base_tan_url = 'http://127.0.0.1/tan'

        self.model_path = r'C:\projects\python\measure\ui\data'
        self.tan_dir = r'C:\tmp\tan'

        # self.model_path = r'C:\projects\python\measure\ui\data'
        # self.pic_dir = r'C:\tmp\pics'
        # self.txt_dir = r'C:\tmp\txtdata'
        # self.tan_dir = r'C:\tmp\tan'
        # self.result_dir = r'C:\projects\python\measure\ui\data\result'
        # self.data_dir = r'C:\projects\python\measure\ui\data'

        # self.model_path = r'C:\projects\python\measure\ui\data'
        # self.tan_dir = r'C:\tmp\tan'
        # self.pic_dir = r'C:\projects\python\data\measure\9.30\pics'
        # self.txt_dir = r'C:\projects\python\data\measure\9.30\txtdata'
        # self.result_dir = r'C:\projects\python\data\measure\9.30\result'
        # self.data_dir = r'C:\projects\python\data\measure\9.30'

        # self.model_path = r'C:\projects\python\measure\ui\data'
        # self.pic_dir = r'C:\projects\python\data\measure\10.10\pics'
        # self.txt_dir = r'C:\projects\python\data\measure\10.10\txtdata'
        # self.tan_dir = r'C:\tmp\tan'
        # self.result_dir = r'C:\projects\python\data\measure\10.10\result'
        # self.data_dir = r'C:\projects\python\data\measure\10.10'

        # self.model_path = r'C:\projects\python\measure\ui\data'
        # self.pic_dir = r'C:\projects\python\data\measure\10.24\pics'
        # self.txt_dir = r'C:\projects\python\data\measure\10.24\txtdata'
        # self.tan_dir = r'C:\tmp\tan'
        # self.result_dir = r'C:\projects\python\data\measure\10.24\result'
        # self.data_dir = r'C:\projects\python\data\measure\10.24'

        # self.model_path = r'C:\projects\python\measure\ui\data'
        # self.pic_dir = r'C:\projects\python\data\measure\10.25\pics'
        # self.txt_dir = r'C:\projects\python\data\measure\10.25\txtdata'
        # self.tan_dir = r'C:\tmp\tan'
        # self.result_dir = r'C:\projects\python\data\measure\10.25\result'
        # self.data_dir = r'C:\projects\python\data\measure\10.25'

        # self.model_path = r'C:\projects\python\measure\ui\data'
        # self.pic_dir = r'C:\projects\python\data\measure\11\pics'
        # self.txt_dir = r'C:\projects\python\data\measure\11\txtdata'
        # self.tan_dir = r'C:\tmp\tan'
        # self.result_dir = r'C:\projects\python\data\measure\11\result'
        # self.data_dir = r'C:\projects\python\data\measure\11'



        # self.pic_dir = r'C:\projects\python\data\measure\202001\pics'
        # self.txt_dir = r'C:\projects\python\data\measure\202001\txtdata'
        # self.result_dir = r'C:\projects\python\data\measure\202001\result'
        # self.data_dir = r'C:\projects\python\data\measure\202001'

        # self.pic_dir = r'C:\projects\python\data\measure\202003\pics'
        # self.txt_dir = r'C:\projects\python\data\measure\202003\txtdata'
        # self.result_dir = r'C:\projects\python\data\measure\202003\result'
        # self.data_dir = r'C:\projects\python\data\measure\202003'

        self.pic_dir = r'C:\projects\python\data\measure\202005\pics'
        self.txt_dir = r'C:\projects\python\data\measure\202005\txtdata'
        self.result_dir = r'C:\projects\python\data\measure\202005\result'
        self.data_dir = r'C:\projects\python\data\measure\202005'

        # self.pic_dir = r'C:\projects\python\tan_client\pics'
        # self.txt_dir = r'C:\projects\python\tan_client\txtdata'
        # self.result_dir = r'C:\projects\python\tan_client\result'
        # self.data_dir = r'C:\projects\python\data\measure\202003'

        # self.pic_dir = r'C:\projects\python\data\measure\pics\202001'
        # self.txt_dir = r'C:\projects\python\data\measure\txtdata\202001'
        # self.result_dir = r'C:\projects\python\data\measure\result\202001'
        # self.data_dir = r'C:\projects\python\data\measure\202001'

        # self.pic_dir = r'C:\projects\python\data\measure\pics\201911'
        # self.txt_dir = r'C:\projects\python\data\measure\txtdata\201911'
        # self.result_dir = r'C:\projects\python\data\measure\result\201911'
        # self.data_dir = r'C:\projects\python\data\measure\201911'

        # self.db_host = '127.0.0.1'
        # self.db_name = 'body1015'
        # self.db_user = 'root'
        # self.db_passwd = 'pass'

        self.db_host = 'rm-bp17347qbxt77k52w4o.mysql.rds.aliyuncs.com'
        self.db_name = 'nonecms'
        self.db_user = 'qinghong'
        self.db_passwd = 'qinghong@20191212'

        self.train_mode = True
        # self.read()


    def build_dict(self):
        conf = {}
        conf['httpInfo']= self.httpInfo
        conf['download_base_pic_url'] = self.download_base_pic_url
        conf['download_base_tan_url'] = self.download_base_tan_url

        conf['model_path'] = self.model_path
        conf['pic_dir'] = self.pic_dir
        conf['txt_dir'] = self.txt_dir
        conf['tan_dir'] = self.tan_dir
        conf['result_dir'] = self.result_dir

        conf['db_user']=self.db_user
        conf['db_name']=self.db_name
        conf['db_host']=self.db_host
        conf['db_passwd']=self.db_passwd

        conf['train_mode']=self.train_mode
        return conf

    def read(self,file_path='config.json'):
        try:
            with open(file_path, 'r') as f:
                conf = json.loads(f.read())
                self.httpInfo = conf['httpInfo']
                self.download_base_pic_url = conf['download_base_pic_url']
                self.download_base_tan_url = conf['download_base_tan_url']

                self.model_path = conf['model_path']
                self.pic_dir = conf['pic_dir']
                self.txt_dir = conf['txt_dir']
                self.tan_dir = conf['tan_dir']

                self.result_dir = conf['result_dir']

                self.db_user = conf['db_user']
                self.db_name = conf['db_name']
                self.db_host = conf['db_host']
                self.db_passwd = conf['db_passwd']

                self.train_mode = conf['train_mode']
        except Exception as e:
            print(e)
            pass

    def save(self,file_path='config.json'):
        conf = self.build_dict()
        with open(file_path, 'w') as f:
            json.dump(conf,f)


config = Config()
# config.read()

if __name__ == '__main__':
    config.save()
