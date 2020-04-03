
class NoBodyException(Exception):

    def __init__(self, msg='No body found'):
        super(Exception,self).__init__(msg)
    #     self.msg = msg
    #
    # def __str__(self):
    #     return self.msg