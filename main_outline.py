#!/usr/bin/python
# -*- coding: utf-8 -*-
from Config import config

config.train_mode = False
from db_client import DB_Client, parse_file
from file_name import get_file_name
import time
import logging

import json
from model.LinearModel import LinearModel

from ui.outline_export import OutlineTransformer, OutlineTan, OutlineBody
from ui.feature_export import FeatureTan

import multiprocessing
import traceback
import os
from BodyClient import body_client

msg = 'success'

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(os.path.join(os.getcwd(), 'outline_log.txt'))
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def save_bd_feature(name, folder):
    tags = ['F', 'S', 'B']
    for tag in tags:
        _, pic_file = get_file_name(name, tag, folder)
        out_file = os.path.join(config.txt_dir, folder, '%s%s1.json' % (name, tag))
        if os.path.exists(out_file):
            continue
        points, rect = body_client.body_points(pic_file)
        with open(out_file, 'w') as fp:
            json.dump(points, fp)


def save_outline(name, folder):
    tags = ['F', 'S', 'B']
    for tag in tags:
        _, pic_file = get_file_name(name, tag, folder)
        out_file = os.path.join(config.txt_dir, folder, '%s%s2.txt' % (name, tag))
        if os.path.exists(out_file):
            continue
        points, width, height = body_client.body_seg(pic_file)
        pts = [dict(x=p[0], y=p[1]) for p in points]
        points = dict(width=width, height=height, featureXY=pts)
        with open(out_file, 'w') as fp:
            json.dump(points, fp)


def process_outline(db, bbiid):
    global msg
    msg = 'success'
    pic_file = db.get_pic_file(bbiid)
    if not pic_file:
        logger.warnning('body not found: bbiid=' + str(bbiid))
        msg = 'body not found'
        return 5, [], [], []
    folder, body_id = parse_file(pic_file)
    save_bd_feature(body_id, folder)
    save_outline(body_id, folder)
    return outline_tan(folder, body_id, bbiid)


def outline_tan(folder, body_id, person_id):
    global msg
    args = {'folder': folder, 'person_id': person_id}
    l_model = LinearModel(**args)
    fbody = l_model.get_body(body_id, 'F')
    sbody = l_model.get_body(body_id, 'S')
    bbody = l_model.get_body(body_id, 'B')
    b_outline_body = OutlineBody(bbody)

    f_bd_features = fbody.bdfeatureXY
    s_bd_features = sbody.bdfeatureXY
    b_bd_features = bbody.bdfeatureXY
    # fbody.load_export_features()
    # sbody.load_export_features()
    flag = 4
    front = []
    side = []
    back = []
    steps = 1
    try:
        outline_exp = OutlineTan(fbody, sbody)
        front_points = outline_exp.front_points()
        f_w = fbody.img_w
        f_h = fbody.img_h
        f_points = [dict(x=p[0], y=p[1]) for p in front_points]
        front = dict(width=f_w, height=f_h, featureXY=f_points)

        steps = 2
        side_points = outline_exp.side_points()
        s_w = sbody.img_w
        s_h = sbody.img_h
        s_points = [dict(x=p[0], y=p[1]) for p in side_points]
        side = dict(width=s_w, height=s_h, featureXY=s_points)
        steps = 3

        back_points = b_outline_body.outline_points()
        b_w = bbody.img_w
        b_h = bbody.img_h
        b_points = [dict(x=p[0], y=p[1]) for p in back_points]
        back = dict(width=b_w, height=b_h, featureXY=b_points)
    except Exception as e:
        logger.error('outline export fail: body_id=%s, person_id=%s' % (body_id, person_id))
        logger.error(e)
        flag = 5
        msg = traceback.format_exc()
    return flag, front, side, back, f_bd_features, s_bd_features, b_bd_features


def main():
    global msg
    db = DB_Client()
    logger.info('program started:------------------------------------')
    sleep_time = 2
    while (True):
        try:
            record = db.get_new_outline()
            # logger.info('get %d records'%len(records))
            data = {}
            processed = False
            if record:
                processed = True
                logger.info('processing record:' + str(record))
                exp_status = False
                try:
                    result, front, side, back, f_bd_features, s_bd_features, b_bd_features = process_outline(db, record[
                        'bbiid'])
                    logger.info('processing record %s, result:%s' % (record, result))
                    if result == 4:
                        db.update_new_outline(record['bbiid'], json.dumps(front), json.dumps(side), json.dumps(back),
                                              json.dumps(f_bd_features), json.dumps(s_bd_features),
                                              json.dumps(b_bd_features))
                    db.update_new_outline_result(record['bbiid'], result, msg)
                    sleep_time = 2
                except Exception as e:
                    logger.error('record process failed: record:%s, exception:%s' % (record, traceback.format_exc()))
                    msg = traceback.format_exc()
                    retries = int(record['result'])
                    if retries >= 3:
                        db.update_new_outline_result(record['bbiid'], 5,
                                                     'retries:%d, exception trace:%s' % (retries, msg))
                    else:
                        db.update_new_outline_result(record['bbiid'], retries + 1,
                                                     'retries:%d, exception trace:%s' % (retries, msg))
                    time.sleep(sleep_time)
                    if sleep_time < 20:
                        sleep_time = 2 * sleep_time
            if not processed:
                db.close_connection()
                time.sleep(2)
        except Exception as e:
            logger.error(e)
            time.sleep(20)


if __name__ == '__main__':
    # multiprocessing.freeze_support()
    main()
