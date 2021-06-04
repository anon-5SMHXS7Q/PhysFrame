#Copyright 2021 Purdue University, University of Virginia.
#All rights reserved.


import os
import lxml.etree as ET
import traceback
import re
import sys
from itertools import product
from symbol_helper import get_body
import linter_rules as rules
#import linter_rules_2 as rules
#import linter_rules_5 as rules
#import linter_rules_10 as rules


#Error 1: self_transform
#Error 2: dup_name
#Error 3: dup_sig
#Error 4: reversed_name
#Error 5: rot_degrees
#Error 6: int_suffix
#Error 7: ned_transform
#Error 8: sensor_null
#Error 9: sig_implication
#Error 10: name_implication
#Error 11: sig_null_disp
#Error 12: name_null_disp
#Error 13: sig_null_rot
#Error 14: name_null_rot


LINTER_ERROR_TYPES = { 1: 'self_transform',
                       2: 'dup_name',
                       3: 'dup_sig',
                       4: 'reversed_name',
                       5: 'rot_degrees',
                       6: 'int_suffix',
                       7: 'ned_transform',
                       8: 'sensor_null',
                       9: 'sig_implication',
                      10: 'name_implication',
                      11: 'sig_null_disp',
                      12: 'name_null_disp',
                      13: 'sig_null_rot',
                      14: 'name_null_rot'
                     }


class Transform:

    def is_null_disp(self):
        return self.dx == 0 and self.dy == 0 and self.dz == 0

    def is_null_rot_val(self):
        return (self.r == 0 and self.p == 0 and self.y == 0 and not self.isQuat) or (self.qx == 0 and self.qy == 0 and self.qz == 0 and self.isQuat)

    def is_null_rot(self):
        if self.frame and len(self.frame)==2:
            f = self.frame[0]
            cf = self.frame[1]
            return (f.x_dir == cf.x_dir and f.y_dir == cf.y_dir and f.z_dir == cf.z_dir)
        else:
            return False


    def is_null(self):
        return self.is_null_disp() and self.is_null_rot()

    def parse_args(self,args):
        if '$' in args:
            raise Exception("Arg error: Current arguments contain a macro\n{args}".format(args=args))
        
        args = args.replace(",","").strip().split()
      
        try:
            float(args[-1])
            args = args[:-1]
        except:
            pass
        if not args or len(args) < 8:
            raise Exception("Arg error: Issue with current arguments\n{args}".format(args=args))

        
        if len(args) == 8:
            error = False
            for i in range(6):
                try:
                    val = float(args[i])
                except:
                    error = True
                    break
            if error:
                raise Exception("Arg error: Some nonfloat arguments \n{args}".format(args=args))
        
        elif len(args) >= 9:
            error = False
            for i in range(7):
                try:
                    val = float(args[i])
                except:
                    error = True
                    break
            if error:
                raise Exception("Arg error: Some nonfloat arguments \n{args}".format(args=args))

        parent = args[-2]
        child = args[-1]
        ####if parent[0] == '/':
        ####    parent = parent[1:]
        ####if child[0] == '/':
        ####    child = child[1:]

        dx = float(args[0])
        dy = float(args[1])
        dz = float(args[2])

        r = 0
        p = 0
        y = 0
        qx = 0
        qy = 0
        qz = 0
        qw = 0
  
        isQuat = False

        if len(args) == 8:
            y = float(args[3])
            p = float(args[4])
            r = float(args[5])

        elif len(args) == 9:
            qx = float(args[3])
            qy = float(args[4])
            qz = float(args[5])   
            qw = float(args[6])   
            isQuat = True
        else:
            raise Exception("Arg error: Invalid arg length\n{args}".format(args=args))
        
        self.parent = parent.replace("'","")
        self.child = child.replace("'","")
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.r = r
        self.p = p
        self.y = y
        self.qx = qx
        self.qy = qy
        self.qz = qz
        self.qw = qw
        self.isQuat = isQuat
        #args_tuple = (parent,child,dx,dy,dz,r,p,y,qx,qy,qz,qw,isQuat)
        self.frame = None
    
    def __str__(self):
        return "Name={name}, Parent={parent}, Child={child}".format(name=self.name, parent=self.parent, child=self.child)

    def __init__(self,node,ns):
        
            if 'name' not in node.attrib or 'args' not in node.attrib:
                raise Exception("A static transform publisher is missing its name or args")

            if 'ns' in node.attrib:
                new_ns = node.attrib['ns'].strip().replace("'","")
                ns = ns +'/'+ new_ns if ns else new_ns
             
            if ns:
                self.name = ns +'/'+ node.attrib['name'].strip().replace("'","")
            else:
                self.name = node.attrib['name'].strip().replace("'","")

            self.skipped = 'args' not in node.attrib or '$' in node.attrib['args']
            self.linenr = node.sourceline

            if not self.skipped:
                try:
                    self.parse_args(node.attrib['args'])
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as e:
                    raise(e)
                    traceback.print_exc()
                    print(e)


def parse_from_tree(root,ns=''):

    transform_list = []
    error_list = []

    for child in root:
        if len(child) > 0:
            new_ns = ns
            if child.tag == "group" and 'ns' in child.attrib:
                new_ns = child.attrib['ns'].strip().replace("'","")
                if ns:
                    new_ns = ns +'/'+ new_ns
            
            (t,e) = parse_from_tree(child,new_ns)
            transform_list = transform_list + t
            error_list = error_list + e

        if 'type' in child.attrib and child.attrib['type'] == 'static_transform_publisher':
            #print("found static")
            #print(type(child))
            try:
                transform_list.append(Transform(child,ns))
            except Exception as error:
                if str(error) == "A static transform publisher is missing its name or args":
                    error_list.append("A static transform publisher is missing its name or args")
                    continue
                elif str(error).startswith("Arg error"):
                    error_list.append(str(error))
                    continue
                else:
                    print(str(error))
                    raise(error)

    return (transform_list,error_list)

def process_file(path):
    if not os.path.isfile(path):
        raise Exception("{path} is not a file!".format(path=path))
    try:
        parser = ET.XMLParser(ns_clean=True,recover=True)
        tree = ET.parse(path,parser)
        transform_list,error_list = parse_from_tree(tree.getroot())
        if transform_list == []:
            error_list.append("CONTAINS NO PARSEABLE TRANSFORMS")
        return (transform_list, error_list)
    except ET.ParseError:
        print("Tree parse error in file %s"%path)
        return ([], ["Tree parse error"])
    except UnicodeEncodeError:
        print("Unicode error")
        return ([], ["Unicode error"])
    except TypeError as error:
        print("error here2")
        print(error)      
    except Exception as error:
        traceback.print_exc()
        print(error)
        
    return ([], [])

def validate_transforms(transform_list):

    ####transform_list = [t  for t in transform_list if not t.skipped]
    error_list = []

    error_list = error_list + v_self_transforms(transform_list)
    error_list = error_list + v_dup_names(transform_list)
    error_list = error_list + v_dup_sigs(transform_list)
    error_list = error_list + v_reversed_names(transform_list)
    error_list = error_list + v_rotation_unit(transform_list)
    error_list = error_list + v_suffixes(transform_list)
    error_list = error_list + v_ned_transform(transform_list)
    error_list = error_list + v_sensor_null(transform_list)
    error_list = error_list + v_sig_implication(transform_list)
    error_list = error_list + v_name_implication(transform_list)
    error_list = error_list + v_sig_null_disp(transform_list)
    error_list = error_list + v_name_null_disp(transform_list)
    error_list = error_list + v_sig_null_rot(transform_list)
    error_list = error_list + v_name_null_rot(transform_list)
    return error_list

#Returns tuple of (false) if valid
#Returns tuple of (true, error string) if invalid
def v_self_transforms(transform_list):
    error_list = []
    for transform in transform_list:
        if transform.parent==transform.child:
            error_list.append("1 ERROR - self_transform: Transform {name} is a self transform".format(name=transform.name))
    return error_list

#Returns list of error strings
#Empty list signifies no errors
def v_dup_names(transform_list):
    name_set = {}
    for transform in transform_list:
        name = transform.name
        if name not in name_set:
            name_set.update({name:0})
        name_set.update({name:name_set[name]+1})

    error_list = []
    for name, count in name_set.items():
        if count > 1:
            error_list.append("2 WARNING - dup_name: The name {name} is duplicated among transforms".format(name=name))

    return error_list

def v_dup_sigs(transform_list):
    sig_set = {}
    for transform in transform_list:
        sig = (transform.parent,transform.child)
        if sig not in sig_set:
            sig_set.update({sig:0})
        sig_set.update({sig:sig_set[sig]+1})

    error_list = []
    for sig, count in sig_set.items():
        if count > 1:
            error_list.append("3 WARNING - dup_sig: The signature {parent}->{child} is duplicated among transforms".format(parent=sig[0], child=sig[1]))

    return error_list

def v_reversed_names(transform_list):
    error_list = []

    for transform in transform_list:
        name = transform.name.lower()
        child = transform.child.lower()
        parent = transform.parent.lower()
        if (name == child+parent
            or name == child+"_"+parent
            or name == child+"to"+parent
            or name == child+"_to_"+parent
            or name == child+"2"+parent
            or name == child+"_2_"+parent
            or parent+"in"+child in name 
            or parent+"_in_"+child in name
            or parent+"_rel_"+child in name 
            or parent+"_wrt_"+child in name):
            error_list.append("4 WARNING - reversed_name: Transform with name {name} may be reversed".format(name=name))
        else:
            conn_in_name = any(substr in transform.name for substr in ['To', '_to_', '2', '_2_', 'In', '_in_', '_rel_', '_wrt_'])
            lp = re.split(r'[_|\.]', parent)
            lc = re.split(r'[_|\.]', child)
            pairs = list(product(lp, lc))
            for p, c in pairs:
                if p == c:
                    continue
                if (not conn_in_name and any((c+substr+p in name and c+substr+p not in child) for substr in ['', '_'])) or \
                        any(c+substr+p in name for substr in ['to', '_to_', '2', '_2_']) or \
                        any(p+substr+c in name for substr in ['in', '_in_', '_rel_', '_wrt_']):
                    error_list.append("4 WARNING - reversed_name: Transform with name {name} may be reversed".format(name=name))
                    break
            
    return error_list

def v_rotation_unit(transform_list):
    error_list = []

    for transform in transform_list:
        if transform.isQuat:
            continue
        if (transform.r > 2*3.14 and 
            (transform.r%2.5 < 0.1 and transform.r%2.5 > -0.1)):
            error_list.append("5 WARNING - rot_degrees: Transform {name} may have roll in degrees".format(name=transform.name))
        if (transform.p > 2*3.14 and 
            (transform.p%2.5 < 0.1 and transform.p%2.5 > -0.1)):
            error_list.append("5 WARNING - rot_degrees: Transform {name} may have pitch in degrees".format(name=transform.name))
        if (transform.y > 2*3.14 and 
            (transform.y%2.5 < 0.1 and transform.y%2.5 > -0.1)):
            error_list.append("5 WARNING - rot_degrees: Transform {name} may have yaw in degrees".format(name=transform.name))
    return error_list

def v_suffixes(transform_list):
    error_list = []

    name_idxs = []
    parent_idxs = []
    child_idxs = []

    idx_regex = "[0-9]+$"
    for transform in transform_list:
        name_match = re.search(idx_regex,transform.name)
        if name_match != None:
            name_idxs.append(int(name_match.group()))
        
        parent_match = re.search(idx_regex,transform.parent)
        if parent_match != None:
            parent_idxs.append(int(parent_match.group()))
        
        child_match = re.search(idx_regex,transform.child)
        if child_match != None:
            child_idxs.append(int(child_match.group()))

    #Remove duplicates in list and sort
    name_idxs = list(dict.fromkeys(name_idxs))
    name_idxs.sort()
    parent_idxs = list(dict.fromkeys(parent_idxs))
    parent_idxs.sort()
    child_idxs = list(dict.fromkeys(child_idxs))
    child_idxs.sort()

    #If there are at least 3, error on any missing intermediate
    if len(name_idxs) >= 3:
        for i in range(len(name_idxs)-1):
            if name_idxs[i] != name_idxs[i+1]-1:
                error_list.append("6 WARNING - int_suffix: May be missing a transform with name having suffix {s}".format(s=name_idxs[i+1]-1))
    if len(parent_idxs) >= 3:
        for i in range(len(parent_idxs)-1):
            if parent_idxs[i] != parent_idxs[i+1]-1:
                error_list.append("6 WARNING - int_suffix: May be missing a transform with parent having suffix {s}".format(s=parent_idxs[i+1]-1))
    if len(child_idxs) >= 3:
        for i in range(len(child_idxs)-1):
            if child_idxs[i] != child_idxs[i+1]-1:
                error_list.append("6 WARNING - int_suffix: May be missing a transform with child having suffix {s}".format(s=child_idxs[i+1]-1))
    return error_list

def v_ned_transform(transform_list):
    error_list = []
    for transform in transform_list:
        if transform.child.lower().endswith("_ned"):
            if (not transform.is_null_disp()) or transform.is_null_rot():
                error_list.append("7 WARNING - ned_null: Transform {name} is a ned transform and should have 0 displacement".format(name=transform.name))
    return error_list

def v_sensor_null(transform_list):
    sensors = ['openni','imu','kinect','velodyne']

    error_list = []

    for transform in transform_list:
        for sensor in sensors:
            if (sensor in transform.parent) or (sensor in transform.child) or (sensor in transform.name):
                f_body = get_body(transform.parent)
                cf_body = get_body(transform.child)
                if f_body and cf_body and f_body == cf_body:
                    continue
                if transform.is_null():
                    error_list.append("8 WARNING - sensor_null: Transform {name} is a {sensor} transform. Should it be null?".format(name=transform.name, sensor=sensor))     
            #elif (sensor in transform.name):
            #    if transform.is_null():
            #        error_list.append("8 WARNING - sensor_null: Transform {name} is a {sensor} transform. Should it be null?".format(name=transform.name, sensor=sensor))
    
    return error_list

def v_sig_implication(transform_list):

    #These are the implications that must be satisifed
    #Generate an error if there is a key signature in the file, but not
    #the signature that it maps to
    sig_pairs = rules.get_sig_implication_rules()

    #Eliminate duplicates
    sig_pairs = list(dict.fromkeys(sig_pairs))

    error_list = []

    present_sigs = set()
    for transform in transform_list:
        present_sigs.add((transform.parent,transform.child))
    
    for sig,implied in sig_pairs:
        if sig in present_sigs and implied not in present_sigs:
            error_list.append("9 WARNING - sig_co-occurrence: {p1}->{c1} is present. Should {p2}->{c2} also be present?".format(p1=sig[0], c1=sig[1], p2=implied[0], c2=implied[1]))

    return error_list

def v_name_implication(transform_list):

    #These are the implications that must be satisifed
    #Generate an error if there is a key signature in the file, but not
    #the signature that it maps to
    name_pairs = rules.get_name_implication_rules()

    #Eliminate duplicates
    name_pairs = list(dict.fromkeys(name_pairs))

    error_list = []

    present_names = set()
    for transform in transform_list:
        present_names.add(transform.name)
    
    for name,implied in name_pairs:
        if name in present_names and implied not in present_names:
            error_list.append("10 WARNING - name_co-occurrence: {name} is present. Should {implied} also be present?".format(name=name, implied=implied))

    return error_list    

def v_sig_null_disp(transform_list):
    error_list = []

    null_sigs = rules.get_sig_null_disp_rules()

    for transform in transform_list:
        sig = (transform.parent,transform.child)
        name = transform.name
        if sig in null_sigs and not transform.is_null_disp():
            error_list.append("11 WARNING - sig_null_disp_exp: The signature of {name} suggests it should have null displacement, but it does not".format(name=name))

    return error_list

def v_name_null_disp(transform_list):
    error_list = []

    null_names = rules.get_name_null_disp_rules()

    for transform in transform_list:
        name = transform.name
        if name in null_names and not transform.is_null_disp():
            error_list.append("12 WARNING - name_null_disp_exp: The name of {name} suggests it should have null displacement, but it does not".format(name=name))

    return error_list

def v_sig_null_rot(transform_list):
    error_list = []

    null_rot_sigs = rules.get_sig_null_rot_rules()

    for transform in transform_list:
        sig = (transform.parent,transform.child)
        name = transform.name
        if sig in null_rot_sigs and not transform.is_null_rot():
            error_list.append("13 WARNING - sig_null_rot_exp: The signature of {name} suggests it should have null rotation, but it does not".format(name=name))

    return error_list

def v_name_null_rot(transform_list):
    error_list = []

    null_rot_names = rules.get_name_null_rot_rules()

    for transform in transform_list:
        name = transform.name
        if name in null_rot_names and not transform.is_null_rot():
            error_list.append("14 WARNING - name_null_rot_exp: The name of {name} suggests it should have null rotation, but it does not".format(name=name))

    return error_list

def process_all_files():
    maxFileIdx = 30000
    #maxFileIdx = 208
    startIdx = 0

    file_ids_tested = set()
    file_ids_errored = set()

    with open('file_error_counts.txt','w') as f:
        for idx in range(maxFileIdx+1):
            if idx < startIdx:
                continue
            #print(idx)
            dir_path = "../launchFiles/launchFiles{d}/".format(d=(1000*(int(idx/1000))))
            file_name = "{idx}_old.launch".format(idx=idx)
            if os.path.isfile(dir_path+file_name):
                file_ids_tested.add(idx)
                error_list = process_file(dir_path+file_name)
                if len(error_list) > 0:
                    file_ids_errored.add(idx)
                    f.write("File {idx} (old) had {n} errors\n".format(idx=idx, n=len(error_list)))
                    print("File {idx} old errors:".format(idx=idx))
                    for error in error_list:
                        try:
                            print(error)
                        except UnicodeEncodeError:
                            print("Unicode encode error in printing out error")
                    print()

            file_name = "{idx}_new.launch".format(idx=idx)
            if os.path.isfile(dir_path+file_name):
                file_ids_tested.add(idx)
                error_list = process_file(dir_path+file_name)
                if len(error_list) > 0:
                    file_ids_errored.add(idx)
                    f.write("File {idx} (new) had {n} errors\n".format(idx=idx, n=len(error_list)))
                    print("File {idx} new errors:".format(idx=idx))
                    for error in error_list:
                        try:
                            print(error)
                        except UnicodeEncodeError:
                            print("Unicode encode error in printing out error")
                    print()

    print("In total, {n} file ids were tested".format(n=len(file_ids_tested)))
    print("In total, {n} file ids had errors".format(n=len(file_ids_errored)))
    

def print_errors(error_list):
    for error in error_list:
        print(error + '\n')


def print_linter_errors(error_list, launch_file, errors_file, restart):
    mode = 'w' if restart else 'a'

    with open(errors_file, mode) as f:
        for error in error_list:
            err = error.split(' ')
            err_num = int(err[0])
            etype = LINTER_ERROR_TYPES[err_num]

            if err_num in [1, 5, 7]:
                f.write("%s; %s; %s\n" % (etype, err[5], launch_file))
            elif err_num in [2, 3]:
                f.write("%s; %s; %s\n" % (etype, err[6], launch_file))
            elif err_num in [4, 11, 12, 13, 14]:
                f.write("%s; %s; %s\n" % (etype, err[7], launch_file))
            elif err_num == 6:
                f.write("%s; %s; %s\n" % (etype, err[13], launch_file))
            elif err_num == 8:
                f.write("%s; %s; %s; %s\n" % (etype, err[5], err[8], launch_file))
            elif err_num in [9, 10]:
                f.write("%s; %s; %s; %s\n" % (etype, err[4], err[8], launch_file))


if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print("Include the filename to lint as the first command line argument")
        print("No other command line arguments allowed")
        exit()

    filename = sys.argv[1]
    error_list = process_file(filename)
    print_errors(error_list)



