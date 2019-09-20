#!/usr/bin/python
# -*- coding: utf-8 -*-
from Config import config
config.train_mode = False
from db_client import DB_Client,parse_file
from file_name import get_file_name
import time
from logger import logger
from BodyClient import body_client
import os

import json
from model.Neck3sideModel import Neck3sideModel
from model.ShoulderModel import ShoulderModel
from model.Hip3sideModel import Hip3sideModel

def save_feature(name,folder):
    tags = ['F', 'S', 'B']
    for tag in tags:
        _, pic_file = get_file_name(name, tag, folder)
        out_file = os.path.join(config.txt_dir, folder, '%s%s1.json' % (name, tag))
        if os.path.exists(out_file):
            continue
        points, rect = body_client.body_points(pic_file)
        with open(out_file, 'w') as fp:
            json.dump(points, fp)

def process_body(name,folder,bbiid,height):
    save_feature(name,folder)
    args = {'folder':folder, 'person_id':bbiid}
    model = Neck3sideModel(name, height, **args)
    neck = model.predict()
    model = ShoulderModel(name, height, **args)
    shoulder = model.predict()
    model = Hip3sideModel(name, height, **args)
    tun = model.predict()
    return neck,shoulder,tun

def process_record(db,id,bbiid):
    pic_file = db.get_pic_file(bbiid)
    if not pic_file:
        logger.warn('body not found: bbiid='+bbiid)
        return None
    folder,name = parse_file(pic_file)
    result = db.get_user_info(bbiid)
    if not result:
        logger.warn('user not found: id=' + bbiid)
        return None
    height = result[0]
    neck,shoulder,tun = process_body(name,folder,bbiid,height)
    return {'neck':round(neck,2), 'shoulder':round(shoulder,2), 'tun':round(tun,2)}

if __name__ == '__main__':
    db=DB_Client()
    logger.info('program started:------------------------------------')
    while(True):
        try:
            records = db.get_queue_records()
            # logger.info('get %d records'%len(records))
            data = {}
            processed = False
            for record in records:
                processed = True
                logger.info('processing record:'+str(record))
                try:
                    data=process_record(db,record['id'],record['bbiid'])
                    logger.info('processing result, input:%s, output:%s '%(record,data))
                    if data:
                        db.process_result(record['id'], data)
                    else:
                        db.del_queue(record['id'])
                except Exception as e:
                    logger.error('record process failed: record:%s, exceptin:%s'%(record,str(e)))
                    db.del_queue(record['id'])
            if not processed:
                db.close_connection()
                time.sleep(2)
        except Exception as e:
            logger.error('exception occured:' + str(e))
            time.sleep(2)