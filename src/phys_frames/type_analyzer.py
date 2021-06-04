#Copyright (c) 2016, University of Nebraska NIMBUS LAB  John-Paul Ore jore@cse.unl.edu
#Copyright 2018 Purdue University, University of Nebraska--Lincoln.
#Copyright 2021 Purdue University, University of Virginia.
#All rights reserved.


from type_annotator import TypeAnnotator
from type_checker import TypeChecker
from symbol_helper import SymbolHelper 
from type_helper import TypeHelper
from frame_type import FrameT
import cppcheckdata 
import testLinter as lint
from file_processor import FileProcessor
import fnmatch
import os                
import networkx as nx
from collections import OrderedDict, defaultdict


class TypeAnalyzer:

    def __init__(self):
        self.current_file_under_analysis = ''
        self.source_file = ''
        self.function_graph = nx.DiGraph()
        self.all_function_graphs = []
        self.all_sorted_analysis_dicts = []
        self.configurations = []
        line2type = lambda:defaultdict(defaultdict)
        self.file2type = defaultdict(line2type)
        self.should_sort_by_function_graph = True
        self.should_add_manual_type_annotations = False
        self.launch_static_transforms = []
        self.launch_files = []
        self.sh = SymbolHelper()
        self.th = TypeHelper()
        self.should_restart_error_printing = True


    def run_file_processor(self, target=''):
        fproc = FileProcessor(target)
        fproc.process_target()


    def run_linter_collect_all(self, target=''):
        for launch_file in self.find_files(target, '*.launch'):
            file_name = os.path.relpath(launch_file, target)
            print "Found launch: %s" % (file_name)
            self.launch_files.append(file_name)

            self.run_linter_collect(launch_file)


    def run_linter_collect(self, launch_file):
        transform_list, error_list = lint.process_file(launch_file)
        lint.print_errors(error_list)

        self.th.clear_frame_orientation()
        tya = TypeAnnotator(self.th, self.sh)

        transform_list = [t  for t in transform_list if not t.skipped]
        for transform in transform_list:
            frame = tya.find_type_annotation_for_linter_transform(transform)
            transform.frame = frame

        self.launch_static_transforms.append(transform_list)

    
    def run_collect_all(self, target=''):
        # PROCESS C/CPP FILES
        for dump_file in self.find_files(target, '*.dump'):
            print "Found dump: %s" % (os.path.relpath(dump_file, target))
            source_file = dump_file.replace('.dump','')
            self.run_collect(dump_file, source_file)

            # DEBUG
            self.print_debug_output()

        # PROCESS LAUNCH FILES
        self.run_linter_collect_all(target)

        # FIND FILE GROUPS
        #self.run_file_processor(target)


    def run_collect(self, dump_file, source_file=''): 
        ''' input: a cppcheck 'dump' file containing an Abstract Syntax Tree (AST), symbol table, and token list
            input: a cpp source file
            returns: None
            side-effect: updates cppcheck data structure with information about this analysis
            '''
        self.current_file_under_analysis = dump_file
        self.source_file = source_file

        self.th.clear_var_id_dict()
        self.th.clear_frame_orientation()

        # PARSE FILE
        data = cppcheckdata.parsedump(dump_file)
        
        #TODO check for multiple? Now, ONLY TEST THE FIRST CONFIGURATION
        for c in data.configurations[:1]:
            c = self.init_cppcheck_config_data_structures(c)
            self.sh.fill_func_name_dict(c.functions)
 
            self.function_graph = nx.DiGraph()
            # GET DICT OF ALL GLOBALLY SCOPED FUNCTIONS          
            analysis_dict = self.find_functions(c)
            # FIND ORDER FOR FUNCTION GRAPH EXPLORATION
            sorted_analysis_dict = analysis_dict;
            if self.should_sort_by_function_graph:
                self.build_function_graph(analysis_dict)
                sorted_analysis_dict = self.make_sorted_analysis_dict_from_function_graph(analysis_dict)
            self.all_sorted_analysis_dicts.append(sorted_analysis_dict)

            self.collect_types_outside_functions(c.tokenlist)

            for function_dict in sorted_analysis_dict.values():
                self.collect_param_types(function_dict)
            
            # RUN TYPE ANNOTATOR ON ALL TOKEN PARSE TREES FOR EACH FUNCTION
            for function_dict in sorted_analysis_dict.values():
                self.collect_types(function_dict)

            self.sh.clear_func_name_dict()
            self.configurations.append(c)


    def find_files(self, directory, pattern):
        if os.path.isfile(directory):
            yield directory

        # THIS IS A DIRECTORY
        for root, dirs, files in os.walk(directory):
            root = os.path.abspath(root)
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename


    def collect_types_outside_functions(self, tokenlist):
        tya = TypeAnnotator(self.th, self.sh)

        for t in tokenlist:
            if self.should_add_manual_type_annotations and (t.variable or t.str in ['.', '[', '(']): #TODO or t.varId
                if os.path.basename(t.file) in self.file2type:
                    line2type = self.file2type[os.path.basename(t.file)]
                    if t.linenr in line2type:
                        (var_token, var_name) = (t, t.str)
                        if t.str in ['.', '[', '(']:
                            (var_token, var_name) = self.sh.find_compound_variable_token_and_name_for_sym_token(t)
                        if var_name in line2type[t.linenr]:
                            frame = eval(line2type[t.linenr][var_name])
                            frame = map(lambda frame_elem: FrameT(*frame_elem), frame)
                            self.th.set_frame_type_for_variable_token(var_token, var_name, frame)
                            
            if t.scope.type in ['Global', 'Namespace', 'Class']:
                if (not t.astParent) and (t.astOperand1 or t.astOperand2):
                    t.isRoot = True
                    tya.add_type_annotations_outside_functions(t)


    def collect_param_types(self, function_dict):
        tya = TypeAnnotator(self.th, self.sh)

        for root_token in function_dict['root_tokens']:                  
            tya.add_param_type_annotations(root_token)


    def collect_types(self, function_dict):
        tya = TypeAnnotator(self.th, self.sh)

        for root_token in function_dict['root_tokens']:
            tya.apply_and_propagate_values(root_token)                  
            tya.add_type_annotations(root_token)


    def find_type_errors(self, target='', errors_file=''):
        tyc = TypeChecker(self.th, self.sh, target)
        errors_file = 'errors.txt'

        print '\n' + '= '*20
        print 'INCONSISTENCIES:'
        print '= '*20 + '\n'

        # C/CPP FILES
        for i in range(len(self.configurations)):
            tyc.check_types_for_file(self.configurations[i], self.all_sorted_analysis_dicts[i])

        # LAUNCH FILES
        for i in range(len(self.launch_static_transforms)):
            if not self.launch_static_transforms[i]:
                continue

            error_list = lint.validate_transforms(self.launch_static_transforms[i])

            if error_list:
                print '- '*40
                print "FILE: %s\n" % (self.launch_files[i])
                lint.print_errors(error_list)
                lint.print_linter_errors(error_list, self.launch_files[i], errors_file, self.should_restart_error_printing)
                self.should_restart_error_printing = False

            tyc.check_types_for_launch_file(self.launch_static_transforms[i], self.launch_files[i])

        # GLOBAL
        tyc.check_types()

        # FILE_GROUPS
        fproc = FileProcessor(target)
        fproc.process_target()
        file_groups_list = fproc.get_file_groups_list()
        for group_id, file_group in file_groups_list:
            tyc.check_types_for_file_group(group_id, file_group)

        tyc.print_all_errors()
        tyc.print_frame_errors(errors_file, self.should_restart_error_printing)

        print '= '*20 + '\n'


    def load_type_annotations(self, annotation_file):
        # LOAD VARIABLE FRAME TYPE DATA
        with open(annotation_file) as f:
            for item in (line.rstrip('\n') for line in f):
                file_name, line_nr, var_name, frame = item.split(':')
                file_name, line_nr, var_name, frame = file_name.strip(), line_nr.strip(), var_name.strip(), frame.strip()
                self.file2type[file_name][line_nr][var_name] = frame

            if self.file2type:
                self.should_add_manual_type_annotations = True


    def init_cppcheck_config_data_structures(self, cppcheck_configuration):  
        ''' AUGMENT CPPCHECK DATA STRUCTURE WITH ADDITIONAL FEATURES TO SUPPORT THIS ANALYSIS
            '''
        c = cppcheck_configuration

        for t in c.tokenlist:
            t.frames = []
            t.vals = []
            t.isRoot = False            
            
        for f in c.functions:
            f.return_type = None
            f.return_frames = []
            f.return_arg_var_nr = 0
            f.arg_frames = []
            for arg_num in f.argument.keys():
                f.arg_frames.append([])
            f.isAnnotated = False

        for v in c.variables:
            v.frames = {}
            v.is_frame_set = False
            v.vals = {}
            v.isParam = False
            v.isTransform = True if self.sh.is_ros_transform_type(v) else False
            v.isUsed = False
            v.checkFrame = True
            #v.xyz = {}

        return c


    def find_functions(self, a_cppcheck_configuration):
        ''' LINEAR SCAN THROUGH TOKENS TO FIND 'function' TOKENS THAT HAVE GLOBAL SCOPE.
            COLLECT AND RETURN DICT CONTAINING FUNCTION START AND END TOKEN POINTERS 
            output: dict containing function start and end tokens
            '''
        function_dicts = {}

        # FIND FUNCTIONS IN 'SCOPES' REGION OF DUMP FILE, START AND END TOKENs
        for s in a_cppcheck_configuration.scopes:
            if s.type=='Function': 
                # SCAN ALL FUNCTIONS UNLESS LIST OF FUNCTIONS SPECIFIED
                function_dicts[s.Id] = {'name': s.className,
                                        'linenr': s.classStart.linenr,
                                        'tokenStart': s.classStart, 
                                        'tokenEnd': s.classEnd, 
                                        'scopeObject': s,
                                        'symbol_table': {},
                                        'function_graph_edges': [],
                                        'function': s.function}
                # CONSTRUCT LIST OF ROOT TOKENS
                function_dicts[s.Id]['root_tokens'] = self.find_root_tokens(s.classStart, s.classEnd)
                    
        #print "Found %d functions..." % len(function_dicts)
        
        return function_dicts


    def find_root_tokens(self, tokenStart, tokenEnd):
        ''' FOR A FUNCTION DEFINED AS ALL TOKENS FROM tokenStart TO tokenEnd, FIND THE ROOTS.
            input: tokenStart, a CPPCheckData Token, first token in a function
            input: tokenEnd, a CPPCheckData Token, last token in a function
            output: a list of root_tokens, in flow order
            '''
        root_tokens_set = set()

        current_token = tokenStart
        while(current_token != tokenEnd):  #TODO: reverse token set exploration to top-down instead of bottom-up
            # HAS A PARENT
            if current_token.astParent: 
                a_parent = current_token.astParent
                has_parent = True
                while has_parent:
                    # HAS NO PARENT, THEREFORE IS ROOT
                    if not a_parent.astParent:     
                        root_tokens_set.add(a_parent)
                        a_parent.isRoot = True  
                        has_parent = False
                    else:
                        a_parent = a_parent.astParent 
            current_token = current_token.next

        
        root_tokens = list(root_tokens_set)
        # SORT NUMERICALLY BY LINE NUMBER
        root_tokens = sorted(root_tokens, key=lambda x : int(x.linenr))

        return root_tokens


    def build_function_graph(self, analysis_dict):
        ''' BUILDS DIRECTED FUNCTION GRAPH.
            input:  a dictionary of functions from this dump file
            output: none 
            side effect: creates a graph linked to this object
            '''
        # BUILD CALL GRAPH
        self.function_graph = nx.DiGraph()
        G = self.function_graph

        for k, function_dict in analysis_dict.iteritems():
            if function_dict['function']:
                node = function_dict['function'].Id
                G.add_node(node)
                all_attr = nx.get_node_attributes(G, 'function_id')
                all_attr[node] = k
                nx.set_node_attributes(G, 'function_id', all_attr)
                self.add_edges_to_function_graph(function_dict, G, node)

        self.function_graph = G


    def add_edges_to_function_graph(self, function_dict, G, current_node):
        current_token = function_dict['tokenStart']
        end_token = function_dict['tokenEnd']

        # TERMINATION GUARENTEED IF DUMP FILE IS WELL FORMED
        while current_token is not end_token: 
            # ON FIRST LOOP, SKIP SELF-REFERENCE
            current_token = current_token.next  
            if current_token.function:
                if not G.has_edge(current_node, current_token.function.Id):
                    G.add_edge(current_node, current_token.function.Id)
                    function_dict['function_graph_edges'].append(current_token.function)


    def make_sorted_analysis_dict_from_function_graph(self, analysis_dict):
        ''' BUILDS A TOPO SORTED FUNCTION GRAPH. 
            THIS ALLOWS THE ANALYSIS TO START ON FUNCTION LEAFS, SO WE CAN HOPEFULLY DISCOVER TYPES OF THE RETURN VALUE.  
            THE FUNCTION GRAPH MAY HAVE CYCLES (recursion, for example), THEREFORE WE REMOVE THESE EDGES FROM THE GRAPH
            AND ANALYZE THEM LAST (<-- not sure this is best)
            input: a dictionary of functions from this dump file
            output: OrderedDict of functions
            postcondition: returned dict must be the same length as the input dict, and contain all the same elements
            '''
        return_dict = OrderedDict()
        G = self.function_graph 

        # TRY FINDING A DAG.  IF NOT, REMOVE EDGES AND TRY AGAIN. 
        super_break = 0
        while nx.number_of_nodes(G) > 0 and super_break < 1000:
            super_break +=1 
            if not nx.is_directed_acyclic_graph(G):
                try:
                    # SEARCH FOR CYCLE AND REMOVE EDGES
                    edges = nx.find_cycle(G)
                    G.remove_edges_from(edges)
                    print 'Function graph has cycle %s' % edges,
                except:
                    print 'Function graph is not a DAG and does not have a cycle!'
                    # GIVE UP AND RETURN UNSORTED 
                    return analysis_dict
            else:
                # WE HAVE A DIGRAPH, CAN PROCEED ( and topo sort )
                break
        
        if nx.number_of_nodes(G) == 0:
            # RETURN UNCHANGED
            return analysis_dict

        # WE HAVE A DIRECTED GRAPH WITH NODES, CAN SORT AND ADD NODES TO ORDERED LIST
        function_graph_topo_sort = nx.topological_sort(G)
        function_graph_topo_sort_reversed = function_graph_topo_sort[::-1]

        # CREATE RETURN DICT FROM TOPO SORT
        for node in function_graph_topo_sort_reversed:
            function_id_attr_dict = nx.get_node_attributes(G, 'function_id')
            if node in function_id_attr_dict:
                # ADD FUNCTION TO NEW DICTIONARY - THIS IS THE EXPLORE ORDER
                return_dict[function_id_attr_dict[node]] = analysis_dict[function_id_attr_dict[node]]
        
        # ADD ANY REMAINING FUNCTIONS NOT IN THE TOPO SORT TO THE ORDERED DICT
        for k in analysis_dict.keys():
            if k not in return_dict:
                return_dict[k] = analysis_dict[k]

        assert (len(return_dict) == len(analysis_dict))

        return return_dict


    def debug_print_function_graph(self, analysis_dict):
        if not analysis_dict:
            return
        for function_dict in analysis_dict.values():
            print "%s :" % function_dict['name']
            for edge in function_dict['function_graph_edges']:
                print ' --> %s' % edge.name
            

###############
# DEBUG
###############

    def print_debug_output(self):
        #self.print_variable_frames_keys()
        #self.print_transform_variable_frames()
        pass


    def print_variable_frames_keys(self):
        for c in self.configurations:
            for v in c.variables:
                if v.nameToken and v.frames:
                    print "%s: %s\n" % (v.nameToken.str, v.frames.keys())


    def print_transform_variable_frames(self):
        for c in self.configurations:
            for v in c.variables:
                if v.isTransform:
                    print "%s: %s\n" % (v.Id, v.frames,)


    
    
