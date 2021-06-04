#Copyright 2021 Purdue University, University of Virginia.
#All rights reserved.


from symbol_helper import SymbolHelper
from frame_type import FrameT
import debug_data as dd
from scipy.spatial.transform import Rotation as R


class TypeHelper:
    
    def __init__(self):
        self.sh = SymbolHelper()
        self.default_frame_type = [FrameT('xyz', 'x', 'y', 'z')]
        self.default_transform_frame_type = [FrameT('xyz', 'x', 'y', 'z'), FrameT('xyz', 'x', 'y', 'z')]
        self.unknown_frame_type = [FrameT('FRAMET_UNKNOWN', 'x', 'y', 'z')]
        self.var_id_dict = {}
        self.frame_orientation_dict = {}
        self.transform_types_dict = {}
        self.std_mobile_frame_ids = ['earth', 'map', 'odom', 'base_link']
        self.mobile_frame_type_order = [FrameT('earth', 'f', 'l', 'u'), 
                                          FrameT('map', 'f', 'l', 'u'),
                                          FrameT('odom', 'f', 'l', 'u'),
                                          FrameT('base_link', 'f', 'l', 'u')
                                        ]
        self.humanoid_frame_type_order = [FrameT('earth', 'f', 'l', 'u'), 
                                          FrameT('map', 'f', 'l', 'u'),
                                          FrameT('odom', 'f', 'l', 'u'),
                                          FrameT('base_link', 'f', 'l', 'u'),
                                          FrameT('ankle', 'f', 'l', 'u'),
                                          FrameT('base_footprint', 'f', 'l', 'u'),
                                          FrameT('sole', 'f', 'l', 'u'),
                                          FrameT('toe', 'f', 'l', 'u'),
                                          FrameT('torso', 'f', 'l', 'u'),
                                          FrameT('gaze', 'f', 'l', 'u'),
                                          FrameT('gripper', 'f', 'l', 'u'),
                                          FrameT('wrist', 'f', 'l', 'u')
                                        ]
        self.transform_frame_tree_type = []
        self.multiple_parents = {}
        self.multiple_sources = set()


    def get_default_frame_type(self):
        return self.default_frame_type


    def get_default_transform_frame_type(self):
        return self.default_transform_frame_type


    def is_default_frame_type(self, frame):
        if frame[-1] and frame[-1].id == 'xyz':
            return True
        
        return False


    def is_non_default_frame_type(self, frame):
        return (not self.is_default_frame_type(frame))


    def get_unknown_frame_type(self):
        return self.unknown_frame_type


    def is_unknown_frame_type_elem(self, f):
        if f and f.id == 'FRAMET_UNKNOWN':
            return True
        
        return False
        

    def create_frame_type(self, id, x_dir, y_dir, z_dir):
        return [FrameT(id, x_dir, y_dir, z_dir)]


    def create_frame_type_for_string(self, frame_id):
        dirs = self.get_frame_orientation(frame_id, default=True)
        if dirs:
            (x_dir, y_dir, z_dir) = dirs
            return [FrameT(frame_id, x_dir, y_dir, z_dir)]
        else:
            return None


    def is_equal(self, frame1, frame2):
        if (not frame1) or (not frame2):
            return False
        else:
            return (frame1.id == frame2.id and frame1.x_dir == frame2.x_dir and \
                    frame1.y_dir == frame2.y_dir and frame1.z_dir == frame2.z_dir)


    def get_frame_type_id(self, frame, idx=0):
        frame_id = frame[idx].id if frame[idx] else None
        if frame_id and (not isinstance(frame_id, basestring)):
            frame_id = 'xxxx'
            #TODO support frame id construction in type checker by storing frame id as a list of 
            #     var_tokens and/or strings i.e. operands of +, and then resolve this list in recurse_and_get
        return frame_id


    #TODO return as list of types [[]]? for now, NO
    #FTYPE
    def find_frame_type(self, token, ret_def=True):
        if not token:
            return None

        frame = None

        if token.isString:
            frame_id = token.str.strip('\"')

            #EMPTY STRING
            if not frame_id:
                return None

            dirs = self.get_frame_orientation(frame_id, default=True)
            if dirs:
                (x_dir, y_dir, z_dir) = dirs
                frame = [FrameT(frame_id, x_dir, y_dir, z_dir)]
            return frame

        if token.str == '*' and token.astOperand1 and (not token.astOperand2):
            # DEREFERENCE
            token = token.astOperand1

        if token.frames:
            frame = token.frames[-1]

        elif token.str == '(' and token.previous:
            # FUNCTION TOKEN

            func_token = token.previous
            if token.previous.str == '>' and token.previous.link and token.previous.link.str == '<' \
                    and token.previous.link.previous:
                func_token = token.previous.link.previous

            if func_token.frames:
                frame = func_token.frames[-1]

            elif func_token.function:
                if func_token.function.return_frames:
                    frame = func_token.function.return_frames[-1]
                if func_token.function.return_arg_var_nr > 0:
                    frame_list = func_token.function.arg_frames[func_token.function.return_arg_var_nr - 1]
                    if frame_list:
                        frame = frame_list[-1]
                if (not frame) and func_token.function.return_type in ['string','std::string', 'auto', 'char']:
                    frame = self.get_unknown_frame_type()

        if not frame:
            name = token.str
            if token.str in ['.', '[', '(']:
                (token, name) = self.sh.find_compound_variable_token_and_name_for_sym_token(token)
                
            if token.variable: #self.sh.has_frame_type(token):
                frame = self.get_frame_type_for_variable_token(token, name)
                if (not frame) and ret_def: 
                    frame = [FrameT((token, name), 'x', 'y', 'z')]

            else:
                # CHECK IN VAR ID MAP
                if token.varId:
                    frame = self.var_id_dict.get(token.varId)
                    if frame:
                        frame = frame[-1]
                    elif ret_def:
                        frame = [FrameT((token, name), 'x', 'y', 'z')]

                # TODO: Try alternative solution of later version of cppcheck
                # HANDLE VARS THAT DO NOT HAVE VARID ASSIGNED BY CPPCHECK
                # .values is non-null for true, false, enum; token is the leaf token because of find...sym_token
                elif token.isName and (not token.values) and (not token.astOperand1) and (not token.astOperand2):
                    frame = self.get_unknown_frame_type()

        if frame:
            for i in range(len(frame)):
                frame_elem = frame[i]
                if frame_elem and isinstance(frame_elem.id, basestring):
                    dirs = self.get_frame_orientation(frame_elem.id)
                    if dirs:
                        frame[i] = FrameT(frame_elem.id, dirs[0], dirs[1], dirs[2]) 

        return frame


    def set_frame_type_for_variable_token(self, var_token, var_name, frame):
        if not var_token.variable:
            # SOME VARIABLES HAVE ONLY VARID
            if var_token.varId:
                if var_token.varId in self.var_id_dict:
                    self.var_id_dict[var_token.varId].append(frame)
                else:
                    self.var_id_dict[var_token.varId] = [frame]
            return

        if var_name.startswith('this.'):
            var_name = var_name.replace('this.', '')

        if var_name in var_token.variable.frames:
            var_token.variable.frames[var_name].append( {'type': frame, 'token': var_token} )
        else:
            var_token.variable.frames[var_name] = [ {'type': frame, 'token': var_token} ]

        if var_token.variable.isTransform:
            f = []
            cf = []
            name = ''
                    
            if ('child_frame_id' in var_name):
                name = var_name.replace('.child_frame_id_', '')
                name = name.replace('.child_frame_id', '')
                cf = list(frame)
            elif ('frame_id' in var_name) or (var_name.endswith('header')):
                name = var_name.replace('.frame_id_', '')
                name = name.replace('.header', '')
                name = name.replace('.frame_id', '')
                f = list(frame)
            else:
                return

            if name in var_token.variable.frames:
                #t_frame = (var_token.variable.frames[name])[-1]['type']
                t_frame = self.get_latest_non_default_frame_type_for_variable_token(var_token, name)

                #TODO resolve tf_frame? if len(tf_frame)==1 with variable tuple in frame_id
                if f:
                    cf = [t_frame[1]] if (t_frame and len(t_frame)==2) else [None]
                elif cf:
                    f = [t_frame[0]] if (t_frame and len(t_frame)==2) else [None]
                    
                f.extend(cf)
                var_token.variable.frames[name].append( {'type': f, 'token': var_token} )
            else:
                if f:
                    cf = [None]
                elif cf:
                    f = [None]
                
                f.extend(cf)
                var_token.variable.frames[name] = [ {'type': f, 'token': var_token} ]
 

    def get_frame_type_for_variable_token(self, var_token, var_name):
        if var_name.startswith('this.'):
            var_name = var_name.replace('this.', '')

        for name in var_token.variable.frames:
            if var_name == name:
                frame = var_token.variable.frames.get(name)
                return frame[-1]['type'] if frame else None

        if self.sh.is_ros_type(var_token.variable) or self.sh.is_ros_transform_type(var_token.variable):
            if var_name == var_token.str:
                for name in var_token.variable.frames:
                    if ('frame_id' in name) or (name.endswith('header')):
                        frame = var_token.variable.frames.get(name)
                        return frame[-1]['type'] if frame else None
                return None
            else:
                root_name = ''
                is_cf = False

                if ('frame_id' in var_name) or (var_name.endswith('header')) :
                    root_name = var_name.replace('.frame_id_', '')
                    root_name = root_name.replace('.header', '')
                    root_name = root_name.replace('.frame_id', '')     
                    
                elif ('child_frame_id' in var_name):
                    root_name = var_name.replace('.child_frame_id_', '')
                    root_name = name.replace('.child_frame_id', '')
                    is_cf = True

                if root_name:
                    for name in var_token.variable.frames:
                        if root_name == name:
                            frame = var_token.variable.frames.get(name)
                            if frame:
                                frame = frame[-1]['type']
                                #TODO resolve frame? if len(frame)==1 with variable tuple in frame_id
                                if var_token.variable.isTransform and len(frame)==2:
                                    frame = [frame[1]] if is_cf else [frame[0]]
                            return frame

        for name in var_token.variable.frames:
            if var_name in name:
                frame = var_token.variable.frames.get(name)
                return frame[-1]['type'] if frame else None

        return None


    def get_latest_non_default_frame_type_from_list(self, frames):
        for i in range(len(frames)-1, -1, -1):
            frame = frames[i]['type']
            if not self.is_default_frame_type(frame):
                return frame

        return None        


    # ASSUMES THAT FRAME TYPE EXISTS FOR VAR_NAME
    def get_latest_non_default_frame_type_for_variable_token(self, var_token, var_name):
        frames = var_token.variable.frames[var_name]
        return self.get_latest_non_default_frame_type_from_list(frames)


    def clear_var_id_dict(self):
        self.var_id_dict.clear()


    def debug_print_var_id_dict(self):
        print "VAR-ID-DICT:\n"

        for key, value in self.var_id_dict.iteritems():
            print "%s: %s\n" % (key, value)


    #TODO
    def clear_frame_orientation(self):
        self.frame_orientation_dict.clear()


    #TODO
    def set_frame_orientation(self, frame_id, dirs):
        if frame_id == 'xyz':
            return

        self.frame_orientation_dict[frame_id] = dirs


    #TODO
    def get_frame_orientation(self, frame_id, default=False):
        if frame_id == 'xyz':
            return None
        elif frame_id in self.frame_orientation_dict:
            return self.frame_orientation_dict[frame_id]
        elif default:
            return self.sh.get_ros_orientation_convention(frame_id)
        else:
            return None
        

    def recurse_and_get_frame_type(self, frame_in):
        frame_out = None
        try:
            frame_out = self.get_frame_type_recursive(frame_in)
            #TODO process the result to generate a list of types
        except RuntimeError:
            print "EXCEPTION: RUNTIME_ERROR during recursion"

        return frame_out


    #TODO
    def get_frame_type_recursive(self, frame_in):

        frame_out = []
        
        for frame_elem in frame_in:
            if not frame_elem:
                frame_out.append(None)

            elif isinstance(frame_elem.id, basestring):
                frame_out.append(frame_elem)

            elif isinstance(frame_elem.id, tuple):
                (var_token, var_name) = frame_elem.id

                if var_token.variable:
                    if var_token.variable.isArgument:
                        arg_frames = self.get_frame_types_for_argument(var_token)
                        if arg_frames:
                            result_frames = []

                            for f in arg_frames:
                                result_frames.append(self.get_frame_type_recursive(f))

                            if all(result_elem==None for result_elem in result_frames):
                                result_frames = None

                            frame_out.append(result_frames)
                        else:
                            frame_out.append(None)        

                    else:
                        result_frame = self.get_frame_type_for_variable_token(var_token, var_name)
                        if result_frame:
                            result_frame = self.get_frame_type_recursive(result_frame)
                            if result_frame:
                                frame_out.extend(result_frame)
                            else:
                                frame_out.append(None)
                        else:
                            frame_out.append(None)

                elif var_token.varId:
                    # CHECK IN VAR ID MAP
                    frame = self.var_id_dict.get(var_token.varId)
                    if frame:
                        frame = frame[-1]
                        frame_out.extend(frame)
                    else:
                        frame_out.append(None)

        if all(frame_elem==None for frame_elem in frame_out):
            frame_out = None

        return frame_out


    def get_frame_types_for_argument(self, var_token):
        if not var_token.variable.isArgument:
            return []

        fscope = var_token.scope
        while fscope:
            if fscope.type == "Function":
                break
            fscope = fscope.nestedIn
            
        if fscope and fscope.function:
            for i, a in fscope.function.argument.iteritems():
                if a == var_token.variable:
                    return fscope.function.arg_frames[int(i)-1]


    def is_valid_transform_type(self, tf_frame):
        if len(tf_frame)==2 and tf_frame[0] and tf_frame[1]:
            if self.is_unknown_frame_type_elem(tf_frame[0]) or self.is_unknown_frame_type_elem(tf_frame[1]):
                return False
            else:
                return (tf_frame[0].id != tf_frame[1].id)
        else:
            return False


    def id_index(self, node, frame):
        for i in range(len(frame)):
            if frame[i].id == node.id:
                return i
        
        return -1


    def clear_transform_frame_tree_type(self):
        self.transform_frame_tree_type = []
        self.multiple_parents = {}
        self.multiple_sources = set()


    def register_transform_type(self, file_name, tf_frame, check_mult_src=True):
        # SAVE TRANSFORM TYPES BY FILE FOR LAUNCH-FILE-BASED FRAME TREE PROCESSING
        if file_name in self.transform_types_dict:
            self.transform_types_dict[file_name].append(tf_frame)
        else:
            self.transform_types_dict[file_name] = [tf_frame]

        #print "\nTRANSFORM_TYPES_DICT: %s = %s\n" % (file_name, tf_frame)
        
        # UPDATE GLOBAL FRAME TREE TYPE
        self.update_transform_frame_tree_type(tf_frame, check_mult_src)


    def construct_transform_frame_tree_type_for_file_group(self, file_group):
        self.clear_transform_frame_tree_type()

        for file_name in file_group:
            if file_name in self.transform_types_dict:
                types = self.transform_types_dict[file_name]
                for t in types:
                    self.update_transform_frame_tree_type(t)

                #print "\nFILE_GROUP_FILE_IN: %s\n" % (file_name,)

            #print "\nFILE_GROUP_FILE_OUT: %s\n" % (file_name,)


    def update_transform_frame_tree_type(self, tf_frame, check_mult_src=True):
        f_list = []
        cf_list = []

        for i in range(len(self.transform_frame_tree_type)):
            frame = self.transform_frame_tree_type[i]

            f_idx = self.id_index(tf_frame[0], frame)
            cf_idx = self.id_index(tf_frame[1], frame)

            if check_mult_src and f_idx >= 0 and cf_idx >= 0 and (cf_idx-f_idx == 1):
                self.multiple_sources.add((tf_frame[0].id, tf_frame[1].id))

            if cf_idx > 0 and frame[cf_idx-1].id != tf_frame[0].id:
                if tf_frame[1].id in self.multiple_parents:
                    self.multiple_parents[tf_frame[1].id].add(frame[cf_idx-1].id)
                    self.multiple_parents[tf_frame[1].id].add(tf_frame[0].id)
                else:
                    self.multiple_parents[tf_frame[1].id] = set([frame[cf_idx-1].id, tf_frame[0].id])

            if f_idx >= 0:
                f_list.append((i, f_idx))

            if cf_idx >= 0:
                cf_list.append((i, cf_idx))


        if (not f_list) and (not cf_list):
            self.transform_frame_tree_type.append(tf_frame)

        elif (not f_list):
            for (cf_frame_idx, node_idx) in cf_list:
                cf_frame = self.transform_frame_tree_type[cf_frame_idx]

                if node_idx == 0:
                    cf_frame.insert(0, tf_frame[0])
                else:
                    new_frame = [tf_frame[0]]
                    new_frame.extend(cf_frame[node_idx:len(cf_frame)])
                    if new_frame not in self.transform_frame_tree_type:
                        self.transform_frame_tree_type.append(new_frame)

        elif (not cf_list):
            for (f_frame_idx, node_idx) in f_list:
                f_frame = self.transform_frame_tree_type[f_frame_idx]

                if node_idx == len(f_frame)-1:
                    f_frame.append(tf_frame[1])
                else:
                    new_frame = f_frame[:node_idx+1]
                    new_frame.append(tf_frame[1])
                    if new_frame not in self.transform_frame_tree_type:
                        self.transform_frame_tree_type.append(new_frame)

        else:
            dup_idx = set()
            new_frames = []

            for (f_frame_idx, f_node_idx) in f_list:
                f_frame = self.transform_frame_tree_type[f_frame_idx]

                if f_node_idx == len(f_frame)-1:
                    dup_idx.add(f_frame_idx)

                for (cf_frame_idx, cf_node_idx) in cf_list:                    
                    if f_frame_idx == cf_frame_idx and (cf_node_idx-f_node_idx == 1):
                        continue
                    
                    cf_frame = self.transform_frame_tree_type[cf_frame_idx]

                    if cf_node_idx == 0:
                        dup_idx.add(cf_frame_idx)

                    new_frame = f_frame[:f_node_idx+1]
                    new_frame.extend(cf_frame[cf_node_idx:len(cf_frame)])
                    if new_frame not in new_frames:
                        new_frames.append(new_frame)                

            dup_idx = sorted(dup_idx, reverse=True)
            for i in dup_idx:
                del self.transform_frame_tree_type[i]

            for new_frame in new_frames:
                if new_frame not in self.transform_frame_tree_type:
                    self.transform_frame_tree_type.append(new_frame)

        #self.debug_print_transform_frame_tree_type()


    def debug_print_transform_frame_tree_type(self, target):
        print '\n' + '= '*20
        print "TREE-TYPE:\n"

        for frame in self.transform_frame_tree_type:
            print "%s\n" % (frame)

        print '= '*20 + '\n'

        if dd.COLLECT_IMPLICIT_CONVENTION_DATA:
            with open('frametree.txt', 'a') as f:
                f.write("***** %s *****\n" % (target))
                for frame in self.transform_frame_tree_type:
                    f.write("%s\n" % (frame))
        

    def create_orientation_type(self, dirs):
        return [tuple(dirs), ('x','y','z')]


    #TTYPE
    def find_orientation_type(self, rot, rot_type):
        if None in rot:
            return None

        r = None
        try:
            if rot_type == 'Q': #QUATERNION
                r = R.from_quat(rot)
            elif rot_type == 'E': #EULER
                r = R.from_euler('ZYX', rot)
            elif rot_type == 'M': #MATRIX
                rot = [[rot[0],rot[1], rot[2]], [rot[3], rot[4], rot[5]], [rot[6], rot[7], rot[8]]]
                r = R.from_dcm(rot)
        except ValueError:
            print "EXCEPTION: VALUE_ERROR while creating rotation"

        if r:
            m = r.as_dcm()
            m = m.round(3)

            dirs = []
            for m_row in m:
                l = (m_row.nonzero())[0].tolist()
                if len(l) != 1:
                    break
                else:
                    idx = l[-1]
                    elem = m_row[idx]
                    if elem not in [1.0, -1.0]:
                        break
                    else:
                        dirs.append(self.get_vector_dir(idx, elem, isNum=True))
                
            if len(dirs) == 3:
                return self.create_orientation_type(dirs)
             
        return None


    def euler_to_quat(self, rot, euler_axes):
        if None in rot:
            return [None]*4
        r = R.from_euler(euler_axes, rot)
        q = r.as_quat()
        q = q.round(3)
        q = q.tolist()
        return q


    def matrix_to_quat(self, rot):
        if None in rot:
            return [None]*4
        rot = [[rot[0],rot[1], rot[2]], [rot[3], rot[4], rot[5]], [rot[6], rot[7], rot[8]]]
        r = R.from_dcm(rot)
        q = r.as_quat()
        q = q.round(3)
        q = q.tolist()
        return q


    def quat_to_matrix(self, rot, flatten=False):
        if None in rot:
            return [None]*9 if flatten else None
        r = R.from_quat(rot)
        m = r.as_dcm()
        m = m.round(3)
        m = m.tolist()
        if flatten:
            m = [elem for row in m for elem in row] #flatten the list of rows
        return m

    
    def quat_mult_quat(self, rot1, rot2):
        if (None in rot1) or (None in rot2):
            return [None]*4
        q1 = R.from_quat(rot1)
        q2 = R.from_quat(rot2)
        r = q1 * q2
        q = r.as_quat()
        q = q.round(3)
        q = q.tolist()
        return q

 
    def matrix_mult_matrix(self, rot1, rot2):
        if (None in rot1) or (None in rot2):
            return [None]*9 
        rot1 = [[rot1[0],rot1[1], rot1[2]], [rot1[3], rot1[4], rot1[5]], [rot1[6], rot1[7], rot1[8]]]
        rot2 = [[rot2[0],rot2[1], rot2[2]], [rot2[3], rot2[4], rot2[5]], [rot2[6], rot2[7], rot2[8]]]
        m1 = R.from_dcm(rot1)
        m2 = R.from_dcm(rot2)
        r = m1 * m2
        m = r.as_dcm()
        m = m.round(3)
        m = m.tolist()
        m = [elem for row in m for elem in row] #flatten the list of rows
        return m

    
    def get_vector_dir(self, idx, sign, isNum=False):
        if idx == 0:
            dir_out = 'x'
        elif idx == 1:
            dir_out = 'y'
        elif idx == 2:
            dir_out = 'z'

        if isNum and sign < 0.:
            dir_out = self.opposite_dir(dir_out)
        elif (not isNum) and '-' in sign:
            dir_out = self.opposite_dir(dir_out)

        return dir_out


    def find_childframe_orientation(self, f_dir, tf_dir):
        tf_f_dir = tf_dir[0]
        tf_cf_dir = tf_dir[1]
        cf_dir = []

        x_dir = None
        y_dir = None
        z_dir = None

        for i in range(3):
            if tf_f_dir[i] == 'x':
                x_dir = f_dir[i]
            elif tf_f_dir[i] == '-x':
                x_dir = self.opposite_dir(f_dir[i])
            elif tf_f_dir[i] == 'y':
                y_dir = f_dir[i]
            elif tf_f_dir[i] == '-y':
                y_dir = self.opposite_dir(f_dir[i])
            elif tf_f_dir[i] == 'z':
                z_dir = f_dir[i]
            elif tf_f_dir[i] == '-z':
                z_dir = self.opposite_dir(f_dir[i])

        for i in range(3):
            axis_dir = None

            if tf_cf_dir[i] in ['x', '-x']:
                axis_dir = x_dir if x_dir else None
            elif tf_cf_dir[i] in ['y', '-y']:
                axis_dir = y_dir if y_dir else None
            elif tf_cf_dir[i] in ['z', '-z']:
                axis_dir = z_dir if z_dir else None
            else:
                continue
   
            if axis_dir and '-' in tf_cf_dir[i]:
                axis_dir = self.opposite_dir(axis_dir) 

            if not axis_dir:
                axis_dir = tf_cf_dir[i]

            cf_dir.append(axis_dir)

        return cf_dir
        

    def opposite_dir(self, dir_in):
        if dir_in == 'f':
            dir_out = 'b'
        elif dir_in == 'b':
            dir_out = 'f'
        elif dir_in == 'l':
            dir_out = 'r'
        elif dir_in == 'r':
            dir_out = 'l'
        elif dir_in == 'u':
            dir_out = 'd'
        elif dir_in == 'd':
            dir_out = 'u'
        elif dir_in == 'x':
            dir_out = '-x'
        elif dir_in == '-x':
            dir_out = 'x'
        elif dir_in == 'y':
            dir_out = '-y'
        elif dir_in == '-y':
            dir_out = 'y'
        elif dir_in == 'z':
            dir_out = '-z'
        elif dir_in == '-z':
            dir_out = 'z'

        return dir_out


    def is_default_frame_elem(self, felem):
        return (felem.id == 'xyz' and felem.x_dir == 'x' and felem.y_dir == 'y' and felem.z_dir == 'z')


    def get_dir(self, dir_in, x_dir, y_dir, z_dir):
        if dir_in in ['x','-x']:
            dir_out = x_dir
        elif dir_in in ['y','-y']:
            dir_out = y_dir
        elif dir_in in ['z','-z']:
            dir_out = z_dir

        if '-' in dir_in:
            dir_out = self.opposite_dir(dir_out)

        return dir_out


    def multiply(self, left_frame, right_frame):
        if not (self.is_default_frame_elem(left_frame[1]) and self.is_default_frame_elem(right_frame[1])):
            return None

        x_dir = self.get_dir(left_frame[0].x_dir, right_frame[0].x_dir, right_frame[0].y_dir, right_frame[0].z_dir)
        y_dir = self.get_dir(left_frame[0].y_dir, right_frame[0].x_dir, right_frame[0].y_dir, right_frame[0].z_dir)
        z_dir = self.get_dir(left_frame[0].z_dir, right_frame[0].x_dir, right_frame[0].y_dir, right_frame[0].z_dir)

        frame = self.create_frame_type('xyz', x_dir, y_dir, z_dir)
        to_frame = self.get_default_frame_type()
        frame.extend(to_frame)

        return frame
                

    #TODO
    def multiply_by_tf_matrix(self, left_frame, right_frame):
        if (not left_frame) or (not right_frame):
            return None
        
        lf_len = len(left_frame)
        rf_len = len(right_frame)
        
        if lf_len == 2 and rf_len == 2:
            if self.is_default_frame_type(left_frame) and self.is_default_frame_type(right_frame):
                return self.multiply(left_frame, right_frame)
        
        return None


    #rotation*translation
    def multiply_by_matrix(self, left_frame, right_frame):
        if (not left_frame) or (not right_frame):
            return None
        
        lf_len = len(left_frame)
        rf_len = len(right_frame)
        
        if lf_len == 2 and rf_len == 2:
            if self.is_default_frame_type(left_frame) and self.is_default_frame_type(right_frame):
                frame = self.multiply(left_frame, right_frame) 
                if self.is_default_frame_elem(frame[0]):  
                    return left_frame

        return None


    def multiply_frame_types(self, left_frame, right_frame):
        if (not left_frame) or (not right_frame):
            return None

        lf_len = len(left_frame)
        rf_len = len(right_frame)
        
        if lf_len == 2 and rf_len == 2:
            if self.is_default_frame_type(left_frame) and self.is_default_frame_type(right_frame):
                return self.multiply(left_frame, right_frame)
            if self.is_equal(left_frame[1], right_frame[0]):
                return [left_frame[0], right_frame[1]]
        elif lf_len == 2 and rf_len == 1 and self.is_equal(left_frame[1], right_frame[0]):
            return [left_frame[0]]

        return None


    def transpose_frame_type(self, frame):
        if frame:
            if len(frame) == 2 and self.is_default_frame_type(frame):
                return self.multiply(frame, frame)
            else:
                frame = frame[:] 
                frame.reverse()
            
        return frame


    def inverse_frame_type(self, frame):
        if frame:
            if len(frame) == 2 and self.is_default_frame_type(frame):
                return self.multiply(frame, frame)
            else:
                frame = frame[:] 
                frame.reverse()
            
        return frame


    
