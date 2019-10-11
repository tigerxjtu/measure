import json

class Config(object):

    def __init__(self):
        # self.httpInfo = 'http://47.100.216.92/admin/app/index.html'
        self.httpInfo = 'http://47.100.216.92/'
        self.download_base_pic_url = 'http://47.100.216.92/uploads'
        self.download_base_tan_url = 'http://47.100.216.92/tan'

        self.model_path = r'/data/post'
        self.pic_dir = r'/data/wwwroot/public/uploads'
        self.txt_dir = r'/data/wwwroot/txtdata'
        self.tan_dir = r'/data/wwwroot/public/tan'

        self.result_dir = r'/data/post/result'
        self.db_host = '127.0.0.1'
        self.db_name = 'nonecms'
        self.db_user = 'aosoft'
        self.db_passwd = 'pass'

        self.train_mode = False
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
