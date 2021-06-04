#Copyright 2021 Purdue University, University of Virginia.
#Copyright 2018 Purdue University, University of Nebraska--Lincoln.
#Copyright (c) 2016, University of Nebraska NIMBUS LAB  John-Paul Ore jore@cse.unl.edu
#All rights reserved.


class FrameErrorTypes:
    """ DEFINES TYPES OF FRAME ERRORS
        """

    MISSING_FRAME = 20
    MISSING_CHILD_FRAME = 21
    CYCLE_IN_FRAME_TREE = 22
    MULTIPLE_PARENTS_IN_FRAME_TREE = 23   
    MULTIPLE_PUBLISH_SOURCES_FOR_TRANSFORM = 24
    INCORRECT_FRAME_ORDER_IN_TREE = 25
    INVALID_FRAMES = 26
    NON_CONNECTED_FRAMES = 27
    INCORRECT_TRANSFORM = 28
    REVERSED_NAME = 29
    NED_NULL = 30
    SENSOR_NULL = 31

    
    ERR_TYPE_NAMES = [              # MUST BE SAME INDEX AS ERRORS LISTED ABOVE
                      'MISSING_FRAME',
                      'MISSING_CHILD_FRAME',
                      'CYCLE_IN_FRAME_TREE',
                      'MULTIPLE_PARENTS_IN_FRAME_TREE',
                      'MULTIPLE_PUBLISH_SOURCES_FOR_TRANSFORM',
                      'INCORRECT_FRAME_ORDER_IN_TREE',
                      'INVALID_FRAMES',
                      'NON_CONNECTED_FRAMES',
                      'INCORRECT_TRANSFORM',
                      'REVERSED_NAME',
                      'NED_NULL',
                      'SENSOR_NULL'
                     ]


    SEVERITY = [                    # MAPPED DIRECTLY FROM ROS VERBOSITY LEVELS
                'DEBUG',
                'INFO',
                'WARN',
                'ERROR',
                'FATAL',
               ]


    def __init__(self):
        pass


    def get_err_short_discription(self, num):
        return self.ERR_TYPE_NAMES[num-20]



s = '''
MISSING FRAME
MISSIMG CHILD FRAME
CYCLE_IN_FRAME_TREE
MULTIPLE PARENTS IN FRAME TREE
MULTIPLE_PUBLISH_SOURCES_FOR_TRANSFORM
INCORRECT_FRAME_ORDER_IN_TREE
INVALID_FRAMES
NON_CONNECTED_FRAMES
INCORRECT_TRANSFORM
REVERSED_NAME
NED_NULL
SENSOR_NULL
'''

