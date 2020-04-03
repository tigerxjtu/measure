from ui.main import Body,FrontBody,SideBody
# from common import *
from train_data import *
from ui.outline_export import OutlineTan
from model.LinearModel import LinearModel

def get_front_side_points(name):
    body_id = name
    l_model = LinearModel()
    fbody = l_model.get_body(body_id, 'F')
    sbody = l_model.get_body(body_id, 'S')
    fbody.load_export_features()
    sbody.load_export_features()
    outline_exp = OutlineTan(fbody, sbody)
    return outline_exp.front_points(),outline_exp.side_points()

if __name__ == '__main__':
    name = names[2]
    # name = 'U100265219110914553552'
    name='U1003017200310155454508'
    print(name)
    # U100221919090109361146
    body_id = name
    front_body = FrontBody(body_id)
    side_body = SideBody(body_id)
    #
    front_body.process_img()
    side_body.process_img()
    #
    # file_path = os.path.join(path3, '%s%s.json' % (body_id, front_body.tag))
    # with open(file_path, 'w') as fp:
    #     print(front_body.get_body_features())
    #     str = json.dumps(front_body.get_body_features())
    #     fp.write(str)

    # l_model = LinearModel()
    # fbody = l_model.get_body(body_id, 'F')
    # sbody = l_model.get_body(body_id, 'S')
    # fbody.load_export_features()
    # sbody.load_export_features()
    # flag = 0
    # base_path = config.result_dir
    # if not os.path.exists(base_path):
    #     os.mkdir(base_path)

    outline_exp = OutlineTan(front_body, side_body)
    file_path = os.path.join(path3, '%s_FC.txt' % (body_id))
    outline_exp.export_front(file_path)


    # file_path = os.path.join(path3, '%s_SC.txt' % (body_id))
    # outline_exp.export_side(file_path)

    # results = []
    # for name in names:
    #     try:
    #         fpoints,spoints = get_front_side_points(name)
    #         # print(len(fpoints),len(spoints))
    #         if len(fpoints)<3000 or len(spoints)<1500:
    #             results.append((name,len(fpoints),len(spoints)))
    #     except Exception as e:
    #         print(e)
    #         results.append((name, -1, -1))
    #         # raise e
    # for record in results:
    #     print(record)