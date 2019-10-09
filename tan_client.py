
from Config import config
import requests
from remote.download import *
from logger import Log
import json
import time

log = Log('tan.txt')

# def get(url):
#     response = requests.get(url)
#     res = response.content.decode('unicode_escape')
#     return json.load(res)

def get(url,data=None):
    if data:
        response = requests.get(url, data=data)
    else:
        response = requests.get(url)
    if not response.ok:
        raise Exception('http error：'+ url + response.status_code )
    res = response.content.decode('unicode_escape')
    return json.loads(res)



if __name__ == '__main__':
    log.info('program started:------------------------------------')
    info_url = config.httpInfo + 'info'
    finish_url = config.httpInfo + 'finish'
    while(True):
        person_info = {}
        # body_info = {}
        try:
            result = get(info_url)
            if result['has_record']==1:
                log.info('process record: %s'%result['data'])
                record_id = result['data']['id']
                person_info['person_id']=result['data']['bbiid']
                person_info['height']=result['data']['height']
                person_info['weight'] = result['data']['weight']
                person_info['name'] = result['data']['name']
                person_info['body_id'] = result['data']['body_id']
                save_person_info(result['data']['folder'],person_info)
                download_files(result['data']['folder'],result['data']['body_id'],result['data']['status'])

                result = get('%s/%d'%(finish_url,record_id))
                print(result)
            else:
                time.sleep(2)
        except Exception as e:
            log.error('exception occured:' + str(e))
            time.sleep(2)


