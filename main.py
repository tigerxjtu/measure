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
from model.LinearModel import  LinearModel
from model.Neck3sideModel import Neck3sideModel
from model.ShoulderModel import ShoulderModel
from model.Hip3sideModel import Hip3sideModel
from model.Xiong3sideModel import Xiong3sideModel
from model.Yao3sideModel import Yao3sideModel

from ui.outline_export import OutlineTransformer,OutlineTan
from ui.feature_export import FeatureTan

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
    model = Xiong3sideModel(name, height, **args)
    xiong = model.predict()
    model = Yao3sideModel(name, height, **args)
    yao = model.predict()
    return neck,shoulder,tun,xiong,yao

def process_record(db,bbiid):
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
    neck,shoulder,tun,xiong,yao = process_body(name,folder,bbiid,height)
    return {'neck':round(neck,2), 'shoulder':round(shoulder,2), 'tun':round(tun,2),
            'xiong':round(xiong,2),'yao':round(yao,2)},folder,name

def export_outline_tan(folder, body_id, person_id):
    args = {'folder': folder, 'person_id': person_id}
    l_model = LinearModel(**args)
    fbody = l_model.get_body(body_id,'F')
    sbody = l_model.get_body(body_id,'S')
    fbody.load_export_features()
    sbody.load_export_features()
    flag = 0
    try:
        base_path = os.path.join(config.tan_dir,folder)
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        outline_exp = OutlineTan(fbody, sbody)
        file_path = os.path.join(base_path, '%s_FC.txt' % (body_id))
        outline_exp.export_front(file_path)
        file_path = os.path.join(base_path, '%s_SC.txt' % (body_id))
        outline_exp.export_side(file_path)
    except Exception as e:
        logger.error('outline export fail: body_id=%s, person_id=%s'%(body_id,person_id))
        logger.error(e)
        flag -= 1
    try:
        exporter = FeatureTan(fbody, sbody)
        # sbody.features['f_neck_up_L'],_=exporter.map_front2side_feature('f_neck_up_L')
        file_path = os.path.join(base_path, '%s_FL.txt' % (body_id))
        exporter.write_file(file_path)
    except Exception as e:
        logger.error('feature export fail: body_id=%s, person_id=%s' % (body_id, person_id))
        logger.error(e)
        flag -= 2
    return flag




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
                exp_status = False
                try:
                    data,folder,body_id=process_record(db,record['bbiid'])
                    logger.info('processing result, input:%s, output:%s '%(record,data))
                    if data:
                        db.process_result(record['id'], data)
                        exp_status = export_outline_tan(folder, body_id, record['bbiid'])
                        db.insert_outline_queue(record['id'],record['bbiid'],folder,body_id,exp_status)
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