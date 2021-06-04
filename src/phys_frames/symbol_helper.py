#Copyright (c) 2016, University of Nebraska NIMBUS LAB  John-Paul Ore jore@cse.unl.edu
#Copyright 2018 Purdue University, University of Nebraska--Lincoln.
#Copyright 2021 Purdue University, University of Virginia.
#All rights reserved.


def get_body(frame_id):
    if any(substr in frame_id for substr in ['sensor', 'laser', 'lidar', 'radar', 'scan', 'sick', 'velodyne']):
        return 'sensor'
    elif any(substr in frame_id for substr in ['camera', 'cam', 'openni', 'kinect', 'pylon']):
        return 'camera'
    elif any(substr in frame_id for substr in ['base', 'robot', 'vehicle']):
        return 'robot'
    elif 'wrist' in frame_id:
        return 'wrist'
    elif any(substr in frame_id for substr in ['gripper', 'effector']):
        return 'gripper'
    elif 'end' in frame_id:
        return 'end'
    elif 'ankle' in frame_id:
        return 'ankle'
    elif 'sole' in frame_id:
        return 'sole'
    elif 'toe' in frame_id:
        return 'toe'
    elif any(substr in frame_id for substr in ['gaze', 'head']):
        return 'gaze'
    elif 'torso' in frame_id:
        return 'torso'
    elif 'odom' in frame_id:
        return 'odom'
    elif any(substr in frame_id for substr in ['map', 'world']):
        return 'world'
    else:
        return frame_id


class SymbolHelper:
    ''' HELPS FIND DEFINITIONS OF SYMBOLS AND DECORATES CPPCHECK SYMBOL TABLE
    '''

    def __init__(self):
        self.is_weak_inference = False
        self.weak_inference_classes = []
        self.ros_frame_dictionary = {}
        self.initialize_ros_frame_dictionary()
        self.ros_transform_frame_dictionary = {}
        self.initialize_ros_transform_frame_dictionary()
        self.ros_orientation_dictionary = {}
        self.initialize_ros_orientation_convention()
        self.ros_functions_with_types = ['x', 'y', 'z', 'w', 'getX', 'getY', 'getZ', 'getW', 'getOrigin', 'getRotation', 'getBasis']
        self.twist_odom_dict = {}
        self.func_name_dict = {}


    def fill_func_name_dict(self, functions):
        for f in functions:
            if f.name not in self.func_name_dict:
                self.func_name_dict[f.name] = [f]
            else:
                self.func_name_dict[f.name].append(f)


    def get_func_list_by_name(self, name):
        return self.func_name_dict.get(name)


    def clear_func_name_dict(self):
        self.func_name_dict.clear()


    def track_twist_odom(self, variable):
        if variable and variable.nameToken:
            filename = variable.nameToken.file

            if filename in self.twist_odom_dict:
                if variable not in self.twist_odom_dict[filename]:
                    self.twist_odom_dict[filename].append(variable)
            else:
                self.twist_odom_dict[filename] = [variable]


    def is_twist_odom(self, variable):
        if variable and variable.nameToken and variable.nameToken.file in self.twist_odom_dict:
            if variable in self.twist_odom_dict[variable.nameToken.file]:
                return True

        return False


    def find_compound_variable_token_and_name_for_variable_token(self, token):
        if not token.variable:
            raise ValueError('received a non variable token for tokenid:%s str:%s' % (token.Id, token.str))
        if not token.astParent:
            return (token, token.str)
        if token.astParent.str not in ['.', '[']:
            return (token, token.str)

        compound_variable_token = token
        compound_variable_root_token = token

        while compound_variable_root_token.astParent and (compound_variable_root_token.astParent.str in ['.', '[', '(']):
            if compound_variable_root_token.astParent.str not in ['[', '('] and \
                    compound_variable_root_token.astParent.astOperand2 and compound_variable_root_token.astParent.astOperand2.variable:
                compound_variable_token = compound_variable_root_token.astParent.astOperand2
            compound_variable_root_token = compound_variable_root_token.astParent

        if compound_variable_root_token.str == '(':     
            #var_type = self.find_variable_type(compound_variable_token.variable)
            #var_type = var_type.lower()
            # Remove the following check to support variable length arrays (~std::vector in c++) of ros types' members
            #((any(substr in var_type for substr in ['vector','deque','queue','map']) and \           
            if compound_variable_root_token.astOperand1 and compound_variable_root_token.astOperand1.str == '.' and \
                    compound_variable_root_token.astOperand1.astOperand2 and \
                    (compound_variable_root_token.astOperand1.astOperand2.str in ['at', 'back', 'front'] or \
                    compound_variable_root_token.astOperand1.astOperand2.str in self.ros_functions_with_types):
                name = self.recursively_visit(compound_variable_root_token.astOperand1.astOperand1)
                return (compound_variable_token, name)
                
            # FUNCTION CALL
            return (compound_variable_root_token, compound_variable_root_token.str)

        name = self.recursively_visit(compound_variable_root_token)
        return (compound_variable_token, name)
        

    #TODO check which variable token to be returned
    def find_compound_variable_token_and_name_for_sym_token(self, token):
        if token.str not in ['.', '[', '(', '&']:
            print 'received a non symbol token for tokenid:%s str:%s' % (token.Id, token.str)
            return (token, token.str)

        compound_variable_token = token
        if token.str == '(' and token.astOperand1:
            compound_variable_token = token.astOperand1
        elif token.str == '&' and token.astOperand2:
            compound_variable_token = token.astOperand2

        while compound_variable_token.astOperand1 and (not compound_variable_token.variable):
            if compound_variable_token.str not in ['[', '('] and \
                    compound_variable_token.astOperand2 and compound_variable_token.astOperand2.variable:
                compound_variable_token = compound_variable_token.astOperand2
            else:
                compound_variable_token = compound_variable_token.astOperand1

        if token.str == '(':
            if compound_variable_token.variable or compound_variable_token.varId:
                #var_type = self.find_variable_type(compound_variable_token.variable)
                #var_type = var_type.lower()
                # Remove the following check to support variable length arrays (~std::vector in c++) of ros types' members
                #((any(substr in var_type for substr in ['vector','deque','queue','map']) and \               
                if token.astOperand1 and token.astOperand1.str == '.' and \
                        token.astOperand1.astOperand2 and \
                        (token.astOperand1.astOperand2.str in ['at', 'back', 'front'] or \
                        token.astOperand1.astOperand2.str in self.ros_functions_with_types):
                    name = self.recursively_visit(token.astOperand1.astOperand1)
                    return (compound_variable_token, name)

            # FUNCTION CALL
            return (token, token.str)

        if token.str == '&' and token.astOperand2:
            token = token.astOperand2
           
        name = self.recursively_visit(token)
        return (compound_variable_token, name)


    def find_compound_variable_name_for_variable_token(self, token):
        ''' input: a variable token from cppcheckdata
            returns: string containing the compound variable name.  ex:  'my_var_.linear.x'
            '''
        if not token.variable:
            raise ValueError('received a non variable token for tokenid:%s str:%s' % (token.Id, token.str))
        if not token.astParent:
            return token.str
        if token.astParent.str != '.':
            return token.str
        compound_variable_root_token = token
        while compound_variable_root_token.astParent and compound_variable_root_token.astParent.str == '.':
            if compound_variable_root_token.astParent.astOperand2 and compound_variable_root_token.astParent.astOperand2.varId:
                compound_variable_root_token = compound_variable_root_token.astParent
            else:
                break
        return self.recursively_visit(compound_variable_root_token)


    def find_compound_variable_name_for_ros_variable_token(self, token):
        ''' input: a variable token from cppcheckdata
            returns: string containing the compound variable name.  ex:  'my_var_.linear.x'
            '''
        if not token.variable:
            raise ValueError('received a non variable token for tokenid:%s str:%s' % (token.Id, token.str))
        if token.astParent.str != '.':
            return token.str
        compound_variable_root_token = token.astParent
        while compound_variable_root_token.astParent and compound_variable_root_token.astParent.str == '.':
            compound_variable_root_token = compound_variable_root_token.astParent
        return self.recursively_visit(compound_variable_root_token)

            
    def recursively_visit(self, token):
        ''' input: a cppcheckdata token
            returns: string aggregation of tokens under the root
            '''
        my_return_string = ''

        if token.astOperand1: 
            my_return_string += self.recursively_visit(token.astOperand1)
        my_return_string += token.str 
        if token.astOperand2:
            my_return_string += self.recursively_visit(token.astOperand2)
        if token.str == '[':
            my_return_string += ']'
        elif token.str == '(':
            my_return_string += ')'
        
        return my_return_string


    def find_sanitized_variable_type(self, variable):
        var_type = self.find_variable_type(variable)
        # SANITIZE VAR TYPE
        var_type = self.sanitize_class_name(var_type)
        return var_type


    def find_variable_type(self, variable):
        ''' input: cppcheckdata variable object
            output: string of variable type  (ex:  'int'  or 'std::vector')
            '''
        my_return_string = variable.typeStartToken.str

        if variable.typeStartToken != variable.typeEndToken:
            nextToken = variable.typeStartToken.next
            hasNext = True
            while(hasNext and nextToken):  # BREAK at end of type region
                my_return_string += nextToken.str
                if nextToken.Id == variable.typeEndTokenId:
                    hasNext = False;
                nextToken = nextToken.next

        return my_return_string


    def rreplace(self, s, old, new, occurance):
        li = s.rsplit(old, occurance)
        return new.join(li)


    def sanitize_class_name(self, class_name):
        ''' TAKES A VARIABLE NAME AND STRIPTS EXTRA CLASS INFORMATION FROM FRONT AND BACK
            input: class_name   'constPtr<tf2::Transform::iterator>'  <-- LOL
            output: str         'trf2::Transform'
            '''
        is_some_change = True
        while (is_some_change):# SOME OF THESE CAN BE CASCADED IN DIFFERENT ORDERS
            is_some_change = False

            # SIMPLIFY ITERATORS
            if str(class_name).endswith('::iterator'):
                class_name = self.rreplace(class_name, '::iterator', '', 1)
                is_some_change = True
            if str(class_name).endswith('::const_iterator'):
                class_name = self.rreplace(class_name, '::const_iterator', '', 1)
                is_some_change = True
            # SIMPLIFY REFERNCES
            if str(class_name).endswith('&'):
                class_name = class_name.replace('&', '')
                is_some_change = True
            # SIMPLIFY CONST
            if str(class_name).endswith('const') or str(class_name).startswith('const'):
                class_name = self.rreplace(class_name, 'const', '', 1)
                is_some_change = True
            # SIMPLIFY CONSTANT POINTERS (REFRENCES)
            if str(class_name).endswith('ConstPtr'):
                class_name = class_name.replace('ConstPtr', '')
                is_some_change = True
            # SIMPLIFY POINTERS
            if str(class_name).endswith('::Ptr'):
                class_name = self.rreplace(class_name, '::Ptr', '', 1)
                is_some_change = True
            if str(class_name).endswith('Ptr'):
                class_name = self.rreplace(class_name, 'Ptr', '', 1)
                is_some_change = True
            # SIMPLIFY POINTERS
            if str(class_name).startswith('std::shared_ptr<') and str(class_name).endswith('>'):
                class_name = class_name.replace('std::shared_ptr<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('boost::shared_ptr<') and str(class_name).endswith('>'):
                class_name = class_name.replace('boost::shared_ptr<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('shared_ptr<') and str(class_name).endswith('>'):
                class_name = class_name.replace('shared_ptr<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('boost::scoped_ptr<') and str(class_name).endswith('>'):
                class_name = class_name.replace('boost::scoped_ptr<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('scoped_ptr<') and str(class_name).endswith('>'):
                class_name = class_name.replace('scoped_ptr<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            # SIMPLIFY FILTERS
            if str(class_name).startswith('tf::MessageFilter<') and str(class_name).endswith('>'):
                class_name = class_name.replace('tf::MessageFilter<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('tf2_ros::MessageFilter<') and str(class_name).endswith('>'):
                class_name = class_name.replace('tf_ros::MessageFilter<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('MessageFilter<') and str(class_name).endswith('>'):
                class_name = class_name.replace('MessageFilter<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            # SIMPLIFY VECTORS
            if str(class_name).startswith('std::vector<') and str(class_name).endswith('>'):
                class_name = class_name.replace('std::vector<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('conststd::vector<') and str(class_name).endswith('>'):
                class_name = class_name.replace('std::vector<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('vector<') and str(class_name).endswith('>'):
                class_name = class_name.replace('vector<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('std::deque<') and str(class_name).endswith('>'):
                class_name = class_name.replace('std::deque<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('deque<') and str(class_name).endswith('>'):
                class_name = class_name.replace('deque<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('std::queue<') and str(class_name).endswith('>'):
                class_name = class_name.replace('std::queue<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('queue<') and str(class_name).endswith('>'):
                class_name = class_name.replace('queue<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('std::map<') and str(class_name).endswith('>'):
                class_name = class_name.replace('std::map<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            if str(class_name).startswith('map<') and str(class_name).endswith('>'):
                class_name = class_name.replace('map<', '')
                class_name = self.rreplace(class_name, '>', '', 1)
                is_some_change = True
            # SIMPLIFY POINTER *
            if str(class_name).endswith('*'):
                class_name = self.rreplace(class_name, '*', '', 1)
                is_some_change = True
            # SIMPLIFY DANGLING ::
            if str(class_name).endswith('::'):
                class_name = self.rreplace(class_name, '::', '', 1)
                is_some_change = True
        # SANITIZED VERSION
        return class_name


    def has_string_type(self, token):
        if token.variable:
            var_type = self.find_sanitized_variable_type(token.variable) 
            if var_type in ['string','std::string']:
                return True
        return False


    def has_ros_frame_type(self, token):
        if token.variable:
            var_type = self.find_sanitized_variable_type(token.variable) 
            var_name = self.find_compound_variable_name_for_ros_variable_token(token)
            if var_type in self.ros_frame_dictionary:
                if any(substr in var_name for substr in self.ros_frame_dictionary[var_type]):
                    return True
            elif var_type in self.ros_transform_frame_dictionary:
                if any(substr in var_name for substr in self.ros_transform_frame_dictionary[var_type]):
                    return True

        return False
 

    def has_frame_type(self, token):
        if token.variable:
            var_type = self.find_sanitized_variable_type(token.variable) 

            if var_type in ['string','std::string', 'auto', 'char']:
                return True

            if var_type in ['tf::Transform','tf::Quaternion','tf::Vector3','tf::Matrix3x3']: # tf::Point, tf::Pose?
                return True

            if var_type in ['tf2::Transform','tf2::Quaternion','tf2::Vector3','tf2::Matrix3x3']:
                return True

            if var_type in ['geometry_msgs::Point', 'geometry_msgs::Pose', 'geometry_msgs::Quaternion', 'geometry_msgs::Transform', 'geometry_msgs::Vector3']:
                return True

            var_name = self.find_compound_variable_name_for_ros_variable_token(token)
            
            if var_type in self.ros_frame_dictionary:
                if var_name == token.str:
                    return True
                elif any(var_name.endswith(substr) for substr in self.ros_frame_dictionary[var_type]):
                    return True
            elif var_type in self.ros_transform_frame_dictionary:
                if var_name == token.str:
                    return True
                elif any(var_name.endswith(substr) for substr in self.ros_transform_frame_dictionary[var_type]):
                    return True

        return False
        

    def is_ros_transform_type(self, variable):
        if variable:
            var_type = self.find_variable_type(variable)

            if any(substr in var_type for substr in ['vector<', 'deque<', 'queue<', 'map<']):
                return False

            # SANITIZE VAR TYPE      
            var_type = self.sanitize_class_name(var_type)

            if var_type in self.ros_transform_frame_dictionary:
                return True

        return False


    def is_ros_type(self, variable):
        if variable:
            var_type = self.find_sanitized_variable_type(variable)
            if var_type in self.ros_frame_dictionary:
                return True
            elif var_type in self.ros_transform_frame_dictionary:
                return True

        return False


    def get_frame_count_by_ros_type_of_variable(self, variable):
        if not variable:
            return 0

        var_type = self.find_variable_type(variable)
        frame_count = self.get_frame_count_for_type(var_type)

        if var_type == 'nav_msgs::Odometry':
            if not self.is_twist_odom(variable):
                frame_count -= 1

        return frame_count


    def get_frame_count_by_ros_type_of_function(self, function):
        if not function:
            return 0

        frame_count = self.get_frame_count_for_type(function.return_type)
        return frame_count        


    def get_frame_count_for_type(self, dtype):
        if not dtype:
            return 0

        if any(substr in dtype for substr in ['::const_iterator', '::iterator', 'vector<', 'MessageFilter<', 'deque<']):
            return 0

        # SANITIZE TYPE
        dtype = self.sanitize_class_name(dtype)

        if dtype in ['stereo_msgs::DisparityImage', 'visualization_msgs::MarkerArray']:
            # header of 'image' field is used to specify frame
            return 0

        frame_count = len(self.ros_frame_dictionary[dtype])-1 if dtype in self.ros_frame_dictionary else 0
        return frame_count


    def get_ros_orientation_convention(self, frame_id):
        for id_str in self.ros_orientation_dictionary:
            if id_str in frame_id:
                return self.ros_orientation_dictionary[id_str]

        return ('f', 'l', 'u')


    def initialize_ros_orientation_convention(self):
        self.ros_orientation_dictionary['world'] = ('f', 'l', 'u')
        self.ros_orientation_dictionary['enu'] = ('f', 'l', 'u')
        self.ros_orientation_dictionary['map'] = ('f', 'l', 'u')
        self.ros_orientation_dictionary['odom'] = ('f', 'l', 'u')
        self.ros_orientation_dictionary['base_link'] = ('f', 'l', 'u')
        self.ros_orientation_dictionary['base_footprint'] = ('f', 'l', 'u')

        self.ros_orientation_dictionary['_ned'] = ('l', 'f', 'd')

        self.ros_orientation_dictionary['optical'] = ('r', 'd', 'f')
        #self.ros_orientation_dictionary['camera'] = ('r', 'd', 'f')


    def initialize_ros_frame_dictionary(self):

        #self.ros_frame_dictionary['actionlib_msgs::GoalStatusArray'] = ['header.frame_id']    #NOT SURE

        #self.ros_frame_dictionary['diagnostic_msgs::DiagnosticArray'] = ['header.frame_id']    #NOT USED

        self.ros_frame_dictionary['geometry_msgs::AccelStamped']               = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::AccelWithCovarianceStamped'] = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::InertiaStamped']             = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::PointStamped']               = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::PolygonStamped']             = ['header', 'frame_id']        
        self.ros_frame_dictionary['geometry_msgs::PoseStamped']                = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::PoseWithCovarianceStamped']  = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::QuaternionStamped']          = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::TwistStamped']               = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::TwistWithCovarianceStamped'] = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::Vector3Stamped']             = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::WrenchStamped']              = ['header', 'frame_id']
        self.ros_frame_dictionary['geometry_msgs::PoseArray']                  = ['header', 'frame_id']    #NOT SURE

        self.ros_frame_dictionary['nav_msgs::Odometry']       = ['header', 'frame_id', 'child_frame_id']       
        #self.ros_frame_dictionary['nav_msgs::GridCells']     = ['header.frame_id']    #NOT SURE
        self.ros_frame_dictionary['nav_msgs::OccupancyGrid'] = ['header', 'frame_id']    #NOT SURE        
        self.ros_frame_dictionary['nav_msgs::Path']           = ['header', 'frame_id']    #NOT SURE
        
        self.ros_frame_dictionary['sensor_msgs::CameraInfo']          = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::CompressedImage']     = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::Image']               = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::FluidPressure']       = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::Illuminance']         = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::Imu']                 = ['header', 'frame_id']       
        self.ros_frame_dictionary['sensor_msgs::LaserScan']           = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::MultiEchoLaserScan']  = ['header', 'frame_id']        
        self.ros_frame_dictionary['sensor_msgs::MagneticField']       = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::NavSatFix']           = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::PointCloud']          = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::PointCloud2']         = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::RelativeHumidity']    = ['header', 'frame_id']
        self.ros_frame_dictionary['sensor_msgs::Temperature']         = ['header', 'frame_id']
        #self.ros_frame_dictionary['sensor_msgs::BatteryState']       = ['header.frame_id']    #NOT SURE
        #self.ros_frame_dictionary['sensor_msgs::JointState']         = ['header.frame_id']    #NOT SURE
        #self.ros_frame_dictionary['sensor_msgs::MultiDOFJointState'] = ['header.frame_id']    #NOT SURE
        #self.ros_frame_dictionary['sensor_msgs::Joy']                = ['header.frame_id']    #NOT SURE/USED
        #self.ros_frame_dictionary['sensor_msgs::Range']              = ['header.frame_id']    #NOT SURE
        #self.ros_frame_dictionary['sensor_msgs::TimeReference']      = ['header.frame_id']    #NOT USED

        self.ros_frame_dictionary['stereo_msgs::DisparityImage'] = ['image', 'header', 'frame_id']    #NOT SURE
        self.ros_frame_dictionary['visualization_msgs::MarkerArray'] = ['markers']
        self.ros_frame_dictionary['std_msgs::Header'] = ['frame_id', 'dummy']
        
        self.ros_frame_dictionary['trajectory_msgs::MultiDOFJointTrajectory'] = ['header', 'frame_id']
        #self.ros_frame_dictionary['trajectory_msgs::JointTrajectory']        = ['header.frame_id']    #NOT SURE
 
        self.ros_frame_dictionary['visualization_msgs::InteractiveMarkerFeedback'] = ['header', 'frame_id']
        self.ros_frame_dictionary['visualization_msgs::InteractiveMarkerPose']     = ['header', 'frame_id']
        self.ros_frame_dictionary['visualization_msgs::Marker']                    = ['header', 'frame_id']
        self.ros_frame_dictionary['visualization_msgs::InteractiveMarker']         = ['header', 'frame_id']    #NOT USED ALWAYS ??
        #self.ros_frame_dictionary['visualization_msgs::InteractiveMarkerControl'] = ['orientation']    #NOT SURE ??

        self.ros_frame_dictionary['tf::Stamped<tf::Point>']      = ['frame_id_', 'dummy']
        self.ros_frame_dictionary['tf::Stamped<tf::Pose>']       = ['frame_id_', 'dummy']
        self.ros_frame_dictionary['tf::Stamped<tf::Quaternion>'] = ['frame_id_', 'dummy']
        self.ros_frame_dictionary['tf::Stamped<tf::Vector3>']    = ['frame_id_', 'dummy']


    def initialize_ros_transform_frame_dictionary(self):

        self.ros_transform_frame_dictionary['geometry_msgs::TransformStamped'] = ['header', 'frame_id', 'child_frame_id']
        self.ros_transform_frame_dictionary['tf::StampedTransform']            = ['frame_id_', 'child_frame_id_']  




