import logging
import os

class Log(object):

    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=os.path.join(os.getcwd(), 'log.txt'),
                            filemode='a')


    def info(self,information):
        logging.info(information)

    def debug(self,information):
        logging.debug(information)

    def warn(self,infomation):
        logging.warning(infomation)

    def error(self,infomation):
        logging.error(infomation,exc_info = True)


logger=Log()