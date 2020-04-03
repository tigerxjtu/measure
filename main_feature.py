#!/usr/bin/python
# -*- coding: utf-8 -*-
from Config import config
config.train_mode = False
from db_client import DB_Client,parse_file
from file_name import get_file_name
import time
import logging
from BodyClient import body_client
import os

import json
from model.LinearModel import  LinearModel

from ui.feature_export import FeatureTan

# import multiprocessing
import traceback


msg='success'

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler(os.path.join(os.getcwd(), 'feature_log.txt'))
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def save_bd_feature(name,folder):
    tags = ['F', 'S', 'B']
    for tag in tags:
        _, pic_file = get_file_name(name, tag, folder)
        out_file = os.path.join(config.txt_dir, folder, '%s%s1.json' % (name, tag))
        if os.path.exists(out_file):
            continue
        points, rect = body_client.body_points(pic_file)
        with open(out_file, 'w') as fp:
            json.dump(points, fp)

def process_feature(db,bbiid):
    global msg
    msg = 'success'
    pic_file = db.get_pic_file(bbiid)
    if not pic_file:
        logger.warning('body not found: bbiid='+str(bbiid))
        msg='body not found'
        return 5,{}
    folder,body_id = parse_file(pic_file)
    save_bd_feature(body_id,folder)
    return feature_tan(folder, body_id, bbiid)


def feature_tan(folder, body_id, person_id):
    global msg
    args = {'folder': folder, 'person_id': person_id}
    l_model = LinearModel(**args)
    fbody = l_model.get_body(body_id,'F')
    sbody = l_model.get_body(body_id,'S')
    fbody.load_export_features()
    sbody.load_export_features()
    flag = 4
    features={}
    try:
        exporter = FeatureTan(fbody, sbody)
        features=exporter.export_features()
    except Exception as e:
        logger.error('feature export fail: body_id=%s, person_id=%s' % (body_id, person_id))
        logger.error(e)
        flag = 5
        msg = traceback.format_exc()
    return flag,features

def main():
    global msg
    db = DB_Client()
    logger.info('program started:------------------------------------')
    while (True):
        try:
            record = db.get_new_feature()
            # logger.info('get %d records'%len(records))
            processed = False
            if record:
                processed = True
                logger.info('processing record:' + str(record))
                exp_status = False
                try:
                    result,features = process_feature(db, record['bbiid'])
                    logger.info('processing record %s, result:%s'% (record, result))
                    if result==4:
                        db.update_new_feature(record['bbiid'],features)
                    db.update_new_feature_result(record['bbiid'],result,msg)
                except Exception as e:
                    logger.error('record process failed: record:%s, exceptin:%s' % (record, traceback.format_exc()))
                    msg = traceback.format_exc()
                    db.update_new_feature_result(record['bbiid'], 5, msg)

            if not processed:
                db.close_connection()
                time.sleep(2)
        except Exception as e:
            logger.error(e)
            time.sleep(2)


if __name__ == '__main__':
    # multiprocessing.freeze_support()
    main()