#!/usr/bin/env python

#Copyright (c) 2016, University of Nebraska NIMBUS LAB  John-Paul Ore jore@cse.unl.edu
#Copyright 2018 Purdue University, University of Nebraska--Lincoln.
#Copyright 2021 Purdue University, University of Virginia.
#All rights reserved.


from type_analyzer import TypeAnalyzer
import click
import os
from distutils import spawn
from subprocess import Popen, PIPE
import sys
from time import gmtime, strftime, mktime


# IF INSTALLED GLOBALLY, SET VALUE TO 'cppcheck'
CPPCHECK_EXECUTABLE = '/cppcheck-1.80/cppcheck'

@click.command()
@click.argument('target')
@click.option('--annotation_file', default='', help='type annotations file')
def main(target, annotation_file):

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # TEST FOR CPPCHECK
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    if not os.path.exists(CPPCHECK_EXECUTABLE):
        if not spawn.find_executable('cppcheck'):
            print('Could not find required program cppcheck') 
            sys.exit(1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # RUN CPPCHECK
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    if not os.path.exists(target):
        print( 'target does not exist: %s' % target)
        sys.exit(1) 

    if annotation_file and not os.path.exists(annotation_file):
        print( 'annotation file does not exist: %s' % annotation_file)
        sys.exit(1)

    print( 'Processing %s' % target)
    print( 'Attempting to run cppcheck...')

    FORCE_CPPCHECK = False

    original_directory = os.getcwd()
    target_dir = target if os.path.isdir(target) else os.path.dirname(target)
    print( 'Changing directory to %s' % target_dir)
    os.chdir(target_dir)

    dump_filename = 'dump_1_80.temp' if os.path.isdir(target) else os.path.basename(target) + '.dump'

    if FORCE_CPPCHECK or not os.path.exists(dump_filename):

        #dirlist = get_include_dirlist(target_dir)
        #dirlist = get_sub_dirlist(target_dir)
        dirlist = get_header_dirlist(target_dir)

    	include_str = ''
    	for d in dirlist:
            include_str += ' -I ' + d
   
    	args = [CPPCHECK_EXECUTABLE, '--dump', include_str, target]
    	print( "Running cppcheck command: %s" % ' '.join(args))
    	cppcheck_process = Popen(' '.join(args),  shell=True, stdout=PIPE, stderr=PIPE)
    	out, err = cppcheck_process.communicate()
        print out
    	if cppcheck_process.returncode != 0 and \
                not out.startswith('cppcheck: error: could not find or open any of the paths given'):
            print( 'cppcheck appears to have failed..exiting with return code %d' % cppcheck_process.returncode)
            sys.exit(1)
    	open(dump_filename, 'a').close()
    	print( "Created cppcheck 'dump' file %s" % dump_filename)

    os.chdir(original_directory)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # RUN FRAME INCONSISTENCY CHECK
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    t_start = gmtime()
    print("Checking Frame Conventions... %s " % strftime("%Y-%m-%d %H:%M:%S", t_start))

    try:
    
        ty_analyzer = TypeAnalyzer()

        # LOAD TYPE ANNOTATIONS IF ANY
        if annotation_file:
            ty_analyzer.load_type_annotations(annotation_file)

        # RUN TYPE ANNOTATOR
        ty_analyzer.run_collect_all(target)

        # RUN TYPE CHECKER
        ty_analyzer.find_type_errors(target)

    except Exception,e:
        print "EXCEPTION: %s" % (str(e),)
        #raise

    t_end = gmtime()
    print("ENDING... %s (%s sec) " % (strftime("%Y-%m-%d %H:%M:%S", t_end), mktime(t_end)-mktime(t_start)))


def get_include_dirlist(topdir):
    dirlist = []
    for root, dirs, files in os.walk(topdir):
        for d in dirs:
            if d == "include":
                dirlist.append(root + '/' + d)
    return dirlist


def get_header_dirlist_alt(topdir):
    dirlist = []

    for root, dirs, files in os.walk(topdir):
        found_header = False
        for f in files:
            if any(f.endswith(s) for s in ['.h', '.hpp', '.hh']):
                found_header = True
                break

        if found_header or dirs:
            dirlist.append(root)

    return dirlist


def get_header_dirlist(topdir):
    dirset = set()
    templist = []

    for root, dirs, files in os.walk(topdir):
        for f in files:
            if any(f.endswith(s) for s in ['.h', '.hpp', '.hh']):
                templist.append(root)
                break

    rootp = topdir.rstrip('/')

    for d in templist:
        dirset.add(d)

        c = d
        while (c != rootp):
            p = os.path.abspath(os.path.join(c, os.pardir))
            dirset.add(p)
            c = p

    dirset.add(rootp)

    return list(dirset)


def get_sub_dirlist(topdir):
    dirlist = []
    for root, dirs, files in os.walk(topdir):
        dirlist.append(root)
    return dirlist
            


if __name__ == "__main__":
    main()




