from tree_walker import TreeWalker
from symbol_helper import SymbolHelper
#from type_helper import TypeHelper
import debug_data as dd
import os
import copy


class TypeAnnotator:

    def __init__(self, th, sh):
        self.tw = TreeWalker()
        self.sh = sh #SymbolHelper()
        self.th = th

        self.is_frame_set = False
        self.disable_use_check = False

        self.current_xyz_assign_line = 0
        self.current_xyz_assign_list = []

        self.tfMatrixIds = []

        self.was_some_value_changed = False
        self.found_values_in_this_tree = False


    def find_type_annotation_for_linter_transform(self, transform):
        rot = [transform.qx, transform.qy, transform.qz, transform.qw] if transform.isQuat else [transform.y, transform.p, transform.r]
        rot_type = 'Q' if transform.isQuat else 'E'

        orient = self.th.find_orientation_type(rot, rot_type)

        (f_x_dir, f_y_dir, f_z_dir) = self.th.get_frame_orientation(transform.parent, default=True)
        f = self.th.create_frame_type(transform.parent, f_x_dir, f_y_dir, f_z_dir)
        
        if orient:
            cf_dir = self.th.find_childframe_orientation([f_x_dir, f_y_dir, f_z_dir],
                                                         [[orient[0][0], orient[0][1], orient[0][2]],
                                                          [orient[1][0], orient[1][1], orient[1][2]]])
            if len(cf_dir) == 3:
                (cf_x_dir, cf_y_dir, cf_z_dir) = tuple(cf_dir)
                self.th.set_frame_orientation(transform.child, (cf_x_dir, cf_y_dir, cf_z_dir))
                cf = self.th.create_frame_type(transform.child, cf_x_dir, cf_y_dir, cf_z_dir)                
                f.extend(cf)
                return f

        cf = self.th.create_frame_type(transform.child, 'x', 'y', 'z')
        f.extend(cf)
        return f


    def add_type_annotations_outside_functions(self, root_token):
        try:
            self.tw.generic_recurse_and_apply_function(root_token, self.identify_used_variables)
            self.tw.generic_recurse_and_apply_function(root_token, self.annotate_frame_id_init_at_constructor)
            self.tw.generic_recurse_and_apply_function(root_token, self.annotate_frame_id_assignment)
        except RuntimeError as detail:
            print "Handling run-time error:", detail


    def add_param_type_annotations(self, root_token):
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_string_functions)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_string_concatenation)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_frame_id_param)


    def add_type_annotations(self, root_token):
        self.is_frame_set = False

        new_root_token = root_token.astOperand2 if (self.is_match(root_token, '=') and root_token.isAssignmentOp) else root_token
        self.tw.generic_recurse_and_apply_function(new_root_token, self.identify_used_variables)

        self.tw.generic_recurse_and_apply_function(root_token, self.identify_optional_header_variables)
        self.tw.generic_recurse_and_apply_function(root_token, self.identify_variables_set_by_common_ros_library)
        self.tw.generic_recurse_and_apply_function(root_token, self.identify_variables_set_by_get_methods)

        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_string_functions)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_string_concatenation)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_frame_id_param)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_frame_ids_in_function_call)        
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_object_construction_by_new)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_object_type_cast)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_pointers)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_object_construction_by_copy)
        #self.tw.generic_recurse_and_apply_function(root_token, self.annotate_ternary)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_publish_message)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_lookup_transform)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_transform_object)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_create_quaternion_functions)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_msg_tf_functions)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_vector3)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_quaternion_construction)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_matrix3x3)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_set_identity)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_set_origin)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_set_basis_and_rotation)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_set_euler_rotation_and_fixed_rotation)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_set_value)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_get_functions)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_matrix_multiplication)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_matrix_transpose)
        #self.tw.generic_recurse_and_apply_function(root_token, self.annotate_inverse)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_transform_construction)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_tf_stamped_construction)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_stamped_transform_construction)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_do_transform)  
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_send_transform)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_function_return)
        self.tw.generic_recurse_and_apply_function(root_token, self.annotate_frame_id_assignment)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # HELPER RULES
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def identify_used_variables(self, token, left_token, right_token):

        #TODO OR handle it similar to Marker in self.identify_optional_header_variables
        if token.str == 'push_back' and self.is_match(token.next, '('):
            if token.astParent and token.astParent.astOperand1:
                (var_token, var_name) = self.get_var_token_and_var_name(token.astParent.astOperand1)
                if var_token and var_token.variable and self.sh.find_sanitized_variable_type(var_token.variable) == 'nav_msgs::Path':
                    self.disable_use_check = True

        elif self.disable_use_check:
            if token.str == '(' and self.is_match(token.previous, 'push_back'):
                self.disable_use_check = False                  

        elif token.variable and token != token.variable.nameToken:
            #NOT A DECLARATION INSTANCE OF VARIABLE

            (var_token, var_name) = self.sh.find_compound_variable_token_and_name_for_variable_token(token)
            
            if ('.frame_id' in var_name) or var_name.endswith('header') or \
                    ('.child_frame_id' in var_name) or \
                    (var_name.endswith(token.variable.nameToken.str)):

                token.variable.isUsed = True


    def identify_optional_header_variables(self, token, left_token, right_token):
        if token.str == 'push_back':
            # As per the specification, if marker is used along with interactive marker control of an interactive marker,
            # the header is optional. If not provided the header of imarker is used for the marker.

            if self.is_match(token.next, '(') and token.next.astOperand2:
                (right_var, right_name) = self.get_var_token_and_var_name(token.next.astOperand2)

                if right_var and right_var.variable and self.sh.find_sanitized_variable_type(right_var.variable).endswith('::Marker'):
                    if self.is_match(token.astParent, '.') and self.is_match(token.astParent.astOperand1, '.') and token.astParent.astOperand1.astOperand1:
                        (left_var, left_name) = self.get_var_token_and_var_name(token.astParent.astOperand1.astOperand1)
                            
                        if left_var and left_var.variable and self.sh.find_sanitized_variable_type(left_var.variable).endswith('InteractiveMarkerControl'):
                            right_var.variable.is_frame_set = True

    
    def identify_variables_set_by_common_ros_library(self, token, left_token, right_token):
        # if token.str in ['getRobotPose', 'getGlobalFrameID', 'getBaseFrameID']:
        #     # costmap_2d ROS
         
        #     if token.astParent and token.astParent.astOperand1:
        #         (left_var, left_name) = self.get_var_token_and_var_name(token.astParent.astOperand1)

        #         if left_var and left_var.variable:
        #             left_type = self.sh.find_sanitized_variable_type(left_var.variable)

        #             if 'Costmap2DROS' in left_type and self.is_match(token.next, '('):
        #                 if token.next.astOperand2:
        #                     (right_var, right_name) = self.get_var_token_and_var_name(token.next.astOperand2)

        #                     if right_var and right_var.variable:
        #                         right_var.variable.is_frame_set = True

        #                 else:
        #                     self.is_frame_set = True

        # elif token.str == 'getRobotVel':
        #     # base_local_planner::odometry_helper_ros

        #     if token.astParent and token.astParent.astOperand1:
        #         (left_var, left_name) = self.get_var_token_and_var_name(token.astParent.astOperand1)

        #         if left_var and left_var.variable:
        #             left_type = self.sh.find_sanitized_variable_type(left_var.variable)

        #             if 'OdometryHelperRos' in left_type and self.is_match(token.next, '('):
        #                 if token.next.astOperand2:
        #                     (right_var, right_name) = self.get_var_token_and_var_name(token.next.astOperand2)

        #                     if right_var and right_var.variable:
        #                         right_var.variable.is_frame_set = True

        if token.str in ['toROSMsg', 'moveToROSMsg'] or token.str in ['fromPCL', 'moveFromPCL'] \
                or token.str in ['copyPCLImageMetaData', 'copyPCLPointCloud2MetaData']:
            # pcl_conversions: ROS wrapper for pcl library
            
            if self.is_match(token.next, '('):
                args_cnt = self.get_count_of_function_arguments(token.next)

                if args_cnt == 2:
                    var_token = self.get_comma_separated_token_at_pose_from_right(token.next, 1)
                    (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                    if var_token and var_token.variable:
                        if token.str in ['toROSMsg', 'moveToROSMsg']:
                            var_type = self.sh.find_sanitized_variable_type(var_token.variable)
                            if var_type == 'sensor_msgs::Image':
                                # As per pcl conversions api code, image header is not set unlike pointecloud2 header
                                return
                        
                        var_token.variable.is_frame_set = True

                elif args_cnt == 1 and token.str == 'fromPCL':
                    # header type has a fromPCL version with both two and one arguments
                    self.is_frame_set = True

        elif token.str == 'transformPointCloud':
            # pcl_ros

            if self.is_match(token.next, '(') and self.get_count_of_function_arguments(token.next) >= 3:
                var_token = self.get_comma_separated_token_at_pose_from_right(token.next, 1)
                (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                if var_token and var_token.variable:
                    var_type = self.sh.find_sanitized_variable_type(var_token.variable)
                    if var_type.startswith('sensor_msgs::PointCloud'):
                        var_token.variable.is_frame_set = True
                    else:
                        var_token = self.get_comma_separated_token_at_pose_from_right(token.next, 2)
                        (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                        if var_token and var_token.variable:
                            var_type = self.sh.find_sanitized_variable_type(var_token.variable)
                            if var_type.startswith('sensor_msgs::PointCloud'):
                                var_token.variable.is_frame_set = True
        
        elif token.str in ['convertPointCloud2ToPointCloud', 'convertPointCloudToPointCloud2']:
            # sensor_msgs/point_cloud_conversion.h
            #TODO assign frame from in var to out var

            if self.is_match(token.next, '(') and self.get_count_of_function_arguments(token.next) == 2:
                var_token = self.get_comma_separated_token_at_pose_from_right(token.next, 1)
                (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                if var_token and var_token.variable:
                    var_token.variable.is_frame_set = True

        elif token.str in ['toImageMsg', 'toCompressedImageMsg']:
            # cv_bridge
            #TODO assign frame from in var to out var

            is_frame_set = True

            if self.is_match(token.astParent, '.') and self.is_match(token.astParent.astOperand1, '('):
                paren_token = token.astParent.astOperand1
                if self.is_match(paren_token.previous, 'CvImage'):
                    args_cnt = self.get_count_of_function_arguments(paren_token)
                    header_token = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt)
                    frame = self.th.find_frame_type(header_token)
                    if not frame:
                        is_frame_set = False
            
            if is_frame_set and self.is_match(token.next, '('):
                args_cnt = self.get_count_of_function_arguments(token.next)

                if args_cnt == 0:
                    self.is_frame_set = True

                elif args_cnt in [1, 2]:
                    var_token = self.get_comma_separated_token_at_pose_from_right(token.next, args_cnt)
                    (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                    if var_token and var_token.variable:
                        var_token.variable.is_frame_set = True

        elif token.str in ['transformLaserScanToPointCloud', 'projectLaser']:
            # laser_geometry LaserProjection
            #TODO assign frame from in var to out var

           if token.astParent and token.astParent.astOperand1:
                (left_var, left_name) = self.get_var_token_and_var_name(token.astParent.astOperand1)

                if left_var and left_var.variable:
                    left_type = self.sh.find_sanitized_variable_type(left_var.variable)

                    if 'LaserProjection' in left_type and self.is_match(token.next, '('):
                        args_cnt = self.get_count_of_function_arguments(token.next)
                        cnt = args_cnt-1 if token.str == 'projectLaser'else args_cnt-2
                        
                        var_token = self.get_comma_separated_token_at_pose_from_right(token.next, cnt)
                        (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                        if var_token and var_token.variable:
                            var_token.variable.is_frame_set = True

        elif token.str == 'waitForMessage':
            # ros::topic

            if token.astParent and \
                    ((token.astParent.str == '::' and self.is_match(token.astParent.astParent, '(')) or \
                     (token.astParent.str == '(')):

                self.is_frame_set = True

        # elif token.str in ['getCurrentPose', 'getRandomPose', 'getPoseTarget'] or \
        #         token.str in ['getEndEffectorLink', 'getPoseReferenceFrame', 'getPlanningFrame']:

        #     if token.astParent and token.astParent.astOperand1:
        #         (left_var, left_name) = self.get_var_token_and_var_name(token.astParent.astOperand1)

        #         if left_var and left_var.variable:
        #             left_type = self.sh.find_sanitized_variable_type(left_var.variable)

        #             if 'MoveGroup' in left_type and self.is_match(token.next, '('): 
        #                 self.is_frame_set = True

        elif token.str == 'tfFrame':

            if token.astParent and token.astParent.astOperand1:
                (left_var, left_name) = self.get_var_token_and_var_name(token.astParent.astOperand1)

                if left_var and left_var.variable:
                    left_type = self.sh.find_sanitized_variable_type(left_var.variable)

                    if 'image_geometry' in left_type and self.is_match(token.next, '('): 
                        self.is_frame_set = True

        elif token.str == 'update':
            # filters::<>
            #TODO assign frame from in var to out var

           if token.astParent and token.astParent.astOperand1:
                (left_var, left_name) = self.get_var_token_and_var_name(token.astParent.astOperand1)

                if left_var and left_var.variable:
                    left_type = self.sh.find_sanitized_variable_type(left_var.variable)

                    if 'filter' in left_type.lower() and self.is_match(token.next, '(') and \
                            self.get_count_of_function_arguments(token.next) == 2:
                        
                        var_token = self.get_comma_separated_token_at_pose_from_right(token.next, 1)
                        (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                        if var_token and var_token.variable:
                            var_token.variable.is_frame_set = True 

        elif token.str == 'subscribe':
            # ros/node.h version which takes the variable as an argument

            if self.is_match(token.next, '('): 
                args_cnt = self.get_count_of_function_arguments(token.next)

                if args_cnt == 5:
                    last_token = self.get_comma_separated_token_at_pose_from_right(token.next, 1)
                    var_token = self.get_comma_separated_token_at_pose_from_right(token.next, args_cnt-1)

                    if last_token.isNumber and (not var_token.isNumber):
                        # nodeHandle.subscribe functions' second argument is number unlike node.subscribe version
                        (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                        if var_token and var_token.variable:
                            var_token.variable.is_frame_set = True

        elif token.str == 'lower_bound':
            # std::lower_bound(t1, t2, tmp, comp)

            if self.is_match(token.next, '('):
                args_cnt = self.get_count_of_function_arguments(token.next)

                if args_cnt == 4:
                    var_token = self.get_comma_separated_token_at_pose_from_right(token.next, 2)
                    func_token = self.get_comma_separated_token_at_pose_from_right(token.next, 1)

                    if func_token and (func_token.str.lower().endswith('stamps') or func_token.str.lower().endswith('stamp')):
                        (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                        if var_token and var_token.variable:
                            var_token.variable.isUsed = False

        elif token.str.startswith('read'):
            # orocos RTT::InputPort

            if self.is_match(token.next, '(') and token.astParent and token.astParent.astOperand1:
                (left_var, left_name) = self.get_var_token_and_var_name(token.astParent.astOperand1)

                if left_var and left_var.variable:
                    left_type = self.sh.find_sanitized_variable_type(left_var.variable)

                    if 'InputPort' in left_type:
                        args_cnt = self.get_count_of_function_arguments(token.next)

                        if args_cnt > 0:
                            right_token = self.get_comma_separated_token_at_pose_from_right(token.next, args_cnt)
                            (right_var, right_name) = self.get_var_token_and_var_name(right_token)

                            if right_var and right_var.variable:
                                right_var.variable.is_frame_set = True


    def identify_variables_set_by_get_methods(self, token, left_token, right_token):

        if token.str.startswith('get') and self.is_match(token.next, '(') and \
                (not token.function) and (not token.varId):
            # 'get...' function, but not identified as a function by cppcheck
         
            args_cnt = self.get_count_of_function_arguments(token.next)

            if args_cnt == 1:
                right_token = self.get_comma_separated_token_at_pose_from_right(token.next, args_cnt)
                (right_var, right_name) = self.get_var_token_and_var_name(right_token)

                if right_var and right_var.variable:
                    right_var.variable.is_frame_set = True

            else:
                self.is_frame_set = True


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # HELPER FUNCTIONS
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        

    def is_match(self, token, value):
        if token and (token.str == value):
            return True

        return False


    def get_comma_separated_token_at_pose_from_right(self, paren_token, pos):
        if self.is_match(paren_token, '('):
            token = paren_token.astOperand2
            i = 1
            while i < pos:
                if not token:
                    return None
                token = token.astOperand1
                i += 1

            if i == pos and token:
                return token.astOperand2 if self.is_match(token, ',') else token
        
        return None


    def recurse_and_get_comma_separated_tokens(self, token, arguments):
        if not token:
            return

        if token.str == ',':
            self.recurse_and_get_comma_separated_tokens(token.astOperand1, arguments)
            self.recurse_and_get_comma_separated_tokens(token.astOperand2, arguments)
        else:
            arguments.append(token)


    def get_function_arguments(self, paren_token):
        arguments = []
        if self.is_match(paren_token, '('):
            self.recurse_and_get_comma_separated_tokens(paren_token.astOperand2, arguments)

        return arguments


    def get_count_of_function_arguments(self, paren_token):
        if self.is_match(paren_token, '('):
            token = paren_token.astOperand2
            if not token:
                return 0

            i = 1
            while token.str == ',':
                i += 1
                token = token.astOperand1

            return i


    def get_var_token_and_var_name(self, token):
        if self.is_match(token, '::') and token.astOperand2:
            # INIT STATEMENT e.g. const std::string s = 's'
            token = token.astOperand2

        if self.is_match(token, '*') and token.astOperand1 and (not token.astOperand2):
            # DEREFERENCE
            token = token.astOperand1

        var_token = token
        var_name = token.str
        
        if token.str in ['.', '[', '(', '&']:
            (var_token, var_name) = self.sh.find_compound_variable_token_and_name_for_sym_token(token)

        return (var_token, var_name)


    def extract_dir_text(self, token):
	if not token:
            return ''

        # TO AVOID NUMERICAL VALUE 0, 1, 2
        if token.isNumber:
            return ''

        isMinus = False
        var_token = None
       
        if token.str == '-':
            isMinus = True
            token = token.astOperand1

        if token and token.str == '(':
            token = token.astOperand1

        if token and (token.str == '.' or token.str == '['):
            var_token = token.astOperand1
            token = token.astOperand2

        if self.is_match(token, 'at') and token.astParent and token.astParent.astParent:
            token = token.astParent.astParent.astOperand2

        if token and (token.str in ['x', 'y', 'z', '0', '1', '2', 'getX', 'getY', 'getZ']):
            dir_text = token.str

            # consider coordinate system of right-side variable to determine axis dir (right_xyz)
            if var_token:
                frame = self.th.find_frame_type(var_token)
                if frame and self.th.is_default_frame_type(frame):
                    f = frame[0]

                    if dir_text in ['x', 'getX']:
                        dir_text = f.x_dir
                    elif dir_text in ['y', 'getY']:
                        dir_text = f.y_dir
                    elif dir_text in ['z', 'getZ']:
                        dir_text = f.z_dir
                else:
                    return ''

            if isMinus:
                dir_text = '-' + dir_text
            return dir_text

        return ''


    # assumes that the name has dir text
    def remove_dir_text(self, token):
        if token.str == '(':
            token = token.astOperand1

        if token.str == '.' or token.str == '[':
            token = token.astOperand1

        name = self.sh.recursively_visit(token)
        return name


    #TODO improve: too many lists; replace with if-else?
    def translate_to_xyz(self, l):
        l[:] = ['x' if e in ['0', 'getX'] else e for e in l]
        l[:] = ['y' if e in ['1', 'getY'] else e for e in l]
        l[:] = ['z' if e in ['2', 'getZ'] else e for e in l]
        l[:] = ['-x' if e in ['-0', '-getX'] else e for e in l]
        l[:] = ['-y' if e in ['-1', '-getY'] else e for e in l]
        l[:] = ['-z' if e in ['-2', '-getZ'] else e for e in l]
        return l



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # TYPE ASSIGNMENT RULES
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # frame id assignment; rhs can be string, function return value of type string, variable 
    def annotate_frame_id_assignment(self, token, left_token, right_token):

        if token.str == '=' and token.isAssignmentOp and \
                left_token and right_token:
                
            # MULTIPLE ASSIGNMENT
            if self.is_match(right_token, '='):
                right_token = right_token.astOperand1
            
            # UNARY MINUS
            right_minus = False
            if self.is_match(right_token, '-') and (not right_token.astOperand2):
                right_minus = True
                right_token = right_token.astOperand1

            #TODO right side: *1.0 or 1.0*

            if self.is_match(right_token, '(') and self.is_match(right_token.previous, 'string'):
                # std::string()
                right_token = right_token.astOperand2

            # XYZ ASSIGNMENT
            left_xyz = self.extract_dir_text(left_token)
            right_xyz = self.extract_dir_text(right_token)

            if left_xyz and right_xyz:

                if self.current_xyz_assign_line != 0 and (int(left_token.linenr) - self.current_xyz_assign_line >= 3):
                    self.current_xyz_assign_line = 0
                    self.current_xyz_assign_list = []

                if self.current_xyz_assign_line == 0:
                    self.current_xyz_assign_line = int(left_token.linenr)
                
                #TODO check if right_list has xyz dirs, else translate right values to frame for the rotation? 
                #TODO check if consecutive lines assign x y z of the same variable from the same variable? - for now, assume that it's same
                if int(left_token.linenr) - self.current_xyz_assign_line < 3:     
                    self.current_xyz_assign_list.append((left_xyz, right_xyz, right_minus))

                if len(self.current_xyz_assign_list) == 3:
                    # UNZIP LIST OF TUPLES TO LISTS
                    self.current_xyz_assign_list = [list(e) for e in zip(*(self.current_xyz_assign_list))]
 
                    left_list = self.translate_to_xyz(self.current_xyz_assign_list[0])
                    if all(d in left_list for d in ['x', 'y', 'z']):
                        right_list = self.translate_to_xyz(self.current_xyz_assign_list[1])
                        minus_list = self.current_xyz_assign_list[2]

                        for i in range(len(minus_list)):
                            if minus_list[i]:
                                right_list[i] = '-' + right_list[i]

                        dir_list = ['']*3
                        for i in range(len(left_list)):
                            if left_list[i] == 'x':
                                dir_list[0] = right_list[i]
                            elif left_list[i] == 'y':
                                dir_list[1] = right_list[i]
                            elif left_list[i] == 'z':
                                dir_list[2] = right_list[i]

                        frame = self.th.create_frame_type('xyz', dir_list[0], dir_list[1], dir_list[2])
                        to_frame = self.th.get_default_frame_type()
                        frame.extend(to_frame)
                        
                        (left_var, left_name) = self.get_var_token_and_var_name(left_token)
                        if left_var and left_var.variable:
                            left_name = self.remove_dir_text(left_token)
                            self.th.set_frame_type_for_variable_token(left_var, left_name, frame)

            #TODO vector assignment to left xyz (e.g. transform translation) 
                        
            # DATA FLOW FROM RIGHT TO LEFT
            if left_token and right_token:
                (left_var, left_name) = self.get_var_token_and_var_name(left_token)

                left_type = None
                if left_var and left_var.variable:
                    left_type = self.sh.find_sanitized_variable_type(left_var.variable)

                    if (left_type == 'nav_msgs::Odometry') and ('twist' in left_name):
                        self.sh.track_twist_odom(left_var.variable)
                    elif (left_type == 'visualization_msgs::Marker') and ('action' in left_name):
                        if (right_token.str == '::' and right_token.astOperand2 and 'delete' in right_token.astOperand2.str.lower()) or \
                                'delete' in right_token.str.lower() or \
                                token.str == '2' or token.str == '3':
                            left_var.variable.checkFrame = False
                    
                right_frame = self.th.find_frame_type(right_token) 
 
                if right_frame:                
                    self.th.set_frame_type_for_variable_token(left_var, left_name, right_frame)
                else:
                    right_type = None
                    if right_token.str == '(' and right_token.previous and \
                            right_token.previous.function and (not right_token.previous.function.isAnnotated):
                        right_type = right_token.previous.function.return_type
                    if left_var and left_var.variable and left_type == right_type:
                        left_var.variable.is_frame_set = True

                if self.is_frame_set:
                    if left_var and left_var.variable:
                        if ('.frame_id' in left_name) or left_name.endswith('header') or \
                                ('.child_frame_id' in left_name) or \
                                (left_name.endswith(left_var.variable.nameToken.str)):
                            left_var.variable.is_frame_set = True

                        self.is_frame_set = False


    def annotate_frame_id_init_at_constructor(self, token, left_token, right_token):

        if (token.str == ':') and self.is_match(right_token, '('):
            if self.is_match(token.astParent, '?'):
                # TERNARY OPERATOR
                return

            var_token = right_token.astOperand1
            frame_token = right_token.astOperand2
            if var_token and frame_token:

                if self.is_match(frame_token, '(') and self.is_match(frame_token.previous, 'string'):
                    # std::string()
                    frame_token = frame_token.astOperand2

                frame = self.th.find_frame_type(frame_token)
                if frame:
                    (var_token, var_name) = self.get_var_token_and_var_name(var_token)
                    self.th.set_frame_type_for_variable_token(var_token, var_name, frame)

            if right_token.link and self.is_match(right_token.link.next, ','):
                # AS THERE IS NO PARENT_CHILD PATH FROM ':',
                # CHECK FOR MORE INITIALIZATIONS AT THE CONSTRUCTOR
                comma_token = right_token.link.next
                while (comma_token):
                    paren_token = comma_token.astOperand2
                    if self.is_match(paren_token, '('):
                        var_token = paren_token.astOperand1
                        frame_token = paren_token.astOperand2

                        if var_token and frame_token:

                            if self.is_match(frame_token, '(') and self.is_match(frame_token.previous, 'string'):
                                # std::string()
                                frame_token = frame_token.astOperand2

                            frame = self.th.find_frame_type(frame_token)
                            if frame:
                                (var_token, var_name) = self.get_var_token_and_var_name(var_token)
                                self.th.set_frame_type_for_variable_token(var_token, var_name, frame)

                    comma_token = comma_token.astParent
                            

    # frame_id param set with default value:
    # a) nh.param<std::string>("frame_id", frame_id_, "map");
    # b) frame_id_ = nh.param<std::string>("frame_id", "map");
    # c) ros::param::param<std::string>("frame_id", frame_id_, "map");
    # d) frame_id_ = ros::param::param<std::string>("frame_id", "map");
    #
    # frame_id param set without default value:
    # a) nh.getParam("frame_id", frame_id_)
    # b) ros::param::get("frame_id", frame_id_)
    # c) nh.getParamCached(("frame_id", frame_id_)
    # d) ros::param::getCached("frame_id", frame_id_)
    #
    def annotate_frame_id_param(self, token, left_token, right_token):
        if (token.str == 'param'):

            #if self.is_match(token.next, '<') and self.is_match(token.next.link, '>') and self.is_match(token.next.link.next, '('):
            #    paren_token = token.next.link.next

            if token.astParent and token.astParent.str in ['.', '::'] and self.is_match(token.astParent.astParent, '('):
                paren_token = token.astParent.astParent
                frame_token = self.get_comma_separated_token_at_pose_from_right(paren_token, 1)

                if self.is_match(frame_token, '('):
                    # std::string()
                    frame_token = frame_token.astOperand2

                frame = self.th.find_frame_type(frame_token)

                if frame:
                    var_token = None

                    if self.is_match(paren_token.astParent, '='):
                        var_token = paren_token.astParent.astOperand1
                    else:
                        var_token = self.get_comma_separated_token_at_pose_from_right(paren_token, 2)

                    if var_token:
                        (var_token, var_name) = self.get_var_token_and_var_name(var_token)
                        self.th.set_frame_type_for_variable_token(var_token, var_name, frame)

                        if var_token.variable:
                            var_token.variable.isParam = True

        elif token.str in ['getParam', 'getParamCached'] or \
                (token.str in ['get', 'getCached'] and self.is_match(token.previous, '::') and self.is_match(token.previous.previous, 'param')):

            if token.astParent and token.astParent.str in ['.', '::'] and self.is_match(token.astParent.astParent, '('):
                paren_token = token.astParent.astParent

                if self.get_count_of_function_arguments(paren_token) == 2:
                    var_token = self.get_comma_separated_token_at_pose_from_right(paren_token, 1)

                    if var_token:
                        (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                        if var_token and var_token.variable and self.sh.get_frame_count_by_ros_type_of_variable(var_token.variable) > 0:
                            if ('.frame_id' in var_name) or var_name.endswith('header') or \
                                    ('.child_frame_id' in var_name) or \
                                    var_name.endswith(var_token.variable.nameToken.str):

                                var_token.variable.is_frame_set = True


    def annotate_frame_ids_in_function_call(self, token, left_token, right_token):

        func = None
        paren_token = None

        if token.function and token != token.function.tokenDef:
            # FUNCTION CALL
            func = token.function
            
            if self.is_match(token.next, '('):
                paren_token = token.next
            elif self.is_match(token.next, '<') and self.is_match(token.next.link, '>') and self.is_match(token.next.link.next, '('):
                paren_token = token.next.link.next

        elif token.str == '(' and token.previous:
            paren_token = token
            token = token.previous
            if token.str == '>' and self.is_match(token.link, '<') and token.link.previous:
                token = token.link.previous
            
            if (not token.function and not token.varId) and paren_token.astOperand2:
                # DUMP COULD NOT IDENTIFY FUNCTION OBJECT FOR THE TOKEN
                func_list = self.sh.get_func_list_by_name(token.str)

                if func_list:
                    args_list = self.get_function_arguments(paren_token)
                    args_type_list = []
                    for i, arg in enumerate(args_list):
                        (arg_var, arg_name) = self.get_var_token_and_var_name(arg)
                        if arg_var and arg_var.variable:
                            arg_type = self.sh.find_sanitized_variable_type(arg_var.variable)
                            args_type_list.append(arg_type)
                        else:
                            args_type_list.append(None)
                    
                    for f in func_list:
                        if len(args_list) != len(f.arg_frames):
                            continue

                        no_match = False
                        for nr, var in f.argument.items():
                            if not var:
                                continue
                            class_name = self.sh.find_variable_type(var)
                            arg_type = args_type_list[int(nr)-1]
                            if arg_type and arg_type not in class_name:
                                no_match = True
                                break

                        # IF MATCH IS NOT FOUND, BECAUSE FIELD'S DATA-TYPE IS NOT AVAILABLE, 
                        # BUT ONLY ONE FUNCTION OBJECT IS PRESENT FOR THE NAME, THEN ASSIGN THAT OBJECT  
                        if (not no_match) or len(func_list)==1:
                            func = f
                            token.function = func
                            break

        if func:
            if self.is_match(paren_token, '('):
                args_list = self.get_function_arguments(paren_token)

                # TO AVOID VARIABLE ARG FUNCTIONS LIKE PRINTF
                if len(args_list) > len(func.arg_frames):
                    return

                for i, arg in enumerate(args_list):
                    frame = self.th.find_frame_type(arg, ret_def=True)
                    if frame:
                        func.arg_frames[i].append(frame)

                        # IF RETURN IS AN ARG VAR, THEN PROPAGATE ARG FRAME TO FUNCTION TOKEN
                        if (func.return_arg_var_nr > 0) and (i == func.return_arg_var_nr-1):
                            token.frames.append(frame)

                    if True:
                        # IDENTIFY IF ARG IS PASSED BY NON-CONST REFERENCE, IF YES, ASSUME THAT CALLED FUNCTION SETS ARG'S FRAME
                        (arg_var, arg_name) = self.get_var_token_and_var_name(arg)
                        if not (arg_var and arg_var.variable):
                            continue

                        arg_type = self.sh.find_sanitized_variable_type(arg_var.variable)
 
                        for nr, var in func.argument.items():
                            if not var:
                                continue

                            if int(nr) == i+1:
                                isConst = self.is_match(var.typeStartToken.previous, 'const')
                                class_name = self.sh.find_variable_type(var)

                                if arg_type not in class_name:
                                    break

                                if str(class_name).endswith('&'):
                                    class_name = class_name.replace('&', '')

                                if str(class_name).endswith('ConstPtr'):
                                    pass
                                elif str(class_name).endswith('Ptr'):
                                    arg_var.variable.is_frame_set = True
                                    break

                                if str(class_name).startswith('shared_ptr<') and str(class_name).endswith('>'):
                                    class_name = class_name.replace('shared_ptr<', '')
                                    class_name = self.sh.rreplace(class_name, '>', '', 1)

                                    if str(class_name).endswith('const'):
                                        pass
                                    else:
                                        arg_var.variable.is_frame_set = True
                                        break

                                if (var.isReference or var.isPointer) and (not isConst):
                                    arg_var.variable.is_frame_set = True
                                    break

                                break

            if not func.return_type:
                # FIND RETURN TYPE FROM FUNCTION DEF TOKEN
                def_token = func.tokenDef
                if def_token.astParent:
                    ret_type = None
                    if def_token.astParent.str == '(' and def_token == def_token.astParent.astOperand1:
                        ret_type = def_token.previous.str if def_token.previous else None
                    elif def_token == def_token.astParent.astOperand2:
                        ret_type = self.sh.recursively_visit(def_token.astParent.astOperand1)
                        ret_type += def_token.astParent.str
                        t = def_token.astParent.next
                        while (t != def_token):
                            ret_type += t.str
                            t = t.next
                    if ret_type:
                        ret_type = self.sh.sanitize_class_name(ret_type)
                        func.return_type = ret_type


    def annotate_object_construction_by_copy(self, token, left_token, right_token):
        if token.str == '(' and left_token and right_token:

            (left_token, left_name) = self.get_var_token_and_var_name(left_token)

            if left_token and left_token.variable:
                right_type = None
                is_right_function = False
                is_copy = False

                (right_token, right_name) = self.get_var_token_and_var_name(right_token)

                if right_token and right_token.variable:
                    right_type = self.sh.find_sanitized_variable_type(right_token.variable)
                    is_copy = True

                elif right_token.str == '(' and right_token.previous and right_token.previous.function:
                    right_type = right_token.previous.function.return_type
                    is_right_function = True

                elif right_token.str == 'new':
                    is_copy = True

                frame = self.th.find_frame_type(right_token)

                if (self.sh.find_sanitized_variable_type(left_token.variable) == right_type) or is_copy:
                    # or right_token.variable:
                    # OR condition to support fields of ros variables whose type is not available
                    # it is now handled by is_copy                 

                    if frame:
                        self.th.set_frame_type_for_variable_token(left_token, left_name, frame)
                    elif is_right_function and (not right_token.previous.function.isAnnotated):
                        left_token.variable.is_frame_set = True
                    elif self.is_frame_set:
                        left_token.variable.is_frame_set = True
                        self.is_frame_set = False


    # pointer-variable = new data-type(value)
    def annotate_object_construction_by_new(self, token, left_token, right_token):
        if token.str == 'new':

            if self.is_match(left_token, '(') and left_token.astOperand2:
                frame = self.th.find_frame_type(left_token.astOperand2)
                if frame:
                    token.frames.append(frame)


    # (type) x
    def annotate_object_type_cast(self, token, left_token, right_token):
        if token.str == '(' and left_token and (not right_token):

            # CHECK if ( is before or after left_token; for type-cast it should be before
            paren_linenr = int(token.linenr)
            isBefore = True

            if int(left_token.linenr) < paren_linenr:
                isBefore = False
            elif int(left_token.linenr) > paren_linenr:
                #isBefore = True
                pass
            else:
                t = left_token
                while t.next and int(t.next.linenr)==paren_linenr:                
                    if t.next == token:
                        isBefore = False
                        break
                    t = t.next

            if isBefore:
                frame = self.th.find_frame_type(left_token)
                if frame:
                    token.frames.append(frame)


    # <>::make_shared<T>(var)
    def annotate_pointers(self, token, left_token, right_token):
        if token.str == '(' and left_token and right_token:

            if left_token.str in ['::', '.'] and left_token.astOperand2:
                left_token = left_token.astOperand2

            if left_token.str in ['make_shared', 'shared_ptr', 'scoped_ptr']:
                frame = self.th.find_frame_type(right_token)
                if frame:
                    token.frames.append(frame)

            elif left_token.str == 'reset':
                var_token = left_token.astParent.astOperand1
                (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                if var_token and var_token.variable:
                    var_type = self.sh.find_variable_type(var_token.variable)

                    if 'ptr' in var_type.lower():
                        args_cnt = self.get_count_of_function_arguments(token)
                        right_token = self.get_comma_separated_token_at_pose_from_right(token, args_cnt)
                
                        frame = self.th.find_frame_type(right_token)
                        if frame:
                            self.th.set_frame_type_for_variable_token(var_token, var_name, frame)


    # TERNARY OPERATOR
    # cond ? true_part : false_part
    def annotate_ternary(self, token, left_token, right_token):
        if token.str == '?' and left_token and self.is_match(right_token, ':'):

            lframe = self.th.find_frame_type(right_token.astOperand1)
            rframe = self.th.find_frame_type(right_token.astOperand2)

            if lframe:
                token.frames.append(lframe)
            elif rframe:
                token.frames.append(rframe)
                                   

    # return x
    def annotate_function_return(self, token, left_token, right_token):
        if token.str == 'return' and left_token:

            frame = self.th.find_frame_type(left_token, ret_def=False)
            ret_type = self.sh.find_sanitized_variable_type(left_token.variable) if left_token.variable else None

            if frame or ret_type:
                # workaround; later on add edges from set to get functions in the function graph in type_analyzer
                isOnlyStatement = False

                isFunScope = False
                scope = token.scope
                while scope:
                    if scope.type == 'Function':
                        isFunScope = True
                        break
                    scope = scope.nestedIn

                if isFunScope and scope.function:
                    # check if return is the only statement; i.e. check if it is a get function
                    if scope.classStart == token.previous:
                        isOnlyStatement = True

                    if frame:
                        scope.function.return_frames.append(frame)
                    if ret_type:
                        scope.function.return_type = ret_type

                    if (not isOnlyStatement):
                        scope.function.isAnnotated = True
            
                if left_token.variable and left_token.variable.isArgument and isFunScope:
                    fun = scope.function

                    for argnr, arg in fun.argument.items():
                        if arg == left_token.variable:
                            break

                    scope.function.return_arg_var_nr = eval(argnr)

                if (not isOnlyStatement) and left_token.variable:
                    # Do not check frame for variable being returned, as it's frame may be set in the calling function
                    left_token.variable.checkFrame = False


    # ros::Publisher::publish(msg)
    def annotate_publish_message(self, token, left_token, right_token):

        if token.str == 'publish' and \
                token.astParent and self.is_match(token.astParent.astParent, '('):

            var_token = token.astParent.astOperand1
            paren_token = token.astParent.astParent

            (var_token, var_name) = self.get_var_token_and_var_name(var_token)

            if var_token and var_token.variable:
                var_type = self.sh.find_sanitized_variable_type(var_token.variable)

                if 'ros::Publisher' in var_type:
                    arg = self.get_comma_separated_token_at_pose_from_right(paren_token, 1)

                    if arg:
                        checkFrame = False
                        frame = None

                        if arg.str == '(' and arg.previous and arg.previous.function:
                            # msg may be a function call returning a msg

                            if arg.previous.function.isAnnotated and self.sh.get_frame_count_by_ros_type_of_function(arg.previous.function) > 0:
                                checkFrame = True
                                frame = self.th.find_frame_type(arg)

                        token.frames.append(checkFrame)
                        token.frames.append(frame)


    # tf lookupTransfom
    # a) lookupTransform (target_frame, source_frame, , stransform_out)
    # b) lookupTransform (target_frame, , source_frame, , fixed_frame, stransform_out) 
    def annotate_lookup_transform(self, token, left_token, right_token):

        if token.str == 'lookupTransform' and \
                token.astParent and self.is_match(token.astParent.astParent, '('):

            paren_token = token.astParent.astParent

            args_cnt = self.get_count_of_function_arguments(paren_token)
            if args_cnt not in [3, 4, 5, 6]:
                return

            tgt_frame = None
            src_frame = None

            # SET TYPE FOR TOKEN 

            if args_cnt in [3, 4]:
                tgt = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt)
                src = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt-1)

                tgt_frame = self.th.find_frame_type(tgt)
                src_frame = self.th.find_frame_type(src)

                tgt_frame = tgt_frame[-1] if tgt_frame else None
                src_frame = src_frame[-1] if src_frame else None
                
                token.frames.append([tgt_frame, src_frame])

            elif args_cnt in [5, 6]:
                tgt = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt)
                fix = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt-4)
                src = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt-2)

                tgt_frame = self.th.find_frame_type(tgt)
                fix_frame = self.th.find_frame_type(fix)
                src_frame = self.th.find_frame_type(src)

                tgt_frame = tgt_frame[-1] if tgt_frame else None
                fix_frame = fix_frame[-1] if fix_frame else None
                src_frame = src_frame[-1] if src_frame else None

                token.frames.append([tgt_frame, fix_frame, src_frame])

            # SET TYPE FOR TRANSFORM VARIABLE

            stf = self.get_comma_separated_token_at_pose_from_right(paren_token, 1)
            (stf, stf_name) = self.get_var_token_and_var_name(stf)

            # TO SUPPORT BOTH TF AND TF2
            if stf and self.sh.is_ros_transform_type(stf.variable):
                self.th.set_frame_type_for_variable_token(stf, stf_name, [tgt_frame, src_frame])

                if self.is_frame_set:
                    stf.variable.is_frame_set = True
                    self.is_frame_set = False
                

    def annotate_transform_object(self, token, left_token, right_token):
        if token.str in ['transformPoint', 'transformPointCloud', 'transformPose', 'transformQuaternion', 'transformVector'] and \
                token.astParent and self.is_match(token.astParent.astParent, '('):

            paren_token = token.astParent.astParent

            args_cnt = self.get_count_of_function_arguments(paren_token)
            if args_cnt not in [3, 5]:
                return

            tgt_frame = None
            src_frame = None

            # SET TYPE FOR TOKEN 

            if args_cnt in [3]:
                tgt = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt)
                src = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt-1)

                tgt_frame = self.th.find_frame_type(tgt)
                src_frame = self.th.find_frame_type(src)

                tgt_frame = tgt_frame[-1] if tgt_frame else None
                src_frame = src_frame[-1] if src_frame else None
                
                token.frames.append([tgt_frame, src_frame])

            elif args_cnt in [5]:
                tgt = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt)
                fix = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt-3)
                src = self.get_comma_separated_token_at_pose_from_right(paren_token, args_cnt-2)

                tgt_frame = self.th.find_frame_type(tgt)
                fix_frame = self.th.find_frame_type(fix)
                src_frame = self.th.find_frame_type(src)

                tgt_frame = tgt_frame[-1] if tgt_frame else None
                fix_frame = fix_frame[-1] if fix_frame else None
                src_frame = src_frame[-1] if src_frame else None

                token.frames.append([tgt_frame, fix_frame, src_frame])

            # SET TYPE FOR OUT VARIABLE

            stf = self.get_comma_separated_token_at_pose_from_right(paren_token, 1)
            (stf, stf_name) = self.get_var_token_and_var_name(stf)

            # TO SUPPORT BOTH TF AND TF2
            if stf and self.sh.is_ros_type(stf.variable):
                self.th.set_frame_type_for_variable_token(stf, stf_name, [tgt_frame])

                if self.is_frame_set:
                    stf.variable.is_frame_set = True
                    self.is_frame_set = False


    # tf sendTransform
    # tf::TransformBroadcaster::sendTransform(transform)
    # tf::TransformBroadcaster::sendTransform(std::vector transforms)
    def annotate_send_transform(self, token, left_token, right_token):
        # CONSTRUCT FRAME TREE

        if token.str == 'sendTransform' and \
                self.is_match(token.next, '(') and token.next.astOperand2:

            if dd.COLLECT_STATS:
                dd.TOTAL_SEND_TF_COUNT += 1

            frame = self.th.find_frame_type(token.next.astOperand2)
            
            if frame:
                token.frames.append(frame)

            #TODO support vector of transforms


    # tf::Stamped<T> (T, time, frame_id)
    def annotate_tf_stamped_construction(self, token, left_token, right_token):
        if token.str == '(' and token.previous:

            # VARIABLE INITIALIZER
            if token.previous.variable:        
                var_type = self.sh.find_sanitized_variable_type(token.previous.variable)
                if 'tf::stamped' not in var_type.lower():
                    return

            # CONSTRUCTOR
            elif token.previous.str == '>':
                if not (self.is_match(token.astOperand1, '::') and \
                        self.is_match(token.astOperand1.previous, 'tf') and \
                        self.is_match(token.astOperand1.next, 'Stamped')):
                    return

            else:
                return

            args_cnt = self.get_count_of_function_arguments(token)
            if args_cnt != 3:
                return

            f = self.get_comma_separated_token_at_pose_from_right(token, 1)
            frame = self.th.find_frame_type(f)

            if frame:
                if token.previous.variable:
                    self.th.set_frame_type_for_variable_token(token.previous, token.previous.str, frame)
                else: 
                    token.astOperand1.next.frames.append(frame)
            elif self.is_frame_set:
                if token.previous.variable:
                    token.previous.variable.is_frame_set = True
                    self.is_frame_set = False


    # tf StampedTransform constructor
    # tf::StampedTransform(transform_in, , frame_id, child_frame_id)
    def annotate_stamped_transform_construction(self, token, left_token, right_token):
        if token.str == '(' and token.previous:

            # VARIABLE INITIALIZER
            if token.previous.variable:        
                var_type = self.sh.find_sanitized_variable_type(token.previous.variable)
                if 'stampedtransform' not in var_type.lower():
                    return

            # CONSTRUCTOR
            elif token.previous.str != 'StampedTransform':
                return

            args_cnt = self.get_count_of_function_arguments(token)
            if args_cnt != 4:
                return

            f = self.get_comma_separated_token_at_pose_from_right(token, 2)
            cf = self.get_comma_separated_token_at_pose_from_right(token, 1) 

            f_frame = self.th.find_frame_type(f)
            cf_frame = self.th.find_frame_type(cf)

            f_frame = f_frame[-1] if f_frame else None
            cf_frame = cf_frame[-1] if cf_frame else None
            checkFrame = False

            if f_frame and cf_frame:
                tf = self.get_comma_separated_token_at_pose_from_right(token, 4)
                tf_frame = self.th.find_frame_type(tf)

                #TODO resolve tf_frame in type-checker, if len(tf_frame)==1 with variable tuple in frame_id;
                #TODO annotate both frame and tf_frame
                if tf_frame and len(tf_frame)==2:

                    #print "F_FRAME: %s: %s" % (token.linenr, f_frame)
                    #print "CF_FRAME: %s: %s" % (token.linenr, cf_frame)
                    #print "TF_FRAME: %s: %s" % (token.linenr, tf_frame)

                    tf_f_frame = tf_frame[0]
                    tf_cf_frame = tf_frame[1]

                    if tf_f_frame and tf_cf_frame:
                        cf_dir = self.th.find_childframe_orientation([f_frame.x_dir, f_frame.y_dir, f_frame.z_dir],
                                                                     [[tf_f_frame.x_dir, tf_f_frame.y_dir, tf_f_frame.z_dir],
                                                                      [tf_cf_frame.x_dir, tf_cf_frame.y_dir, tf_cf_frame.z_dir]])

                        if len(cf_dir) == 3:
                            (cf_x_dir, cf_y_dir, cf_z_dir) = tuple(cf_dir)
                            cf_frame = (self.th.create_frame_type(cf_frame.id, cf_x_dir, cf_y_dir, cf_z_dir))[-1]
                            self.th.set_frame_orientation(cf_frame.id, (cf_x_dir, cf_y_dir, cf_z_dir))

                        checkFrame = True

                    #print "CF_FRAME_2: %s: %s" % (token.linenr, cf_frame)

            frame = [f_frame, cf_frame]

            if token.previous.variable:
                self.th.set_frame_type_for_variable_token(token.previous, token.previous.str, frame)
                if token.previous.previous and token.previous.previous.str == 'StampedTransform':
                    token.previous.previous.frames.append(checkFrame)
                    token.previous.previous.frames.append(frame)

                if self.is_frame_set:
                    token.previous.variable.is_frame_set = True
                    self.is_frame_set = False

            elif token.previous.str == 'StampedTransform':
                token.previous.frames.append(checkFrame)
                token.previous.frames.append(frame)


    #TODO translation frame type
    # tf Transform
    # tf::Transform(Matrix3x3 rotation, Vector3 translation = default_value)
    def annotate_transform_construction(self, token, left_token, right_token):
        if token.str == '(' and token.previous:

            # VARIABLE INITIALIZER
            if token.previous.variable:        
                var_type = self.sh.find_sanitized_variable_type(token.previous.variable)
                if ('transform' not in var_type.lower()) or ('stampedtransform' in var_type.lower()):
                    return

            # CONSTRUCTOR
            elif token.previous.str != 'Transform':
                return

            args_cnt = self.get_count_of_function_arguments(token)    
            t_rot = self.get_comma_separated_token_at_pose_from_right(token, args_cnt)

            frame = self.th.find_frame_type(t_rot)
            if (not frame):
                frame = self.th.get_default_transform_frame_type()
                return

            if token.previous.variable:
                self.th.set_frame_type_for_variable_token(token.previous, token.previous.str, frame)
            elif token.previous.str == 'Transform':
                token.previous.frames.append(frame)


    def annotate_quaternion_construction(self, token, left_token, right_token):
        if token.str == '(' and token.previous:

            # VARIABLE INITIALIZER
            if token.previous.variable:        
                var_type = self.sh.find_sanitized_variable_type(token.previous.variable)
                if 'quaternion' not in var_type.lower():
                    return

            # CONSTRUCTOR
            elif token.previous.str != 'Quaternion':
                return

            frame = None
            val = None

            if token.previous.variable:
                val = token.previous.variable.vals.get('vec')
            elif token.vals:
                val = token.vals[-1]

            if val and len(val) == 4 and (None not in val):
                orient = self.th.find_orientation_type(val, 'Q')
                        
                if orient:
                    frame = self.th.create_frame_type('xyz', orient[0][0], orient[0][1], orient[0][2])
                    to_frame = self.th.create_frame_type('xyz', orient[1][0], orient[1][1], orient[1][2])
                    frame.extend(to_frame)

            if not frame and (self.get_count_of_function_arguments(token) == 4): #(x,y,z,w); avoid 3 euler args 
                frame_dirs = self.get_frame_dirs_from_3_args(token)

                if len(frame_dirs) == 3:
                    frame = self.th.create_frame_type('xyz', frame_dirs[0], frame_dirs[1], frame_dirs[2])
                    to_frame = self.th.get_default_frame_type()
                    frame.extend(to_frame)

            if frame:
                if token.previous.variable:
                    self.th.set_frame_type_for_variable_token(token.previous, token.previous.str, frame)
                elif token.previous.str == 'Quaternion':
                    token.previous.frames.append(frame)


    def get_frame_dirs_from_3_args(self, paren_token):
        elements = self.get_function_arguments(paren_token)
        frame_dirs = []

        if len(elements) == 4:
            del elements[-1]

        if len(elements) == 3:

            for elem in elements:
                #TODO consider the input data's frame for deciding the actual xyz?
                frame_dirs.append(self.extract_dir_text(elem))

            if frame_dirs.count('') > 0:
                return []

            # TO AVOID THE VALUE (0,0,0): HANDLED IN EXTRACT_DIR_TEXT
            #if frame_dirs.count('0') == 3:
            #    return []

            frame_dirs = self.translate_to_xyz(frame_dirs)
        
        return frame_dirs


    # tf vector constructor
    def annotate_vector3(self, token, left_token, right_token):
        if token.str == '(' and token.previous:

            # VARIABLE INITIALIZER
            if token.previous.variable:        
                var_type = self.sh.find_sanitized_variable_type(token.previous.variable)
                if 'vector3' not in var_type.lower():
                    return

            # CONSTRUCTOR
            elif token.previous.str != 'Vector3':
                return

            if self.is_match(right_token, ','):
                frame_dirs = self.get_frame_dirs_from_3_args(token)

                if len(frame_dirs) == 3:
                    frame = self.th.create_frame_type('xyz', frame_dirs[0], frame_dirs[1], frame_dirs[2])
                    to_frame = self.th.get_default_frame_type()
                    frame.extend(to_frame)

                    if token.previous.variable:
                        self.th.set_frame_type_for_variable_token(token.previous, token.previous.str, frame)
                    elif token.previous.str == 'Vector3':
                        token.previous.frames.append(frame)


    def get_frame_dirs_from_9_args(self, paren_token):
        elements = self.get_function_arguments(paren_token)
        frame_dirs = []

        if len(elements) == 9:                       
            # 3x3 MATRIX ROW MAJOR WITH ONLY ONE NON-ZERO IN ROW AND IN COLUMN
            j = 0
            found_nonzero = False
                
            for elem in elements:

                if elem.str not in ['0', '1', '-1']:
                    # MATRIX SHOULD HAVE ONLY 0, 1, -1
                    break

                if not elem.isInt:
                    break

                j += 1

                if int(elem.str):                        
                    if found_nonzero:
                        # MORE THAN ONE NON-ZERO IN A ROW
                        break
                    else:
                        frame_dirs.append(self.th.get_vector_dir(j-1, elem.str))
                        found_nonzero = True

                if j == 3:
                    if not found_nonzero:
                        # NO NON-ZERO IN A ROW
                        break
                    j = 0
                    found_nonzero = False

        return frame_dirs


    # tf matrix constructor
    def annotate_matrix3x3(self, token, left_token, right_token):
        if token.str == '(' and token.previous:
            
            # VARIABLE INITIALIZER
            if token.previous.variable:
                var_type = self.sh.find_sanitized_variable_type(token.previous.variable)
                if 'matrix' not in var_type.lower():
                    return

            #CONSTRUCTOR
            elif token.previous.str != 'Matrix3x3':
                return
                
            frame = None
            frame_dirs = []

            if self.is_match(right_token, ','):
                frame_dirs = self.get_frame_dirs_from_9_args(token)

            if len(frame_dirs) == 3:
                frame = self.th.create_frame_type('xyz', frame_dirs[0], frame_dirs[1], frame_dirs[2])
                to_frame = self.th.get_default_frame_type()
                frame.extend(to_frame)
            else:
                val = None
                if token.previous.variable:
                    val = token.previous.variable.vals.get('vec')
                elif token.vals:
                    val = token.vals[-1]

                if val and len(val) == 9:
                    orient = self.th.find_orientation_type(val, 'M')
                        
                    if orient:
                        frame = self.th.create_frame_type('xyz', orient[0][0], orient[0][1], orient[0][2])
                        to_frame = self.th.create_frame_type('xyz', orient[1][0], orient[1][1], orient[1][2])
                        frame.extend(to_frame)

            if frame:                                            
                if token.previous.variable:
                    self.th.set_frame_type_for_variable_token(token.previous, token.previous.str, frame)
                    self.tfMatrixIds.append(token.previous.variable.Id)
                elif token.previous.str == 'Matrix3x3':
                    token.previous.frames.append(frame)
                    self.tfMatrixIds.append(token.previous.Id) 


    # transform.setIdentity()
    # matrix.setIdentity()
    def annotate_set_identity(self, token, left_token, right_token):
        if token.str == 'setIdentity' and \
                self.is_match(token.previous, '.') and token.previous.astOperand1:

            (var_token, var_name) = self.get_var_token_and_var_name(token.previous.astOperand1)
            frame = self.th.get_default_transform_frame_type()
            self.th.set_frame_type_for_variable_token(var_token, var_name, frame)


    # transform.setOrigin()
    def annotate_set_origin(self, token, left_token, right_token):
        if token.str == 'setOrigin' and \
                self.is_match(token.next, '(') and token.next.astOperand2:

            frame = self.th.find_frame_type(token.next.astOperand2)
            if (not frame):
                #frame = self.th.get_default_transform_frame_type()
                return
 
            if self.is_match(token.previous, '.') and token.previous.astOperand1:
                (tf_var, tf_var_name) = self.get_var_token_and_var_name(token.previous.astOperand1)
                self.th.set_frame_type_for_variable_token(tf_var, tf_var_name, frame)


    # transform.setBasis()
    # transform.setRotation()
    # matrix.setRotation()
    def annotate_set_basis_and_rotation(self, token, left_token, right_token):
        if (token.str == 'setBasis' or token.str == 'setRotation') and \
                self.is_match(token.next, '(') and token.next.astOperand2:

            frame = self.th.find_frame_type(token.next.astOperand2)
            if (not frame):
                frame = self.th.get_default_transform_frame_type()
                return
 
            if self.is_match(token.previous, '.') and token.previous.astOperand1:
                (tf_var, tf_var_name) = self.get_var_token_and_var_name(token.previous.astOperand1)
                self.th.set_frame_type_for_variable_token(tf_var, tf_var_name, frame)


    # ...
    def annotate_set_euler_rotation_and_fixed_rotation(self, token, left_token, right_token):
        if (token.str.startswith('setEuler') or token.str == 'setRPY') and \
                self.is_match(token.previous, '.') and token.previous.astOperand1:

            (var_token, var_name) = self.get_var_token_and_var_name(token.previous.astOperand1)
            if var_token and var_token.variable and var_token.variable.vals:
                if 'vec' in var_token.variable.vals:
                    val = var_token.variable.vals['vec']
                    if val and len(val) == 4: #quaternion
                        val = self.th.quat_to_matrix(val, flatten=True)
                    
                    if val and len(val) == 9: #matrix, or converted quaternion
                        orient = self.th.find_orientation_type(val, 'M')
                        
                        if orient:
                            frame = self.th.create_frame_type('xyz', orient[0][0], orient[0][1], orient[0][2])
                            to_frame = self.th.create_frame_type('xyz', orient[1][0], orient[1][1], orient[1][2])
                            frame.extend(to_frame)

                            self.th.set_frame_type_for_variable_token(var_token, var_name, frame)


    # vector.setValue()
    # matrix.setValue()
    # quaternion.setValue() #TODO
    def annotate_set_value(self, token, left_token, right_token):
        if token.str == 'setValue' and \
                self.is_match(token.next, '(') and token.next.astOperand2 and \
                self.is_match(token.previous, '.') and token.previous.astOperand1:

            (var_token, var_name) = self.get_var_token_and_var_name(token.previous.astOperand1)
            if var_token and var_token.variable:
                var_type = self.sh.find_sanitized_variable_type(var_token.variable)

                frame = None
                frame_dirs = []

                if 'vector3' in var_type.lower():
                    frame_dirs = self.get_frame_dirs_from_3_args(token.next)
                elif 'matrix' in var_type.lower():
                    frame_dirs = self.get_frame_dirs_from_9_args(token.next)

                if len(frame_dirs)==3:
                    frame = self.th.create_frame_type('xyz', frame_dirs[0], frame_dirs[1], frame_dirs[2])
                    to_frame = self.th.get_default_frame_type()
                    frame.extend(to_frame)
                else:
                    if 'matrix' in var_type.lower():
                        val = var_token.variable.vals.get('vec')
                        if val and len(val) == 9:
                            orient = self.th.find_orientation_type(val, 'M')
                        
                            if orient:
                                frame = self.th.create_frame_type('xyz', orient[0][0], orient[0][1], orient[0][2])
                                to_frame = self.th.create_frame_type('xyz', orient[1][0], orient[1][1], orient[1][2])
                                frame.extend(to_frame)

                if frame: 
                    self.th.set_frame_type_for_variable_token(var_token, var_name, frame)


    #TODO vector.<setX, setY, setZ>
    #TODO quaternion.<setX, setY, setZ>


    #TODO check if frame id and child frame id are already set, and then set appropriate frame type
    # stampedTransform.setData()
    def annotate_set_data(self, token, left_token, right_token):
        pass


    #TODO vector.<getX, getY, getZ, x, y, z>?
    #TODO quaternion.<getX, getY, getZ, x, y, z>?


    #TODO matrix get functions
    def annotate_get_functions(self, token, left_token, right_token):
        if token.str == '(' and left_token and left_token.astOperand1 and left_token.astOperand2:
            func_token = left_token.astOperand2
            frame = None

            if func_token.str == 'getIdentity':
                frame = self.th.get_default_transform_frame_type()
                
            elif func_token.str == 'getRotation' or func_token.str == 'getBasis':
                (var_token, var_name) = self.get_var_token_and_var_name(left_token.astOperand1)
                if var_token and var_token.variable:
                    val = var_token.variable.vals.get('rot')
                    if val and len(val) == 4:
                        orient = self.th.find_orientation_type(val, 'Q')
                        
                        if orient:
                            frame = self.th.create_frame_type('xyz', orient[0][0], orient[0][1], orient[0][2])
                            to_frame = self.th.create_frame_type('xyz', orient[1][0], orient[1][1], orient[1][2])
                            frame.extend(to_frame)

            if frame:
                func_token.frames.append(frame)


    # handle other multiplication operations too
    def annotate_matrix_multiplication(self, token, left_token, right_token):
        if token.str == '*' and token.isArithmeticalOp:
            if (not left_token) or (not right_token):
                return

            left_matrix = False
            right_matrix = False
            isTfMatrix = False
            
            # LEFT OPERAND
            (left_var, left_name) = self.get_var_token_and_var_name(left_token)
            if left_var and left_var.variable:
                left_type = self.sh.find_sanitized_variable_type(left_var.variable)
                if 'matrix' in left_type.lower():
                    left_matrix = True
                    if left_var.variable.Id in self.tfMatrixIds:
                        isTfMatrix = True

            elif self.is_match(left_token, '(') and self.is_match(left_token.previous, 'Matrix3x3'):
                left_matrix = True
                if left_token.previous.Id in self.tfMatrixIds:
                    isTfMatrix = True

            # LEFT OPERAND IS MATRIX
            if left_matrix:
                left_frame = self.th.find_frame_type(left_token)

                if left_frame:
                    (right_var, right_name) = self.get_var_token_and_var_name(right_token)

                    if right_var and right_var.variable:
                        right_frame = self.th.get_frame_type_for_variable_token(right_var, right_name)
                        right_type = self.sh.find_sanitized_variable_type(right_var.variable)

                        if not right_frame:
                            if 'matrix' in right_type.lower() or 'quaternion' in right_type.lower() or 'vector3' in right_type.lower():
                                right_frame = self.th.get_default_transform_frame_type()
                            #else:
                            #    right_frame = self.th.get_default_frame_type()  

                        frame = None
                        if isTfMatrix or 'matrix' in right_type.lower() or 'quaternion' in right_type.lower():
                            frame = self.th.multiply_by_tf_matrix(left_frame, right_frame)
                        elif 'vector3' in right_type.lower():
                            frame = self.th.multiply_by_matrix(left_frame, right_frame)

                        if frame:
                            token.frames.append(frame)

            elif right_matrix:
                #TODO right_matrix
                pass

            else:
                left_frame = self.th.find_frame_type(left_token)
                right_frame = self.th.find_frame_type(right_token)

                if left_frame and len(left_frame) == 2 and self.th.is_default_frame_type(left_frame) and (not right_frame):
                     (right_var, right_name) = self.get_var_token_and_var_name(right_token)
                     if right_var and right_var.variable:
                         right_type = self.sh.find_sanitized_variable_type(right_var.variable)
                         if 'matrix' in right_type.lower() or 'quaternion' in right_type.lower():
                             right_frame = self.th.get_default_transform_frame_type()

                frame = self.th.multiply_frame_types(left_frame, right_frame)
                if frame:
                    token.frames.append(frame)


    #matrix.transpose()
    def annotate_matrix_transpose(self, token, left_token, right_token):
        if token.str == 'transpose' and \
                self.is_match(token.next, '(') and \
                self.is_match(token.previous, '.') and token.previous.astOperand1:

            (var, var_name) = self.get_var_token_and_var_name(token.previous.astOperand1)
            if var and var.variable:
                var_type = self.sh.find_sanitized_variable_type(var.variable)
                if 'matrix' not in var_type.lower():
                    return

            var_frame = self.th.find_frame_type(token.previous.astOperand1)

            if var_frame:
                frame = self.th.transpose_frame_type(var_frame)
                token.frames.append(frame)


    #matrix.inverse()
    #transform.inverse()
    def annotate_inverse(self, token, left_token, right_token):
        if token.str == 'inverse' and \
                self.is_match(token.next, '(') and \
                self.is_match(token.previous, '.') and token.previous.astOperand1:

            (var, var_name) = self.get_var_token_and_var_name(token.previous.astOperand1)
            if var and var.variable:
                var_type = self.sh.find_sanitized_variable_type(var.variable)
                if ('matrix' not in var_type.lower()) and ('transform' not in var_type.lower()):
                    return

            var_frame = self.th.find_frame_type(token.previous.astOperand1)

            if var_frame:
                frame = self.th.inverse_frame_type(var_frame)
                token.frames.append(frame)


    #tf2 doTransform(in, out, transform)
    def annotate_do_transform(self, token, left_token, right_token):
        if token.str == 'doTransform' and \
                token.astParent and self.is_match(token.astParent.astParent, '('):

            paren_token = token.astParent.astParent

            args_cnt = self.get_count_of_function_arguments(paren_token)
            if args_cnt != 3:
                return

            in_token = self.get_comma_separated_token_at_pose_from_right(paren_token, 3)
            tf_token = self.get_comma_separated_token_at_pose_from_right(paren_token, 1)

            in_frame = self.th.find_frame_type(in_token)
            tf_frame = self.th.find_frame_type(tf_token)

            f = tf_frame[0] if tf_frame else None
           
            out_token = self.get_comma_separated_token_at_pose_from_right(paren_token, 2)
            (out_var, out_name) = self.get_var_token_and_var_name(out_token)

            if out_var and out_var.variable:
                if self.sh.is_ros_transform_type(out_var.variable):
                    cf = in_frame[-1] if in_frame else None
                    self.th.set_frame_type_for_variable_token(out_var, out_name, [f, cf])
                else:
                    self.th.set_frame_type_for_variable_token(out_var, out_name, [f])

                if self.is_frame_set:
                    out_var.variable.is_frame_set = True
                    self.is_frame_set = False                
            
            #TODO annotate token and check if frame of in is equal to child_frame of transform
                

    #TODO other tf/tf2 api functions
    def annotate_create_quaternion_functions(self, token, left_token, right_token):
        if token.str.startswith('createQuaternion') and self.is_match(token.next, '(') and \
                token.next.vals:

            val = token.next.vals[-1]

            if val and len(val) == 4:     
                orient = self.th.find_orientation_type(val, 'Q')
                        
                if orient:
                    frame = self.th.create_frame_type('xyz', orient[0][0], orient[0][1], orient[0][2])
                    to_frame = self.th.create_frame_type('xyz', orient[1][0], orient[1][1], orient[1][2])
                    frame.extend(to_frame)
                    token.frames.append(frame)

        elif token.str == ('createIdentityQuaternion') and self.is_match(token.next, '('):

            frame = self.th.get_default_transform_frame_type()
            token.frames.append(frame)


    #TODO 
    #tf2::<>TF2ToMsg(transform, msg, , frame, child_frame)
    #tf2::<>TF2ToMsg(quat, vec, msg, , frame, child_frame)


    #tf::<>MsgToTF(msg, tf)
    #tf::<>TFToMsg(tf, msg)
    #tf2::<>MsgToTF2(msg, tf2)
    def annotate_msg_tf_functions(self, token, left_token, right_token):
        if (token.str.endswith('MsgToTF') or token.str.endswith('TFToMsg') or token.str.endswith('MsgToTF2')) \
                and self.is_match(token.next, '('):

            paren_token = token.next
            from_token = None
            to_token = None

            args_cnt = self.get_count_of_function_arguments(paren_token)
            
            if args_cnt == 2:
                from_token = self.get_comma_separated_token_at_pose_from_right(paren_token, 2)
                to_token = self.get_comma_separated_token_at_pose_from_right(paren_token, 1)

                frame = self.th.find_frame_type(from_token)

                if frame:
                    (to_token, to_name) = self.get_var_token_and_var_name(to_token)
                    if to_token and to_token.variable:
                        self.th.set_frame_type_for_variable_token(to_token, to_name, frame)

                
    def annotate_string_concatenation(self, token, left_token, right_token):
        if token.str == "+":
            isLeftString = False
            isRightString = False

            if self.is_match(left_token, '(') and self.is_match(left_token.previous, 'string'):
                # std::string()
                left_token = left_token.astOperand2
            if self.is_match(right_token, '(') and self.is_match(right_token.previous, 'string'):
                # std::string()
                right_token = right_token.astOperand2

            if left_token and right_token:
                if left_token.isString:
                    isLeftString = True
                else:
                    (left_var, left_name) = self.get_var_token_and_var_name(left_token)
                    if left_var and left_var.variable:
                        left_type = self.sh.find_sanitized_variable_type(left_var.variable)
                        if left_type in ['string','std::string', 'auto', 'char']:
                            isLeftString = True

                if right_token.isString:
                    isRightString = True
                else:
                    (right_var, right_name) = self.get_var_token_and_var_name(right_token)
                    if right_var and right_var.variable:
                        right_type = self.sh.find_sanitized_variable_type(right_var.variable)
                        if right_type in ['string','std::string', 'auto', 'char']:
                            isRightString = True

                if isLeftString or isRightString:
                    left_frame = self.th.find_frame_type(left_token)
                    right_frame = self.th.find_frame_type(right_token)
     
                    if (not left_frame) or (not right_frame):
                        return

                    left_id = self.th.get_frame_type_id(left_frame)
                    right_id = self.th.get_frame_type_id(right_frame)

                    if (not left_id) or (not right_id):
                        return

                    frame = self.th.create_frame_type_for_string(left_id + right_id)
                    if frame:
                        token.frames.append(frame)


    def annotate_string_functions(self, token, left_token, right_token):
        if token.str == '(':

            if self.is_match(token.previous, 'string'):
                # std::string(string)
                frame = self.th.find_frame_type(token.astOperand2)
                if frame:
                    token.previous.frames.append(frame)

            elif self.is_match(token.previous, 'c_str'):
                # string.c_str()
                if self.is_match(token.previous.astParent, '.'):
                    frame = self.th.find_frame_type(token.previous.astParent.astOperand1)
                    if frame:
                        token.previous.frames.append(frame)

            elif self.is_match(token.previous, 'str'):
                # stringstream.str(); stringstream.str(string)
                if self.is_match(token.previous.astParent, '.') and token.previous.astParent.astOperand1:
                    if token.astOperand2:
                        # stringstream.str(string)
                        frame = self.th.find_frame_type(token.astOperand2)
                        if frame:
                            (var_token, var_name) = self.get_var_token_and_var_name(token.previous.astParent.astOperand1)
                            self.th.set_frame_type_for_variable_token(var_token, var_name, frame)
                    else:
                        # stringstream.str()
                        frame = self.th.find_frame_type(token.previous.astParent.astOperand1)
                        if frame:
                            token.previous.frames.append(frame)

            elif self.is_match(token.previous, 'to_string'):
                # std::to_string(num)
                if token.astOperand2:
                    val = str(token.astOperand2.vals[-1]) if token.astOperand2.vals else 'yyyy'
                    frame = self.th.create_frame_type_for_string(val)
                    if frame:
                        token.previous.frames.append(frame)

            elif self.is_match(token.previous, 'toStdString'):
                # QString.toStdString()
               if self.is_match(token.previous.astParent, '.'):
                    frame = self.th.find_frame_type(token.previous.astParent.astOperand1)
                    if not frame:
                        frame = self.th.create_frame_type_for_string('zzzz')
                    if frame:
                        token.previous.frames.append(frame)
                    



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # VALUE ASSIGNMENT RULES
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def apply_and_propagate_values(self, root_token):
        # ASSUME THE TOKENS COME BACK AS A SORTED LIST
        break_point = 1000
        i=0
            
        self.tw.generic_recurse_and_apply_function(root_token, self.apply_number_values)
        self.tw.generic_recurse_and_apply_function(root_token, self.apply_variable_values)

        # CONTINUE TO ATTEMPT CHANGES UNTIL CHANGES CEASE
        while self.was_some_value_changed:  
            if i>break_point:
                s = "BREAKING WHILE LOOP AT %d" % break_point
                raise ValueError(s)
                return
            i+=1
            self.was_some_value_changed = False
            # LOOK FOR EARLY ABANDONMENT OF THIS AST
            if not self.found_values_in_this_tree:
                break
            ### PROPAGATE VALUES
            self.tw.generic_recurse_and_apply_function(root_token, self.propagate_values_across_typecast)
            self.tw.generic_recurse_and_apply_function(root_token, self.propagate_values_across_operators)
            self.tw.generic_recurse_and_apply_function(root_token, self.propagate_values_across_comma_connector)
            self.tw.generic_recurse_and_apply_function(root_token, self.propagate_values_across_tf_functions)
            self.tw.generic_recurse_and_apply_function(root_token, self.propagate_values_across_constructor)
            self.tw.generic_recurse_and_apply_function(root_token, self.propagate_values_across_dot_connector)
            self.tw.generic_recurse_and_apply_function(root_token, self.propagate_values_across_get_functions)
            self.tw.generic_recurse_and_apply_function(root_token, self.propagate_values_across_copy_constructor)
            self.tw.generic_recurse_and_apply_function(root_token, self.propagate_values_across_param)
            self.tw.generic_recurse_and_apply_function(root_token, self.propagate_values_across_assignment_operator)    
        # END -- WHILE LOOP


    def apply_number_values(self, token, left_token, right_token):
        val = None

        if token.isNumber:
            val = token.str
            val = val.lower().replace('f', '')
            val = val.lower().replace('u', '')
            val = val.lower().replace('l', '')

            try:
                val = float(val)
            except Exception,e:
                print "EXCEPTION: %s" % (str(e),)
                return

        elif token.str == 'M_PI':
            val = 3.14159
        elif token.str == 'M_PI_2':
            val = 1.5708
        elif token.str == 'M_PI_4':
            val = 0.7854
 
        if val is not None:
            token.vals.append(val)
            self.was_some_value_changed = True
            self.found_values_in_this_tree = True 
            

    def apply_variable_values(self, token, left_token, right_token):
        if token.variable:
            (var_token, var_name) = self.sh.find_compound_variable_token_and_name_for_variable_token(token)
            if not (var_token and var_token.variable):
                return

            val = None

            if 'num' in var_token.variable.vals:
                val = var_token.variable.vals['num']
            elif 'vec' in var_token.variable.vals:
                val = var_token.variable.vals['vec']
            # assignment of disp and rot values
            elif 'disp' in var_token.variable.vals or 'rot' in var_token.variable.vals:
                if 'transform.translation' in var_name:
                    # geometry_msgs::TransformStamped
                    if not ('disp' in var_token.variable.vals):
                        return

                    d = var_token.variable.vals['disp']
                    if var_name.endswith('.x'):
                        val = d[0]
                    elif var_name.endswith('.y'):
                        val = d[1]
                    elif var_name.endswith('.z'):
                        val = d[2]
                    elif var_name.endswith('.translation'):
                        val = var_token.variable.vals['disp']

                elif 'transform.rotation' in var_name:
                    # geometry_msgs::TransformStamped
                    if not ('rot' in var_token.variable.vals):
                        return

                    r = var_token.variable.vals['rot']
                    if var_name.endswith('.x'):
                        val = r[0]
                    elif var_name.endswith('.y'):
                        val = r[1]
                    elif var_name.endswith('.z'):
                        val = r[2]
                    elif var_name.endswith('.w'):
                        val = r[3]
                    elif var_name.endswith('.rotation'):
                        val = var_token.variable.vals['rot']

                else:
                    #if not('.header' in var_name) and not('frame_id' in var_name):
                    if not any(substr in var_name for substr in ['.header', 'frame_id']):
                        val = var_token.variable.vals

            if val is not None:
                token.vals.append(val)
                self.was_some_value_changed = True
                self.found_values_in_this_tree = True


    def update_token_value(self, token, val):
        if token.vals and (token.vals[-1] == val):
            return
        token.vals.append(val)
        self.was_some_value_changed = True


    def mult(self, a, b):
        return None if (a is None or b is None) else a*b 

    def add(self, a, b):
        return None if (a is None or b is None) else a+b

    def sub(self, a, b):
        return None if (a is None or b is None) else a-b

    def usub(self, a):
        return None if (a is None) else -a


    def dot(self, v1, v2):
        s = self.add(self.mult(v1[0],v2[0]), self.mult(v1[1],v2[1]))
        s = self.add(s, self.mult(v1[2],v2[2]))
        return s 


    def transform_mult_vector(self, t, v):
        if 'disp' in t and 'rot' in t:
            m = self.th.quat_to_matrix(t['rot'])
            if m is not None:
                d = t['disp']
                # dot product
                return [self.add(self.dot(m[0], v), d[0]), self.add(self.dot(m[1], v), d[1]), self.add(self.dot(m[2], v), d[2])]
        return None


    def propagate_values_across_operators(self, token, left_token, right_token):
        if token.isOp and token.str in ['+', '-', '+=', '-=', '*', '/', '*=', '/=']:
            left_val = left_token.vals[-1] if (left_token and left_token.vals) else None
            right_val = right_token.vals[-1] if (right_token and right_token.vals) else None
            val = None

            # perform operations on transform/quaternion/matrix3x3/vector3
            is_left_num = (not isinstance(left_val, dict)) and (not isinstance(left_val, list))
            is_right_num = (not isinstance(right_val, dict)) and (not isinstance(right_val, list))

            if (left_val is not None) and (right_val is not None): # binary
                if token.str in ['+', '+=']:
                    if isinstance(left_val, list) and isinstance(right_val, list):
                        val = [self.add(x,y) for x,y in zip(left_val, right_val)]
                    elif is_left_num and is_right_num:
                        val = left_val + right_val

                elif token.str in ['-', '-=']:
                    if isinstance(left_val, list) and isinstance(right_val, list):
                        val = [self.sub(x,y) for x,y in zip(left_val, right_val)]
                    elif is_left_num and is_right_num:
                        val = left_val - right_val

                elif token.str in  ['*', '*=']:
                    if isinstance(left_val, dict) and isinstance(right_val, dict): #*transform
                        r = None
                        d = None
                        if 'rot' in left_val and 'rot' in right_val:
                            r = self.th.quat_mult_quat(left_val['rot'], right_val['rot'])
                        if 'disp' in left_val and 'disp' in right_val:
                            d = self.transform_mult_vector(left_val, right_val['disp'])
                        if r is None:
                            r = [None]*4
                        if d is None:
                            d = [None]*3
                        val = {'disp': d, 'rot': r}                            
                    elif isinstance(left_val, dict) and isinstance(right_val, list):
                        if len(right_val)==3: #*vector
                            val = self.transform_mult_vector(left_val, right_val)
                        elif len(right_val)==4: #*quat
                            if 'rot' in left_val:
                                val = self.th.quat_mult_quat(left_val['rot'], right_val)
                    elif isinstance(left_val, list) and isinstance(right_val, list):
                        if len(left_val)==3 and len(right_val)==3: #vector*vector
                            val = [self.mult(x,y) for x,y in zip(left_val, right_val)]
                        elif len(left_val)==4 and len(right_val)==4: #quat*quat
                            val = self.th.quat_mult_quat(left_val, right_val)
                        elif len(left_val)==9 and len(right_val)==9: #matrix*matrix
                            val = self.th.matrix_mult_matrix(left_val, right_val)
                    elif isinstance(left_val, list) and is_right_num:
                        val = [self.mult(x,right_val) for x in left_val]
                    elif is_left_num and is_right_num:
                        val = left_val * right_val

                elif token.str in ['/', '/=']:
                    if right_val == 0.0:
                        return
                    if isinstance(left_val, list) and is_right_num:
                        dnom = 1.0 / right_val
                        val = [self.mult(x,dnom) for x in left_val]
                    elif is_left_num and is_right_num:
                        val = left_val / right_val

            elif token.str == '-' and (not token.astOperand2): # unary minus
                if left_val is not None:
                    if isinstance(left_val, list):
                        val = [self.usub(x) for x in left_val]
                    elif is_left_num:
                        val = -left_val
     
            if val is not None:
                self.update_token_value(token, val)


    def propagate_values_across_typecast(self, token, left_token, right_token):
        if token.str == '(' and token.valueType:
            if token.astOperand1 and token.astOperand1.vals:
                val = token.astOperand1.vals[-1]
                self.update_token_value(token, val)


    def propagate_values_across_constructor(self, token, left_token, right_token):
        if token.str == '(' and token.previous:
            val_token = token.astOperand2
            if not val_token:
                return

            # VARIABLE INITIALIZER
            if token.previous.variable:        
                ctor = self.sh.find_sanitized_variable_type(token.previous.variable)
            # CONSTRUCTOR
            else:
                ctor = token.previous.str
 
            val = None

            if ctor in ['StampedTransform', 'tf::StampedTransform']:
                d = [None]*3
                r = [None]*4 
                if val_token.vals:
                    val = val_token.vals[-1]
                    val = copy.deepcopy(val[0]) #value of tf::transform
                    if val and 'disp' in val:
                        d = val['disp']
                    if val and 'rot' in val:
                        r = val['rot']
                val = {'disp': d, 'rot': r}
                        
            elif ctor in ['Transform', 'tf::Transform']:
                d = [None]*3
                r = [None]*4
                if val_token.vals:
                    if val_token.str == ',': #(rotation, translation)                                                            
                        val = copy.deepcopy(val_token.vals[-1])
                        if val[1]:
                            d = val[1]
                        if val[0]:
                            r = val[0]                    
                    else: #(rotation)
                        r = copy.deepcopy(val_token.vals[-1])
                        d = [0, 0, 0]
                    
                val = {'disp': d, 'rot': r}

            elif ctor in ['Quaternion', 'tf::Quaternion']:
                val = copy.deepcopy(val_token.vals[-1]) if val_token.vals else [None]*4
                if isinstance(val, list) and len(val)==3: # ypr=YXZ euler
                    #val = [val[1], val[0], val[2]]
                    val = self.th.euler_to_quat(val, 'YXZ')

            elif ctor in ['Vector3', 'tf::Vector3']: # w=0?
                val = copy.deepcopy(val_token.vals[-1]) if val_token.vals else [None]*3

            elif ctor in ['Matrix3x3', 'tf::Matrix3x3']:
                val = copy.deepcopy(val_token.vals[-1]) if val_token.vals else [None]*9
                if isinstance(val, list) and len(val)==4: # quaternion
                    val = self.th.quat_to_matrix(val, flatten=True)

            else:
                return

            # VARIABLE INITIALIZER
            if token.previous.variable:
                if isinstance(val, dict):
                    token.previous.variable.vals = val
                elif isinstance(val, list):
                    token.previous.variable.vals['vec'] = val
                else:
                    token.previous.variable.vals['num'] = val      
                
            # CONSTRUCTOR
            else:
                self.update_token_value(token, val)
                

    def propagate_values_across_tf_functions(self, token, left_token, right_token):
        if token.str == '(' and token.previous:
            func_token = token.previous
            val_token = token.astOperand2
 
            val = None

            if func_token.str.startswith('createQuaternion') and val_token:
                val = copy.deepcopy(val_token.vals[-1]) if val_token.vals else [None]*4
                if not isinstance(val, list):
                    val = [0, 0, val]

                if len(val)==3: # rpy=xyz fixed_axes
                    val = self.th.euler_to_quat(val, 'xyz')

            elif func_token.str == 'createIdentityQuaternion':
                val = [0, 0, 0, 1]

            else:
                return

            self.update_token_value(token, val)


    def propagate_values_across_get_functions(self, token, left_token, right_token):
        if token.str == '(' and left_token:
            func_token = left_token.astOperand2
            if not func_token:
                return

            if func_token.str == 'getIdentity':
                type_token = left_token.astOperand1
                if not type_token:
                    return

                val = None

                if type_token.str == 'Transform':
                    val = {'disp': [0, 0, 0], 'rot': [0, 0, 0, 1]}
                elif type_token.str == 'Quaternion':
                    val = [0, 0, 0, 1]
                elif type_token.str == 'Matrix3x3':
                    val = [1, 0, 0, 0, 1, 0, 0, 0, 1]

                if val is not None:
                    self.update_token_value(token, val)

            elif left_token.vals:
                left_val = left_token.vals[-1]
                left_type = None

                if left_token.astOperand1:
                    (var_token, var_name) = self.get_var_token_and_var_name(left_token.astOperand1)
                    if var_token and var_token.variable:
                        left_type = self.sh.find_sanitized_variable_type(var_token.variable)

                if not left_type:
                    return

                val = None

                if 'quaternion' in left_type.lower() or 'vector' in left_type.lower():
                    if not isinstance(left_val, list):
                        return
                    if func_token.str == 'getX' or func_token.str == 'x':
                        val = left_val[0]
                    elif func_token.str == 'getY' or func_token.str == 'y':
                        val = left_val[1]
                    elif func_token.str == 'getZ' or func_token.str == 'z':
                        val = left_val[2]
                    elif (func_token.str == 'getW' or func_token.str == 'w') and len(left_val)==4:
                        val = left_val[3]
                        
                    if val is not None:
                        self.update_token_value(token, val)

                elif 'transform' in left_type.lower():
                    if not isinstance(left_val, dict):
                        return
                    if func_token.str == 'getOrigin':
                        val = left_val.get('disp')
                    elif func_token.str == 'getRotation':
                        val = left_val.get('rot')
                    elif func_token.str == 'getBasis':
                        val = left_val.get('rot')
                        if val:
                            val = self.th.quat_to_matrix(val, flatten=True)

                    if val is not None:
                        self.update_token_value(token, val)

                #TODO 
                elif 'matrix' in left_type.lower():            
                    if not isinstance(left_val, list):
                        return
                    if func_token.str == 'getEulerYPR': #ypr=ZYX; YXZ euler or as per the code ZYX euler?
                        pass #TODO
                    elif func_token.str == 'getRPY': #rpy=XYZ fixed
                        pass #TODO
                    elif func_token.str == 'getRotation': #quaternion
                        pass #TODO
                    elif func_token.str == 'inverse': #matrix return
                        pass #TODO
                    elif func_token.str == 'transpose': #matrix return
                        pass #TODO
             
                   
                
    def propagate_values_across_dot_connector(self, token, left_token, right_token):
        if token.str == '.':
            if self.is_match(token.astParent, '(') and left_token and right_token:
                #tf api functions
                val_token = token.astParent.astOperand2

                (left_token, left_name) = self.get_var_token_and_var_name(left_token)
                if left_token and left_token.variable:
                    left_type = self.sh.find_sanitized_variable_type(left_token.variable)

                    val = None

                    if 'stampedtransform' in left_type.lower():
                        if right_token.str == 'setData':
                            if (val_token and val_token.vals):
                                val = copy.deepcopy(val_token.vals[-1])
                                left_token.variable.vals = val
                            else:
                                left_token.variable.vals['disp'] = [None]*3
                                left_token.variable.vals['rot'] = [None]*4
                            return
                            
                    elif 'transform' in left_type.lower():
                        if right_token.str == 'setIdentity':
                            left_token.variable.vals['disp'] = [0, 0, 0]
                            left_token.variable.vals['rot'] = [0, 0, 0, 1]
                        elif right_token.str == 'setOrigin':
                            val = copy.deepcopy(val_token.vals[-1]) if (val_token and val_token.vals) else [None]*3 
                            left_token.variable.vals['disp'] = val 
                        elif right_token.str == 'setRotation': #quaternion
                            val = copy.deepcopy(val_token.vals[-1]) if (val_token and val_token.vals) else [None]*4 
                            left_token.variable.vals['rot'] = val
                        elif right_token.str == 'setBasis': #matrix
                            val = copy.deepcopy(val_token.vals[-1]) if (val_token and val_token.vals) else [None]*4
                            if len(val)==9: #matrix
                                val = self.th.matrix_to_quat(val)
                            left_token.variable.vals['rot'] = val

                        if val is not None:
                            return

                    #TODO QuadWord setValue, setX, setY, setZ, setW
                    elif 'quaternion' in left_type.lower():
                        if right_token.str == 'setEuler': #ypr=YXZ
                            if (val_token and val_token.vals):
                                val = copy.deepcopy(val_token.vals[-1])
                                #val = [val[1], val[0], val[2]]
                                val = self.th.euler_to_quat(val, 'YXZ')
                            else:
                                val = [None]*4
                        elif right_token.str == 'setEulerZYX': #ypr=ZYX
                            if (val_token and val_token.vals):
                                val = copy.deepcopy(val_token.vals[-1]) 
                                #val.reverse()
                                val = self.th.euler_to_quat(val, 'ZYX')
                            else:
                                val = [None]*4
                        elif right_token.str == 'setRotation': #axis,angle
                            val = copy.deepcopy(val_token.vals[-1]) if (val_token and val_token.vals) else [[None]*3, None]
                            #TODO convert axis-angle to quaternion; for now, assign None
                            val = None                   
                        elif right_token.str == 'setRPY': #rpy=XYZ fixed
                            val = copy.deepcopy(val_token.vals[-1]) if (val_token and val_token.vals) else [None]*4
                            if len(val)==3: #rpy=XYZ fixed
                                val = self.th.euler_to_quat(val, 'xyz')
                                
                        if val is not None:
                            left_token.variable.vals['vec'] = val
                            return

                        if 'set' in right_token.str:
                            if not ('vec' in left_token.variable.vals):
                                left_token.variable.vals['vec'] = [None]*4
                            left_val = left_token.variable.vals['vec']

                            if (val_token and val_token.vals):
                                val = val_token.vals[-1]

                            if right_token.str == 'setX':                                
                                left_val[0] = val
                                return
                            elif right_token.str == 'setY':
                                left_val[1] = val
                                return
                            elif right_token.str == 'setZ':
                                left_val[2] = val
                                return
                            elif right_token.str == 'setW':
                                left_val[3] = val
                                return
                                                 
                    elif 'vector' in left_type.lower():
                        if right_token.str == 'setValue': #xyz, w=0?
                            val = copy.deepcopy(val_token.vals[-1]) if (val_token and val_token.vals) else [None]*3 
                        elif right_token.str == 'setZero':
                            val = [0, 0, 0]

                        if val is not None:
                            left_token.variable.vals['vec'] = val
                            return

                        if 'set' in right_token.str:
                            if not ('vec' in left_token.variable.vals):
                                left_token.variable.vals['vec'] = [None]*3
                            left_val = left_token.variable.vals['vec']

                            if (val_token and val_token.vals):
                                val = val_token.vals[-1]

                            if right_token.str == 'setX':                                
                                left_val[0] = val
                                return
                            elif right_token.str == 'setY':
                                left_val[1] = val
                                return
                            elif right_token.str == 'setZ':
                                left_val[2] = val
                                return
                            #TODO setW?

                    #TODO 
                    elif 'matrix' in left_type.lower():
                        if right_token.str == 'setEulerYPR' or right_token.str == 'setEulerZYX': #ypr=ZYX euler
                            pass #TODO
                        elif right_token.str == 'setRPY': #rpy=XYZ fixed
                            pass #TODO
                        elif right_token.str == 'setRotation': #quaternion
                            pass #TODO
                        elif right_token.str == 'setIdentity':
                            pass #TODO
                        elif right_token.str == 'setValue': #xx,xy,xz,yx,yy,yz,zx,zy,zz row major
                            pass #TODO
                        
            left_val = left_token.vals[-1] if (left_token and left_token.vals) else None
            right_val = right_token.vals[-1] if (right_token and right_token.vals) else None

            if (left_val is not None) and (right_val is not None):
                self.update_token_value(token, right_val)
                # must be something wrong; we just want to propagate variable value to the top; warn
                # print "WARN: both left and right child of '.' have values."
            elif left_val is not None:
                self.update_token_value(token, left_val)
            elif right_val is not None:
                self.update_token_value(token, right_val)
            

    def propagate_values_across_comma_connector(self, token, left_token, right_token):
        if token.str == ',':
            left_val = left_token.vals[-1] if (left_token and left_token.vals) else None
            right_val = right_token.vals[-1] if (right_token and right_token.vals) else None

            if self.is_match(left_token, ','):
                val = copy.deepcopy(left_val)
                val.append(right_val)
            else:
                val = [left_val, right_val]

            self.update_token_value(token, val)


    def propagate_values_across_assignment_operator(self, token, left_token, right_token):
        if (token.isAssignmentOp or (token.isOp and token.str in ['+=','-=','*=','/='])) and left_token and right_token:
            left_name = left_token.str
            if left_token.str in ['.', '[', '(']:
                (left_token, left_name) = self.sh.find_compound_variable_token_and_name_for_sym_token(left_token)

            if left_token.variable:
                val = None
                if token.vals: # for arithmetic assignment operators
                    val = copy.deepcopy(token.vals[-1]) 
                elif right_token and right_token.vals:
                    val = copy.deepcopy(right_token.vals[-1])

                if val is None:
                    return
                    #TODO reset value of left variable to None i.e. empty {}?

                if self.sh.is_ros_transform_type(left_token.variable):
                    if 'transform.translation' in left_name:
                        # geometry_msgs::TransformStamped
                        if not ('disp' in left_token.variable.vals):
                            left_token.variable.vals['disp'] = [None]*3

                        d = left_token.variable.vals['disp']
                        if left_name.endswith('.x'):
                            d[0] = val
                        elif left_name.endswith('.y'):
                            d[1] = val
                        elif left_name.endswith('.z'):
                            d[2] = val
                        elif left_name.endswith('.translation'):
                            if isinstance(val, list):
                                left_token.variable.vals['disp'] = val
                            # else: something wrong

                    elif 'transform.rotation' in left_name:
                        # geometry_msgs::TransformStamped
                        if not ('rot' in left_token.variable.vals):
                            left_token.variable.vals['rot'] = [None]*4

                        r = left_token.variable.vals['rot']
                        if left_name.endswith('.x'):
                            r[0] = val
                        elif left_name.endswith('.y'):
                            r[1] = val
                        elif left_name.endswith('.z'):
                            r[2] = val
                        elif left_name.endswith('.w'):
                            r[3] = val
                        elif left_name.endswith('.rotation'):
                            if isinstance(val, list):
                                left_token.variable.vals['rot'] = val
                            # else: something wrong

                    else:
                        # assignment of transform variable to another transform variable
                        #if not('.header' in left_name) and not('frame_id' in left_name):
                        if not any(substr in left_name for substr in ['.header', 'frame_id', 'stamp']):
                            left_token.variable.vals = val
                                 
                else:
                    if isinstance(val, dict):
                        left_token.variable.vals = val
                    elif isinstance(val, list):
                        left_token.variable.vals['vec'] = val
                    else:
                        left_token.variable.vals['num'] = val


    def propagate_values_across_copy_constructor(self, token, left_token, right_token):
        if token == '(' and left_token and right_token:

            (left_token, left_name) = self.get_var_token_and_var_name(left_token)
            if left_token and left_token.variable:
                (right_token, right_name) = self.get_var_token_and_var_name(right_token)
                if right_token and right_token.variable:

                    if self.sh.find_sanitized_variable_type(left_token.variable) == \
                            self.sh.find_sanitized_variable_type(right_token.variable):

                        val = right_token.variable.vals 

                        if val:
                            left_token.variable.vals = copy.deepcopy(val) 


    def propagate_values_across_param(self, token, left_token, right_token):
        if (token.str == 'param'):

            if self.is_match(token.astParent, '.') and self.is_match(token.astParent.astParent, '('):
                paren_token = token.astParent.astParent
                val_token = self.get_comma_separated_token_at_pose_from_right(paren_token, 1)

                val = copy.deepcopy(val_token.vals[-1]) if (val_token and val_token.vals) else None 

                if val is not None:
                    var_token = None

                    if self.is_match(paren_token.astParent, '='):
                        var_token = paren_token.astParent.astOperand1
                    else:
                        var_token = self.get_comma_separated_token_at_pose_from_right(paren_token, 2)

                    if var_token:
                        (var_token, var_name) = self.get_var_token_and_var_name(var_token)

                        if var_token.variable:
                            var_token.variable.isParam = True
                            # Assume no transform variables set in the param
                            if isinstance(val, list):
                                var_token.variable.vals['vec'] = val
                            else:
                                var_token.variable.vals['num'] = val



    #TODO function call
    #TODO function return

                


