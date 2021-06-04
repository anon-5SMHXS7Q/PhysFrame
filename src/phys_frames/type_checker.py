#Copyright 2021 Purdue University, University of Virginia.
#All rights reserved.


from symbol_helper import SymbolHelper, get_body
#from type_helper import TypeHelper
from tree_walker import TreeWalker
from frame_error import FrameError
from frame_error_types import FrameErrorTypes
import debug_data as dd
import os.path
from collections import OrderedDict, defaultdict
import re
from itertools import product



class TypeChecker:

    def __init__(self, th, sh, target=''):
        self.all_errors = []
        self.unique_errors = []
        self.sh = sh #SymbolHelper()
        self.th = th
        self.target = target
        self.frames_to_check = []
        self.sensors = ['openni','imu','kinect','velodyne']
        self.current_file_group = ''
        self.combine_errors = True


    def check_types_for_launch_file(self, transform_list, launch_file):
        for transform in transform_list:
            self.error_check_launch_incorrect_transform(transform, launch_file)
            self.register_launch_transform_to_frame_tree_type(transform, launch_file)


    def error_check_launch_incorrect_transform(self, transform, launch_file):
        f = transform.frame[0] if transform.frame else None
        cf = transform.frame[1] if transform.frame else None

        if f and cf:
            if self.th.is_unknown_frame_type_elem(f) or self.th.is_unknown_frame_type_elem(cf):
                return

            f_body = get_body(f.id)
            cf_body = get_body(cf.id)
            if f_body and cf_body and f_body != cf_body:
                return

            is_non_valid = any(d in cf.x_dir for d in ('x','y','z'))
            if not is_non_valid:
                (cf_x_dir, cf_y_dir, cf_z_dir) = self.sh.get_ros_orientation_convention(cf.id)

                if (cf.x_dir != cf_x_dir) or (cf.y_dir != cf_y_dir) or (cf.z_dir != cf_z_dir):
                    values = [(cf.x_dir, cf.y_dir, cf.z_dir), (cf_x_dir, cf_y_dir, cf_z_dir)]
                    file_name = launch_file
                    linenr = transform.linenr
                    self.report_incorrect_transform_error(None, '', cf.id, values, file_name, linenr)
                

    def register_launch_transform_to_frame_tree_type(self, transform, launch_file):
        tf_frame = transform.frame
        if self.th.is_valid_transform_type(tf_frame):              
            self.th.register_transform_type(launch_file, tf_frame, check_mult_src=False)


    def check_types(self):
        #self.th.debug_print_transform_frame_tree_type(self.target)

        #self.error_check_tranform_frame_tree_type()
        self.error_check_transform_frame_tree_type_order()
        self.error_check_frames_connection()
        #self.error_check_transform_multiple_sources()

        if dd.COLLECT_STATS:
            self.collect_stats()


    def check_types_for_file_group(self, group_id, file_group):
        if not file_group:
            return

        self.current_file_group = group_id
        self.th.construct_transform_frame_tree_type_for_file_group(file_group)
        self.error_check_tranform_frame_tree_type()
        self.error_check_transform_multiple_sources()

        #print "FILE_GROUP: %s" % (file_group[0])
        #print "FILE_GROUP: %s" % (group_id)
        #self.th.debug_print_transform_frame_tree_type(self.target)


    def check_types_for_file(self, configuration, sorted_analysis_dict):
        self.th.clear_frame_orientation()

        self.error_check_missing_frame(configuration)
        self.error_check_incorrect_transform(configuration)
        #self.error_check_transform_variables(configuration)

        for function_dict in sorted_analysis_dict.values():
            tw = TreeWalker()
            for root_token in function_dict['root_tokens']: 
                tw.generic_recurse_and_apply_function(root_token, 
                                                      self.error_check_publish_message_recursive)              
                tw.generic_recurse_and_apply_function(root_token, 
                                                      self.error_check_stamped_transform_construction_recursive)
                tw.generic_recurse_and_apply_function(root_token,
                                                      self.construct_and_error_check_transform_frame_tree_type_recursive)
                tw.generic_recurse_and_apply_function(root_token, 
                                                      self.error_check_lookup_transform_recursive)
                tw.generic_recurse_and_apply_function(root_token, 
                                                      self.error_check_transform_object_recursive)

        if dd.COLLECT_IMPLICIT_CONVENTION_DATA:
            self.collect_transform_vars_data(configuration)


    def add_unique_error(self, new_error):
        found = False

        for e in self.unique_errors:
            if e.ERROR_TYPE == new_error.ERROR_TYPE:
                if e.frame_name == new_error.frame_name and e.values == new_error.values:
                    e.file_name.append(self.current_file_group)
                    found = True

        if not found:
            new_error.file_name = [self.current_file_group]
            self.unique_errors.append(new_error)


    def is_match(self, token, value):
        if token and (token.str == value):
            return True

        return False


    def get_file_name(self, token):
        return os.path.relpath(token.file, self.target)


    def get_var_name(self, token):
        name = ''
        if token.variable or token.str in ['.', '[']:
            name = self.sh.recursively_visit(token)
        if (not name) and token.astOperand1:
            name = self.get_var_name(token.astOperand1)   
        if (not name) and token.astOperand2:
            name = self.get_var_name(token.astOperand2)
        return name


    def report_missing_frame_error(self, var, var_name, file_name, linenr):
        new_error = FrameError()
        new_error.ERROR_TYPE = FrameErrorTypes.MISSING_FRAME
        new_error.var_name = var_name if var_name else self.get_var_name(var.nameToken)
        new_error.file_name = file_name
        new_error.linenr = linenr if linenr else var.nameToken.linenr
        self.all_errors.append(new_error)

    
    def report_missing_child_frame_error(self, var, var_name, file_name, linenr):
        new_error = FrameError()
        new_error.ERROR_TYPE = FrameErrorTypes.MISSING_CHILD_FRAME
        new_error.var_name = var_name if var_name else self.get_var_name(var.nameToken)
        new_error.file_name = file_name
        new_error.linenr = linenr if linenr else var.nameToken.linenr
        self.all_errors.append(new_error)


    def report_incorrect_transform_error(self, var, var_name, frame_name, values, file_name, linenr):
        new_error = FrameError()
        new_error.ERROR_TYPE = FrameErrorTypes.INCORRECT_TRANSFORM
        new_error.var = var
        new_error.var_name = var_name if var_name else '' #self.get_var_name(var.nameToken)
        new_error.frame_name = frame_name
        new_error.values = values
        new_error.file_name = file_name
        new_error.linenr = linenr
        self.all_errors.append(new_error)


    def report_transform_error(self, err_type, values, file_name, linenr):
        new_error = FrameError()
        new_error.ERROR_TYPE = err_type
        new_error.values = values
        new_error.file_name = file_name
        new_error.linenr = linenr

        if err_type == FrameErrorTypes.NON_CONNECTED_FRAMES:
            new_error.is_warning = True

        self.all_errors.append(new_error)


    def report_error(self, err_type, var_name, values, file_name, linenr, is_warning):
        new_error = FrameError()
        new_error.ERROR_TYPE = err_type
        new_error.var_name = var_name
        new_error.values = values
        new_error.file_name = file_name
        new_error.linenr = linenr
        new_error.is_warning = is_warning
        self.all_errors.append(new_error)


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # TYPE CHECKING RULES
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #TODO
    def error_check_missing_frame(self, configuration):
        for v in configuration.variables:

            if v.isArgument: # and v.isReference:
                continue

            if str(self.sh.find_variable_type(v)).endswith('ConstPtr'):
                continue

            if not v.nameToken:
                continue
 
            file_name = self.get_file_name(v.nameToken)
            if file_name.endswith(('.h', '.hpp')):
                continue

            if not v.isUsed:
                continue

            if v.is_frame_set:
                continue

            if not v.checkFrame:
                continue

            if v.isTransform:
                if (not v.frames):
                    self.report_missing_frame_error(v, '', file_name, None)
                    self.report_missing_child_frame_error(v, '', file_name, None)
                    continue

                found_type = False
                for name, frame_list in v.frames.iteritems():
                    frame = self.th.get_latest_non_default_frame_type_from_list(frame_list) #frame_list[-1]['type']
                    if frame and len(frame) == 2:
                        found_type = True
                        if (not frame[0]):
                            self.report_missing_frame_error(v, name, file_name, None)
                        if (not frame[1]):
                            self.report_missing_child_frame_error(v, name, file_name, None)
                #TODO verify
                #if (not found_type):
                #    self.report_missing_child_frame_error(v, '', file_name, None)

            else:
                frame_count = self.sh.get_frame_count_by_ros_type_of_variable(v)

                max_frame_len = 0
                #for frame_list in v.frames.itervalues():
                #    frame = self.th.get_latest_non_default_frame_type_from_list(frame_list) #frame_list[-1]['type']
                #    if frame and (len(frame) > max_frame_len):
                #        max_frame_len = len(frame)

                for name, frame_list in v.frames.iteritems():
                    if ('.frame_id' in name) or name.endswith('header') or ('.child_frame_id' in name) or (name.endswith(v.nameToken.str)):
                        frame = self.th.get_latest_non_default_frame_type_from_list(frame_list)
                        if frame and (len(frame) > max_frame_len):
                            max_frame_len = len(frame)

                if max_frame_len < frame_count:
                    if (not max_frame_len) or (frame_count > 1 and (not(any(('.frame_id' in name) or (name.endswith('header')) or (name.endswith(v.nameToken.str)) for name in v.frames)))):
                        self.report_missing_frame_error(v, '', file_name, None)
        
                    if frame_count > 1 and ((not max_frame_len) or (not(any(('.child_frame_id' in name) or (name.endswith(v.nameToken.str)) for name in v.frames)))):
                        self.report_missing_child_frame_error(v, '', file_name, None)


    #TODO check rotation and translation separately.
    def error_check_incorrect_transform(self, configuration):
        for v in configuration.variables:

            if v.isTransform and v.frames:

                if not v.nameToken:
                    continue
 
                #TODO check based on var_token instead of v.nameToken?
                file_name = self.get_file_name(v.nameToken)
                if file_name.endswith(('.h', '.hpp')):
                    continue

                var_token = None
                var_name = None
                var_frame = None
                tf_frame = None

                for name, frame_list in v.frames.iteritems():
                    frame = frame_list[-1]['type']
                    if len(frame) == 2 and frame[0] and frame[1]:
                        if frame[-1].id == 'xyz':
                            tf_frame = frame
                        else:
                            var_token = frame_list[-1]['token']
                            var_name = name
                            var_frame = frame

                var_type = self.sh.find_sanitized_variable_type(v)

                if var_frame and (tf_frame or var_type=='geometry_msgs::TransformStamped'):
                    result_frame = self.th.recurse_and_get_frame_type(var_frame)

                    if not result_frame:
                        continue
                        
                    to_frame = result_frame[0]
                    from_frame = result_frame[1]

                    #TODO only one of them is list; i.e., one is an argument

                    #both are lists; i.e. both are arguments OR both are non-lists
                    if not isinstance(to_frame, list):
                        to_frame = [[to_frame]]
                    if not isinstance(from_frame, list):
                        from_frame = [[from_frame]]

                    if len(to_frame) != len(from_frame):
                        continue

                    for frame1, frame2 in zip(to_frame, from_frame):
                        f = None
                        cf = None
                        if frame1 and frame1[-1]: 
                            f = frame1[-1]
                        if frame2 and frame2[-1]:
                            cf = frame2[-1]

                        if f and cf:
                            if self.th.is_unknown_frame_type_elem(f) or self.th.is_unknown_frame_type_elem(cf):
                                continue

                            skip = False
                            if self.is_static_rot_values(v.vals):
                                f_body = get_body(f.id)
                                cf_body = get_body(cf.id)
                                if f_body and cf_body and f_body != cf_body:
                                    skip = True

                            if tf_frame and (not skip):
                                tf_f_frame = tf_frame[0]
                                tf_cf_frame = tf_frame[1]

                                (f_x_dir, f_y_dir, f_z_dir) = self.th.get_frame_orientation(f.id, default=True)
                                f = (self.th.create_frame_type(f.id, f_x_dir, f_y_dir, f_z_dir))[-1]

                                cf_dir = self.th.find_childframe_orientation([f_x_dir, f_y_dir, f_z_dir],
                                                                          [[tf_f_frame.x_dir, tf_f_frame.y_dir, tf_f_frame.z_dir],
                                                                           [tf_cf_frame.x_dir, tf_cf_frame.y_dir, tf_cf_frame.z_dir]])
                                if len(cf_dir) == 3:
                                    (cf_x_dir, cf_y_dir, cf_z_dir) = tuple(cf_dir)
                                    cf = (self.th.create_frame_type(cf.id, cf_x_dir, cf_y_dir, cf_z_dir))[-1]
                                    self.th.set_frame_orientation(cf.id, (cf_x_dir, cf_y_dir, cf_z_dir))

                                (cf_x_dir, cf_y_dir, cf_z_dir) = self.sh.get_ros_orientation_convention(cf.id)

                                if (cf.x_dir != cf_x_dir) or (cf.y_dir != cf_y_dir) or (cf.z_dir != cf_z_dir):
                                    values = [(cf.x_dir, cf.y_dir, cf.z_dir), (cf_x_dir, cf_y_dir, cf_z_dir)]
                                    file_name = self.get_file_name(var_token)
                                    linenr = var_token.linenr
                                    self.report_incorrect_transform_error(v, var_name, cf.id, values, file_name, linenr)

                            # CHECK LINTER RULES
                            self.error_check_transform_variable(var_token, var_name, f, cf, v.vals)


    def is_static_rot_values(self, values):
        if (not values):
            return False
        rot = values.get('rot')
        if (not rot) or (None in rot):
            return False
        return True


    def is_null_disp_values(self, variable):
        disp = variable.vals.get('disp')
        if (not disp) or (None in disp):
            return None

        return (disp[0] == 0 and disp[1] == 0 and disp[2] == 0)

    def is_null_rot_values(self, variable):
        rot = variable.vals.get('rot')
        if (not rot) or (None in rot):
            return None

        return (rot[0] == 0 and rot[1] == 0 and rot[2] == 0)

    def is_null_transform_values(self, variable):
        disp = self.is_null_disp_values(variable)
        rot = self.is_null_rot_values(variable)
        if (disp is None) or (rot is None):
            return None
 
        return (disp and rot)

    def is_null_disp(self, values):
        disp = values.get('disp')
        if (not disp) or (None in disp):
            return None

        return (disp[0] == 0 and disp[1] == 0 and disp[2] == 0)

    def is_null_rot(self, f, cf):
        return (f.x_dir == cf.x_dir and f.y_dir == cf.y_dir and f.z_dir == cf.z_dir)


    def is_null_transform(self, f, cf, values):
        disp = self.is_null_disp(values)
        rot = self.is_null_rot(f, cf)
        if (disp is None) or (rot is None):
            return None
 
        return (disp and rot)


    #TODO call this function from both incorrect transform and incorrect stampedtransform 
    #so that frame dirs (instead of values) can be used to determine if the rotation is null
    # Linter Rules
    # 4: reversed_name
    # 7: ned_transform
    # 8: sensor_null
    #def error_check_transform_variables(self, configuration)
    def error_check_transform_variable(self, token, var_name, f, cf, values):
        name = var_name.lower() 
        parent = f.id.lower()
        child = cf.id.lower()
           
        if name:    
            #4: reversed_name
            if (child+parent in name or child+"_"+parent in name \
                    or child+"to"+parent in name or child+"_to_"+parent in name \
                    or child+"2"+parent in name or child+"_2_"+parent in name \
                    or parent+"in"+child in name or parent+"_in_"+child in name \
                    or parent+"_rel_"+child in name or parent+"_wrt_"+child in name):

                self.report_error(FrameErrorTypes.REVERSED_NAME, var_name, (f.id, cf.id), \
                                  self.get_file_name(token), token.linenr, is_warning=True)
            else:
                conn_in_name = any(substr in var_name for substr in ['To', '_to_', '2', '_2_', 'In', '_in_', '_rel_', '_wrt_'])
                lp = re.split(r'[_|\.]', parent)
                lc = re.split(r'[_|\.]', child)
                pairs = list(product(lp, lc))
                for p, c in pairs:
                    if p == c:
                        continue
                    if (not conn_in_name and any((c+substr+p in name and c+substr+p not in child) for substr in ['', '_'])) or \
                            any(c+substr+p in name for substr in ['to', '_to_', '2', '_2_']) or \
                            any(p+substr+c in name for substr in ['in', '_in_', '_rel_', '_wrt_']):

                        self.report_error(FrameErrorTypes.REVERSED_NAME, var_name, (f.id, cf.id), \
                                          self.get_file_name(token), token.linenr, is_warning=True)
                        break

        if values:
            # 7: ned_transform
            if child.endswith("_ned"):
                if (self.is_null_disp(values) is False) or (self.is_null_rot(f, cf) is True):

                    self.report_error(FrameErrorTypes.NED_NULL, var_name, values, \
                                      self.get_file_name(token), token.linenr, is_warning=False) # DICT


            # 8: sensor_null
            for sensor in self.sensors:
                if (sensor in name or sensor in parent or sensor in child):
                    if self.is_null_transform(f, cf, values):

                        self.report_error(FrameErrorTypes.SENSOR_NULL, var_name, sensor, \
                                          self.get_file_name(token), token.linenr, is_warning=False) # STRING
  

    def error_check_publish_message_recursive(self, token, left_token, right_token):
        if token.str == 'publish' and \
            token.astParent and self.is_match(token.astParent.astParent, '('):

            if token.frames:
                checkFrame = token.frames[0]
                frame = token.frames[1]

                if checkFrame and (not frame):
                     self.report_missing_frame_error(None, 'publish', self.get_file_name(token), token.linenr)
                              

    def error_check_lookup_transform(self, sorted_analysis_dict):
        for function_dict in sorted_analysis_dict.values():
            tw = TreeWalker()
            for root_token in function_dict['root_tokens']:
                tw.generic_recurse_and_apply_function(root_token, self.error_check_lookup_transform_recursive)


    def error_check_lookup_transform_recursive(self, token, left_token, right_token):
        if token.str == 'lookupTransform' and \
                token.astParent and self.is_match(token.astParent.astParent, '('):

            if not token.frames:
                return
        
            self.error_check_transform_between_frames(token, 'Lookup')


    def error_check_transform_object(self, sorted_analysis_dict):
        for function_dict in sorted_analysis_dict.values():
            tw = TreeWalker()
            for root_token in function_dict['root_tokens']:
                tw.generic_recurse_and_apply_function(root_token, self.error_check_transform_object_recursive)


    def error_check_transform_object_recursive(self, token, left_token, right_token):
        if token.str in ['transformPoint', 'transformPose', 'transformQuaternion', 'transformVector'] and \
                token.astParent and self.is_match(token.astParent.astParent, '('):

            if not token.frames:
                return
        
            self.error_check_transform_between_frames(token)


    def error_check_transform_between_frames(self, token, context=''):
        frame = token.frames[-1]
        result_frame = self.th.recurse_and_get_frame_type(frame)

        if not result_frame:
            return

        for i in range(len(result_frame)-1):
            to_frame = result_frame[i]
            from_frame = result_frame[i+1]

            #TODO only one of them is list; i.e., one is an argument

            #both are lists; i.e. both are arguments OR both are non-lists
            if not isinstance(to_frame, list):
                to_frame = [[to_frame]]
            if not isinstance(from_frame, list):
                from_frame = [[from_frame]]

            if len(to_frame) != len(from_frame):
                continue

            for frame1, frame2 in zip(to_frame, from_frame):
                if frame1 and frame1[-1] and frame2 and frame2[-1]:
                    #temporary fix: later, process the result_frame before looping through
                    if isinstance(frame1[-1], list) or isinstance(frame2[-1], list):
                        continue

                    if self.th.is_unknown_frame_type_elem(frame1[-1]) or self.th.is_unknown_frame_type_elem(frame2[-1]):
                        continue
                   
                    if len(frame)==2 and frame1[-1].id and frame2[-1].id and frame1[-1].id == frame2[-1].id:
                        #check for only simple API without fixed_frame
                        self.report_transform_error(FrameErrorTypes.INVALID_FRAMES, 
                                                    [frame1, frame2, context],
                                                    self.get_file_name(token),
                                                    token.linenr )

                    else:
                        #non-connected frames; check against the frame tree
                        self.frames_to_check.append((token, frame1[-1], frame2[-1]))

    
    def error_check_stamped_transform_construction(self, sorted_analysis_dict):
        for function_dict in sorted_analysis_dict.values():
            tw = TreeWalker()
            for root_token in function_dict['root_tokens']:
                tw.generic_recurse_and_apply_function(root_token, 
                                                      self.error_check_stamped_transform_construction_recursive)

   
    def error_check_stamped_transform_construction_recursive(self, token, left_token, right_token):
        if token.str == 'StampedTransform':
                #and token.astParent and self.is_match(token.astParent.astParent, '('):

            if (not token.frames):
                return

            checkFrame = token.frames[-2]
            if (not checkFrame):
                return

            frame = token.frames[-1]
            result_frame = self.th.recurse_and_get_frame_type(frame)

            if not result_frame:
                return

            to_frame = result_frame[0]
            from_frame = result_frame[1]

            #TODO only one of them is list; i.e., one is an argument

            #both are lists; i.e. both are arguments OR both are non-lists
            if not isinstance(to_frame, list):
                to_frame = [[to_frame]]
            if not isinstance(from_frame, list):
                from_frame = [[from_frame]]
            
            if len(to_frame) != len(from_frame):
                return

            var_token = token
            var_name = ''
            values = None

            # GET VAR, IF ANY
            if token.next and token.next.variable:
                var_token = token.next
                var_name = token.next.str
                values = token.next.variable.vals
            elif self.is_match(token.next, '('):
                values = token.next.vals[-1] if token.next.vals else None

            # CHECK IF RECOMPUTE DIRS
            old_f = frame[0]
            old_cf = frame[1]
            recompute = any(d in old_cf.x_dir for d in ('x','y','z')) if old_cf else False
                            
            for frame1, frame2 in zip(to_frame, from_frame):
                f = None
                cf = None
                if frame1 and frame1[-1]:
                    f = frame1[-1]
                if frame2 and frame2[-1]:
                    cf = frame2[-1]
                
                if f and cf:
                    if self.th.is_unknown_frame_type_elem(f) or self.th.is_unknown_frame_type_elem(cf):
                        continue

                    skip = False
                    if self.is_static_rot_values(values):
                        f_body = get_body(f.id)
                        cf_body = get_body(cf.id)
                        if f_body and cf_body and f_body != cf_body:
                            skip = True

                    if (not skip):                    
                        if recompute:
                            (f_x_dir, f_y_dir, f_z_dir) = self.th.get_frame_orientation(f.id, default=True)
                            f = (self.th.create_frame_type(f.id, f_x_dir, f_y_dir, f_z_dir))[-1]

                            cf_dir = self.th.find_childframe_orientation([f_x_dir, f_y_dir, f_z_dir],
                                                                         [[old_f.x_dir, old_f.y_dir, old_f.z_dir],
                                                                          [old_cf.x_dir, old_cf.y_dir, old_cf.z_dir]])
                    
                            if len(cf_dir) == 3:
                                (cf_x_dir, cf_y_dir, cf_z_dir) = tuple(cf_dir)
                                cf = (self.th.create_frame_type(cf.id, cf_x_dir, cf_y_dir, cf_z_dir))[-1]
                                self.th.set_frame_orientation(cf.id, (cf_x_dir, cf_y_dir, cf_z_dir))

                        (cf_x_dir, cf_y_dir, cf_z_dir) = self.sh.get_ros_orientation_convention(cf.id)

                        #print "CF_FRAME3: %s: %s" % (token.linenr, cf)
                        #print "CONVENTION: %s: %s" % (token.linenr, (cf_x_dir, cf_y_dir, cf_z_dir))

                        if (cf.x_dir != cf_x_dir) or (cf.y_dir != cf_y_dir) or (cf.z_dir != cf_z_dir):
                            err_values = [(cf.x_dir, cf.y_dir, cf.z_dir), (cf_x_dir, cf_y_dir, cf_z_dir)]
                            self.report_incorrect_transform_error(None, '', cf.id, err_values, self.get_file_name(token), token.linenr)

                    # CHECK LINTER RULES
                    self.error_check_transform_variable(var_token, var_name, f, cf, values)


    def construct_and_error_check_transform_frame_tree_type(self, sorted_analysis_dict):
        for function_dict in sorted_analysis_dict.values():
            tw = TreeWalker()
            for root_token in function_dict['root_tokens']:
                tw.generic_recurse_and_apply_function(root_token, 
                                                      self.construct_and_error_check_transform_frame_tree_type_recursive)


    def construct_and_error_check_transform_frame_tree_type_recursive(self, token, left_token, right_token):
        if token.str == 'sendTransform' and \
                token.astParent and self.is_match(token.astParent.astParent, '('):
            
            if dd.COLLECT_STATS:
                used_sendtf = False

            if dd.COLLECT_IMPLICIT_CONVENTION_DATA:
                paren_token = token.astParent.astParent
                collect = False
                if self.is_match(paren_token.astOperand2, '(') and self.is_match(paren_token.astOperand2.previous, 'StampedTransform'):
                    #transform object without variable
                    val = paren_token.astOperand2.vals[-1] if paren_token.astOperand2.vals else None
                    d = val['disp'] if val and ('disp' in val) else None
                    r = val['rot'] if val and ('rot' in val) else None
                    collect = True

            for frame in token.frames:
                if frame[-1] and frame[-1].id == 'xyz':
                    continue

                result_frame = self.th.recurse_and_get_frame_type(frame)

                to_frame = result_frame[0] if result_frame else None
                from_frame = result_frame[1] if result_frame else None

                if dd.COLLECT_IMPLICIT_CONVENTION_DATA:
                    if collect:
                        with open('value_transforms.txt', 'a') as vtfile:
                            vtfile.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (self.target, None, to_frame, from_frame, d, r))

                if not result_frame:
                    continue

                #TODO only one of them is list; i.e., one is an argument

                #both are lists; i.e. both are arguments OR both are non-lists
                if not isinstance(to_frame, list):
                    to_frame = [[to_frame]]
                if not isinstance(from_frame, list):
                    from_frame = [[from_frame]]

                if len(to_frame) != len(from_frame):
                    continue

                for frame1, frame2 in zip(to_frame, from_frame):
                    if frame1 and frame2:
                        tf_frame = [frame1[-1], frame2[-1]]
                        if self.th.is_valid_transform_type(tf_frame):              
                            self.th.register_transform_type(self.get_file_name(token), tf_frame)
                        
                            if dd.COLLECT_IMPLICIT_CONVENTION_DATA:
                                with open('transforms.txt', 'a') as tfile:
                                    tfile.write("%s,%s,%s\n" % (self.target, tf_frame[0].id, tf_frame[1].id))

                            if dd.COLLECT_STATS:
                                dd.CHECKED_SEND_TF_COUNT += 1
                                used_sendtf = True

                        if tf_frame[0] and tf_frame[1] and \
                                (not self.th.is_unknown_frame_type_elem(tf_frame[0])) and (not self.th.is_unknown_frame_type_elem(tf_frame[1])) and \
                                tf_frame[0].id and tf_frame[1].id and tf_frame[0].id == tf_frame[1].id:
                            self.report_transform_error(FrameErrorTypes.INVALID_FRAMES, 
                                                        [tf_frame[0], tf_frame[1], 'SendTransform'],
                                                        self.get_file_name(token),
                                                        token.linenr )

                            if dd.COLLECT_STATS:
                                dd.CHECKED_SEND_TF_COUNT += 1
                                used_sendtf = True

            if dd.COLLECT_STATS and used_sendtf:
                dd.USED_SEND_TF_COUNT += 1


    #TODO
    def error_check_transform_multiple_sources(self):
        for item in self.th.multiple_sources:
            new_error = FrameError()
            new_error.ERROR_TYPE = FrameErrorTypes.MULTIPLE_PUBLISH_SOURCES_FOR_TRANSFORM
            new_error.values = item # TUPLE
            new_error.is_warning = True
            self.add_unique_error(new_error)


    #TODO
    def error_check_tranform_frame_tree_type(self):
        # CHECK IF MULTIPLE PARENTS
        for cf_frame, f_frames in self.th.multiple_parents.iteritems():
            new_error = FrameError()
            new_error.ERROR_TYPE = FrameErrorTypes.MULTIPLE_PARENTS_IN_FRAME_TREE
            new_error.frame_name = cf_frame
            new_error.values = f_frames
            self.add_unique_error(new_error)

        # CHECK IF CYCLE
        cycles = set()

        for frame in self.th.transform_frame_tree_type:
            d = defaultdict(list)
            for i, node in enumerate(frame):
                d[node].append(i)

            for k, v in d.items():
                if len(v) > 1:
                    cycle = []                    
                    for i in range(v[0], v[-1]+1):
                        cycle.append(frame[i].id)

                    cycles.add(tuple(cycle))

        if cycles:
            new_error = FrameError()
            new_error.ERROR_TYPE = FrameErrorTypes.CYCLE_IN_FRAME_TREE
            new_error.values = cycles
            self.add_unique_error(new_error)


    #TODO 
    def error_check_transform_frame_tree_type_order(self):
        wrong_orders = set()

        # CHECK MOBILE ORDER
        for frame in self.th.transform_frame_tree_type:
            # STRIP
            frame = [node for node in frame if (node.id in self.th.std_mobile_frame_ids)]
            # REMOVE DUPLICATES DUE TO CYCLES
            frame = list(OrderedDict.fromkeys(frame))

            found = True
            i = 0
            j = 0
            while i < len(frame):
                node  = frame[i]

                while j < len(self.th.mobile_frame_type_order):
                    if self.th.mobile_frame_type_order[j].id == node.id:
                        break
                    j = j+1
                
                if j == len(self.th.mobile_frame_type_order):
                    # END OF STANDARD
                    found = False
                    break
                else:
                    # CHECK NEXT NODE IN FRAME
                    j = j+1
                    i = i+1

            if (not found):
                wrong_orders.add((frame[i-1].id, frame[i].id))

            for order in wrong_orders:
                new_error = FrameError()
                new_error.ERROR_TYPE = FrameErrorTypes.INCORRECT_FRAME_ORDER_IN_TREE
                new_error.values = order
                self.all_errors.append(new_error)


        #TODO IF APPLICABLE, CHECK HUMANOID ORDER


    def error_check_frames_connection(self):
        for (token, frame1_node, frame2_node) in self.frames_to_check:
            connected = False
            for frame in self.th.transform_frame_tree_type:
                if self.th.id_index(frame1_node, frame) >= 0 and self.th.id_index(frame2_node, frame) >= 0:
                    connected = True
                    break
            if (not connected):
                new_error = FrameError()
                new_error.ERROR_TYPE = FrameErrorTypes.NON_CONNECTED_FRAMES
                new_error.values = (frame1_node, frame2_node)
                new_error.file_name = self.get_file_name(token)
                new_error.linenr = token.linenr
                new_error.is_warning = True
                self.all_errors.append(new_error)


    def print_all_errors(self):
        if self.combine_errors:
            self.all_errors.extend(self.unique_errors)
            self.combine_errors = False

        self.pretty_print(show_low_confidence=True)


    def pretty_print(self, show_high_confidence=True, show_low_confidence=True):
        ''' PRINTS ERRORS TO STD OUT, ATTEMPTS TO BE HUMAN READABLE
            '''

        for e in self.all_errors:

            is_high_confidence = not e.is_warning
            is_low_confidence = e.is_warning

            if is_high_confidence and not show_high_confidence:
                continue
            if is_low_confidence and not show_low_confidence:
                continue

            #print '- '*40

            if e.is_warning:
                confidence = 'low'
            else:
                confidence = 'high'


            if e.ERROR_TYPE == FrameErrorTypes.MISSING_FRAME:
                print '- '*40
                print e.get_error_desc()
                if e.var_name == 'publish':
                    print "Missing frame id for the published message on line %s (%s)." % (e.linenr, e.file_name)
                else:
                    print "Missing frame id for variable %s on line %s (%s)." % (e.var_name, e.linenr, e.file_name)

            elif e.ERROR_TYPE == FrameErrorTypes.MISSING_CHILD_FRAME:
                print '- '*40
                print e.get_error_desc()
                print "Missing child frame id for variable %s on line %s (%s)." % (e.var_name, e.linenr, e.file_name)

            elif e.ERROR_TYPE == FrameErrorTypes.INVALID_FRAMES:
                print '- '*40
                print 'REDUNDANT_TRANSFORM'
                s = (e.values[2]+' ') if e.values[2] else ''
                print "%sTransform between frames on line %s (%s). Transform from %s to %s." % \
                        (s, e.linenr, e.file_name, e.values[0], e.values[1])

            elif e.ERROR_TYPE == FrameErrorTypes.INCORRECT_TRANSFORM:
                print '- '*40
                print e.get_error_desc()
                if e.var:
                    print "Incorrect transform for variable %s on line %s (%s). "\
                            "The orientation %s of frame %s does not match the convention %s." % \
                            (e.var_name, e.linenr, e.file_name, e.values[0], e.frame_name, e.values[1])
                else:
                    print "Incorrect transform on line %s (%s). "\
                            "The orientation %s of frame %s does not match the convention %s." % \
                            (e.linenr, e.file_name, e.values[0], e.frame_name, e.values[1])

            elif e.ERROR_TYPE == FrameErrorTypes.MULTIPLE_PARENTS_IN_FRAME_TREE:
                print '- '*40
                print e.get_error_desc()
                print "Multiple parents in the frame tree for frame %s in %d file-groups. Parents: %s. File-Groups: %s" % \
                      (e.frame_name, len(e.file_name), e.values, e.file_name) 

            elif e.ERROR_TYPE == FrameErrorTypes.CYCLE_IN_FRAME_TREE:
                print '- '*40
                print e.get_error_desc()
                print "Cycle in the frame tree in %d file-groups. Cycles: %s. File-Groups: %s" % \
                      (len(e.file_name), e.values, e.file_name)

            elif e.ERROR_TYPE == FrameErrorTypes.MULTIPLE_PUBLISH_SOURCES_FOR_TRANSFORM:
                pass
                #print e.get_error_desc()
                #print "Multiple publish sources for the transform from %s to %s." % \
                #        (e.values[0], e.values[1])

            elif e.ERROR_TYPE == FrameErrorTypes.INCORRECT_FRAME_ORDER_IN_TREE:
                print '- '*40
                print e.get_error_desc()
                print "Reversed frame order in the frame tree. Incorrect order: %s" % (e.values,)

            elif e.ERROR_TYPE == FrameErrorTypes.NON_CONNECTED_FRAMES:
                pass
                #print e.get_error_desc()
                #print "WARNING: Transform not available between frames %s and %s on line %s (%s). "\
                #        "Possibly non connected frames in the frame tree." % \
                #        (e.values[0], e.values[1], e.linenr, e.file_name)

            elif e.ERROR_TYPE == FrameErrorTypes.REVERSED_NAME:
                print '- '*40
                print e.get_error_desc()
                print "WARNING: Transform with name %s may be reversed on line %s (%s)." % \
                        (e.var_name, e.linenr, e.file_name)

            elif e.ERROR_TYPE == FrameErrorTypes.NED_NULL:
                print '- '*40
                print e.get_error_desc()
                print "WARNING: Transform %s on line %s is a ned transform, and should have 0 displacement and non-zero rotation (%s). "\
                        "It has %s displacement and %s rotation." % \
                        (e.var_name, e.linenr, e.filename, e.values.get('disp'), e.values.get('rot'))

            elif e.ERROR_TYPE == FrameErrorTypes.SENSOR_NULL:
                print '- '*40
                print e.get_error_desc()            
                print "WARNING: Transform %s on line %s is a %s transform (%s). Should it be null?" % \
                        (e.var_name, e.linenr, e.values, e.file_name)


    def print_frame_errors(self, errors_file, restart, show_high_confidence=True, show_low_confidence=True):
        if self.combine_errors:
            self.all_errors.extend(self.unique_errors)
            self.combine_errors = False

        mode = 'w' if restart else 'a'

        with open(errors_file, mode) as f:
            for e in self.all_errors:
                is_high_confidence = not e.is_warning
                is_low_confidence = e.is_warning

                if is_high_confidence and not show_high_confidence:
                    continue
                if is_low_confidence and not show_low_confidence:
                    continue
                
                etype = e.get_error_desc()

                if (e.ERROR_TYPE == FrameErrorTypes.MISSING_FRAME
                    or e.ERROR_TYPE == FrameErrorTypes.MISSING_CHILD_FRAME
                    or e.ERROR_TYPE == FrameErrorTypes.REVERSED_NAME
                    or e.ERROR_TYPE == FrameErrorTypes.NED_NULL
                    or e.ERROR_TYPE == FrameErrorTypes.SENSOR_NULL):

                    f.write("%s; %s; %s; %s\n" % (etype, e.var_name, e.linenr, e.file_name))

                elif (e.ERROR_TYPE == FrameErrorTypes.INCORRECT_TRANSFORM):

                    f.write("%s; %s; %s; %s\n" % (etype, e.frame_name, e.linenr, e.file_name))

                elif (e.ERROR_TYPE == FrameErrorTypes.MULTIPLE_PARENTS_IN_FRAME_TREE):

                    f.write("%s; %s; %s\n" % (etype, e.frame_name, e.values))

                elif (e.ERROR_TYPE == FrameErrorTypes.CYCLE_IN_FRAME_TREE
                    or e.ERROR_TYPE == FrameErrorTypes.INCORRECT_FRAME_ORDER_IN_TREE):

                    f.write("%s; %s\n" % (etype, e.values))
           
                elif (e.ERROR_TYPE == FrameErrorTypes.INVALID_FRAMES
                    or e.ERROR_TYPE == FrameErrorTypes.MULTIPLE_PUBLISH_SOURCES_FOR_TRANSFORM
                    or e.ERROR_TYPE == FrameErrorTypes.NON_CONNECTED_FRAMES):

                    f.write("%s; %s; %s; %s; %s\n" % (etype, e.values[0], e.values[1], e.linenr, e.file_name))


    def collect_transform_vars_data(self, configuration):
        for v in configuration.variables:

            if v.isTransform and v.frames:

                if not v.nameToken:
                    continue
 
                file_name = self.get_file_name(v.nameToken)
                if file_name.endswith(('.h', '.hpp')):
                    continue

                parent_frame = None
                child_frame = None
                                
                d = v.vals['disp'] if 'disp' in v.vals else None
                r = v.vals['rot'] if 'rot' in v.vals else None

                var_token = None
                var_name = None
                var_frame = None

                for name, frame_list in v.frames.iteritems():
                    frame = frame_list[-1]['type']
                    if len(frame) == 2 and frame[0] and frame[1]:
                        if frame[-1].id != 'xyz':
                            var_token = frame_list[-1]['token']
                            var_name = name
                            var_frame = frame

                if var_frame:
                    result_frame = self.th.recurse_and_get_frame_type(var_frame)

                    if result_frame:                        
                        parent_frame = result_frame[0]
                        child_frame = result_frame[1]

                        with open('name_transforms.txt', 'a') as ntfile:
                            ntfile.write("%s,%s,%s,DLIM,%s\n" % (self.target, var_name, parent_frame, child_frame))

                with open('value_transforms.txt', 'a') as vtfile:
                    vtfile.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (self.target, var_name, parent_frame, child_frame, d, r))


    def collect_stats(self):
        with open('sendtf_stats.txt', 'a') as stfile:
            stfile.write("%s,%s,%s,%s\n" % (self.target, dd.TOTAL_SEND_TF_COUNT, dd.USED_SEND_TF_COUNT, dd.CHECKED_SEND_TF_COUNT))




