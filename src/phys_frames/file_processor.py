#Copyright 2021 Purdue University, University of Virginia.
#All rights reserved.


import sys
import os
import fnmatch
import traceback
import copy
import lxml.etree as ET
#import cmakelists_parsing.parsing as CP
import parsing as CP
# TRY FOLLOWING PACKAGE INSTEAD OF ABOVE: cmakeast


class FileProcessor:

    def __init__(self, target=''):
        self.target = target
        self.pkg_name_dict = {} # package_name : package_path
        self.node_files_dict = {} # node_exe : cpp_files_list
        self.launch_dict = {} # launch_path : launch_content_dict
        self.global_variables = {}
        self.pending_link_libs = {}


    def resolve_args(self, name):
        if '$' not in name:
            #print "Launch_File: %s" % (name,)
            return name

        # FIND ARG
        idx1 = name.find('$(')
        if idx1 == -1:
            #print "Arg error in launch file name %s" % (name,)
            return None

        idx2 = name.find(')', idx1)
        if idx2 == -1:
            #print "Arg error in launch file name %s" % (name,)
            return None

        start = name[:idx1]
        arg = name[idx1+2:idx2]
        end = name[idx2+1:]

        parts = arg.split(' ')
        parts = [p for p in parts if p]
        if len(parts) != 2 or parts[0] != 'find':
            #print "Invalid command in launch file name %s" % (name,)
            return None

        pkg_name = parts[1]
        if pkg_name not in self.pkg_name_dict:
            #print "Non-local package in launch file name %s" % (name,)
            return None

        return start + self.pkg_name_dict[pkg_name] + end


    def parse_from_xml_tree(self, root):
        launch_files = []
        node_exes = []
        for child in root:
            if len(child) >= 2:
                (l,n) = self.parse_from_xml_tree(child)
                launch_files = launch_files + l
                node_exes = node_exes + n
            if child.tag == "include" and 'file' in child.attrib:
                file_name = child.attrib['file']
                resolved_name = self.resolve_args(file_name)
                if resolved_name:
                    #file_path = os.path.join(self.target + resolved_name)
                    #if os.path.exists(file_path):
                        #launch_files.append(file_path)
                    launch_files.append(resolved_name)
            elif child.tag == "node" and 'pkg' in child.attrib and 'type' in child.attrib:
                pkg_name = child.attrib['pkg']
                if pkg_name not in self.pkg_name_dict:
                    #print "Non-local package node %s" % (pkg_name)
                    continue

                exe_name = child.attrib['type']
                if exe_name not in self.node_files_dict:
                    #print "Executable %s not found" % (exe_name)
                    continue

                self.mark_node_as_used(exe_name)
                node_exes.append(exe_name)                
                    
        return launch_files, node_exes


    def add_launch_file(self, path, launch_files, node_exes):
        file_name = os.path.relpath(path, self.target)
        self.launch_dict[file_name] = {'launch_files': launch_files,
                                       'nodes': node_exes,
                                       'is_child': False}
                 

    def process_launch_file(self, path):
        try:
            parser = ET.XMLParser(ns_clean=True,recover=True)
            tree = ET.parse(path,parser)
            launch_files, node_exes = self.parse_from_xml_tree(tree.getroot())
            self.add_launch_file(path, launch_files, node_exes)
        
        except ET.ParseError:
            print("Tree parse error in file %s"%path)

        except UnicodeEncodeError:
            print("Unicode error")

        #except TypeError as error:
        #    print("error here2")
      
        except Exception as error:
            traceback.print_exc()
            print(error)


    def add_package(self, path, pkg_name):
        file_name = os.path.relpath(path, self.target)
        dir_name = os.path.dirname(file_name)
        self.pkg_name_dict[pkg_name] = dir_name


    def process_package_file(self, path):
        try:
            parser = ET.XMLParser(ns_clean=True,recover=True)
            tree = ET.parse(path,parser)
            root = tree.getroot()
            if root.tag == 'package':
                for child in root:
                    if child.tag == 'name':
                        self.add_package(path, child.text)
                        break        

        except ET.ParseError:
            print("Tree parse error in file %s"%path)

        except UnicodeEncodeError:
            print("Unicode error")

        except TypeError as error:
            print("error here2")
      
        except Exception as error:
            traceback.print_exc()
            print(error)


    def process_pending_links(self):
        #print "\nGLOBAL_VARIABLES: %s\n" % (self.global_variables)
        #print "\nPENDING: %s\n" % (self.pending_link_libs)
        for exe_name, libs in self.pending_link_libs.iteritems():
            cpp_files = []
            for l in libs:
                name = self.get_cmake_name(l, self.global_variables)
                if name in self.node_files_dict:
                    cpp_files.extend(self.node_files_dict[name]['cpp_files'])
            if cpp_files:
                self.add_cmake_exe(exe_name, cpp_files)


    def track_pending_link_libs(self, exe_name, libs):
        if exe_name in self.pending_link_libs:
            self.pending_link_libs[exe_name].extend(libs)
        else:
            self.pending_link_libs[exe_name] = libs


    def mark_node_as_used(self, exe_name):
        if exe_name in self.node_files_dict:
            self.node_files_dict[exe_name]['is_used'] = True
        else:
            print "Error: node %s not found for marking" % (exe_name,)


    def add_cmake_exe(self, exe_name, cpp_files):
        if exe_name in self.node_files_dict:
            self.node_files_dict[exe_name]['cpp_files'].extend(cpp_files)
        else:
            self.node_files_dict[exe_name] = {'cpp_files': cpp_files,
                                              'is_used': False}


    def get_cmake_name(self, name, variables, default_None=True):
        idx1 = name.find('${')
        idx2 = name.find('}', idx1)
        if idx1 != -1 and idx2 != -1:
            var_name = name[idx1+2:idx2]

            if var_name in variables:
                value = variables[var_name]
                if isinstance(value, list):
                    if len(value) > 1:
                        return value
                    elif len(value) == 1:
                        value = value[0]
                    else:
                        return None if default_None else name
                new_name = name[:idx1] + value + name[idx2+1:]      
                return new_name
            else:
                return None if default_None else name
        else:
            return name


    def parse_from_cmake_tree(self, root, path):
        # tree is a list of commands

        path = os.path.dirname(path)
        relpath = os.path.relpath(path, self.target)

        #print "\nGLOBAL_VARIABLES: %s\n" % (self.global_variables)

        variables = copy.deepcopy(self.global_variables)
        for child in root:
            if isinstance(child, CP._Command):
                cmd = child.name.lower()
                args = child.body

                if cmd == 'add_executable' or cmd == 'add_library':
                    exe_name = self.get_cmake_name(args[0].contents, variables)
                    if not exe_name:
                        continue
                    cpp_files = []
                    for arg in args[1:]:
                        name = self.get_cmake_name(arg.contents, variables)
                        if not name:
                            continue
                        if isinstance(name, list):
                            cpp_files.extend(name)
                        else:
                            name = os.path.join(relpath, name)
                            cpp_files.append(name)
                    self.add_cmake_exe(exe_name, cpp_files)

                elif cmd == 'target_link_libraries':
                    exe_name = self.get_cmake_name(args[0].contents, variables)
                    if not exe_name:
                        continue
                    cpp_files = []
                    libs = []
                    for arg in args[1:]:
                        name = self.get_cmake_name(arg.contents, variables, default_None=False)
                        if name in self.node_files_dict:
                            cpp_files.extend(self.node_files_dict[name]['cpp_files'])
                        else:
                            # PROCESS AFTER ALL CMAKELISTS.TXT FILES ARE PARSED
                            libs.append(name)
                    self.add_cmake_exe(exe_name, cpp_files)
                    self.track_pending_link_libs(exe_name, libs)

                elif cmd == 'project':
                    name = self.get_cmake_name(args[0].contents, variables)
                    if name:
                        variables['PROJECT_NAME'] = name

                elif cmd == 'set':
                    var_name = self.get_cmake_name(args[0].contents, variables)
                    if not var_name:
                        continue
                    value = []
                    for arg in args[1:]:
                        name = self.get_cmake_name(arg.contents, variables)
                        if not name:
                            continue
                        if isinstance(name, list):
                            value.extend(name)
                        else:
                            name = os.path.join(relpath, name)
                            value.append(name)
                    variables[var_name] = value

                elif cmd == 'catkin_package':
                    if 'PROJECT_NAME' not in variables:
                        continue
                    lib_mode = False
                    value = []
                    for arg in args:
                        name = self.get_cmake_name(arg.contents, variables)
                        if not name:
                            continue
                        if name == 'LIBRARIES':
                            lib_mode = True
                        elif lib_mode:
                            if isinstance(name, list):
                                value.extend(name)
                            elif name in ['CATKIN_DEPENDS', 'DEPENDS', 'INCLUDE_DIRS']:
                                lib_mode = False
                            else:
                                value.append(name)
                    var_name = variables['PROJECT_NAME'] + '_LIBRARIES'
                    variables[var_name] = value
                    self.global_variables[var_name] = value


    def process_cmake_file(self, path):
        try:
            with open(path) as f:
                contents = f.read()
            tree = CP.parse(contents) 
            #print repr(tree)
            self.parse_from_cmake_tree(tree, path)

        #except AttributeError:
        #    print("Attibute error")

        except Exception as error:
            #traceback.print_exc()
            #print(error)
            print("EXCEPTION: CMake Parse error")


    def find_files(self, directory, pattern):
        if os.path.isfile(directory):
            yield directory

        # THIS IS A DIRECTORY
        for root, dirs, files in os.walk(directory):
            root = os.path.abspath(root)
            for basename in files:
                if fnmatch.fnmatch(basename.lower(), pattern):
                    filename = os.path.join(root, basename)
                    yield filename


    def process_target(self):
        for cmake_file in self.find_files(self.target, 'cmakelists.txt'):
            #print "\nCMAKE_FILE: %s\n" % (cmake_file,)
            if not os.path.exists(cmake_file):
                # THIS IS A SYMLINK WITH TARGET THAT DOES NOT EXIST
                continue
            self.process_cmake_file(cmake_file)

        self.process_pending_links()

        for package_file in self.find_files(self.target, 'package.xml'):
            self.process_package_file(package_file)

        for launch_file in self.find_files(self.target, '*.launch'):
            self.process_launch_file(launch_file)

        #debug_print_node_files_dict(self.node_files_dict)
        #debug_print_pkg_name_dict(self.pkg_name_dict)
        #debug_print_launch_dict(self.launch_dict)


    def get_file_group(self, f):
        file_group = [f]

        if f not in self.launch_dict:
            return file_group
  
        d = self.launch_dict[f]     
      
        for n in d['nodes']:
            if n in self.node_files_dict:
                file_group.extend(self.node_files_dict[n]['cpp_files'])

        for l in d['launch_files']:
            f_g = self.get_file_group(l)
            file_group.extend(f_g)

        return list(set(file_group))


    def get_file_groups_list(self):
        # A LIST OF TUPLES: (GROUP_ID, GROUPS)
        file_groups = []

        for f in self.launch_dict:
            file_group = self.get_file_group(f)
            file_groups.append((f, file_group))

        for n in self.node_files_dict:
            if not self.node_files_dict[n]['is_used']:
                file_groups.append((n, self.node_files_dict[n]['cpp_files']))

        return file_groups


def debug_print_launch_dict(l_dict):
    print "\nLAUNCH DICTIONARY:\n"
    for path, val in l_dict.iteritems():
        print "%s : %s" % (path, val)


def debug_print_pkg_name_dict(p_dict):
    print "\nPACKAGE DICTIONARY:\n"
    for name, path in p_dict.iteritems():
        print "%s : %s" % (name, path)


def debug_print_node_files_dict(n_dict):
    print "\nNODE DICTIONARY:\n"
    for name, val in n_dict.iteritems():
        print "%s : %s" % (name, val)


def print_groups(groups_list):
    pass


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Include the target path as the first command line argument")
        print("No other command line arguments allowed")
        exit()

    fproc = FileProcessor(sys.argv[1])

    fproc.process_target()
    file_groups_list = fproc.get_file_groups_list()
    print_groups(file_groups_list)



