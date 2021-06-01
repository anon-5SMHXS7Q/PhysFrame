from frame_error_types import FrameErrorTypes


class FrameError:

    def __init__(self):
        self.ERROR_TYPE = None 
        self.SEVERITY = ''
        self.is_warning = False
        self.var_name = ''
        self.file_name = '' # OR [] FOR TREE RELATED ERRORS 
        self.frame_name = ''
        self.values = None
        self.linenr = 0


    def get_error_desc(self):
        return FrameErrorTypes().get_err_short_discription(self.ERROR_TYPE)

