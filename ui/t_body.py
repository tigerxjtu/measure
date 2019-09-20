from ui.main import Body,FrontBody,SideBody
from common import *

if __name__ == '__main__':
    print(names[2])
    # U100221919090109361146
    body_id = names[2]
    front_body = FrontBody(body_id)
    side_body = SideBody(body_id)

    front_body.process_img()
    side_body.process_img()

    file_path = os.path.join(path3, '%s%s.json' % (body_id, front_body.tag))
    with open(file_path, 'w') as fp:
        print(front_body.get_body_features())
        str = json.dumps(front_body.get_body_features())
        fp.write(str)