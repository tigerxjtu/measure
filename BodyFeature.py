
from BodyClient import body_client
from ui.main import Body,FrontBody,SideBody


class BodyFeature(object):

    def __init__(self):
        self.front_ponits = {}
        self.front_outline = []
        self.fornt_rect = None

        self.side_ponits = {}
        self.side_outline = []
        self.side_rect = None

    def process_front(self,front_file):
        self.front_ponits,self.front_outline,self.front_rect = body_client.process_body(front_file)


    def process_side(self,side_file):
        self.side_ponits, self.side_outline,self.side_rect = body_client.process_body(side_file)

    def front_height(self):
        return self.fornt_rect[3]

    def side_height(self):
        return self.side_rect[3]

    def save(self):
        pass

    def load(self):
        pass
