#Copyright 2021 Purdue University, University of Virginia.
#All rights reserved.


import sys
import jinja2

from dbUtil import *

cursor = None

def gen_sig_implications(cursor,table_name,threshold):
    queryDual = f"SELECT first_parent, first_child, second_parent, second_child FROM {table_name} WHERE zScore>={threshold};"

    sig_implications = []

    cursor.execute(queryDual)
    row = cursor.fetchone()
    while row is not None:
        implication = {'first_parent':str(row[0]).replace("'",""),'first_child':str(row[1]).replace("'",""),
                        'second_parent':str(row[2]).replace("'",""),'second_child':str(row[3]).replace("'","")}
        sig_implications.append(implication)
        row = cursor.fetchone()

    return sig_implications

def gen_name_implications(cursor,table_name,threshold):
    query = f"SELECT first_name, second_name FROM {table_name} WHERE z_score>={threshold} AND (first_name<>second_name);"

    name_implications = []

    cursor.execute(query)
    row = cursor.fetchone()
    while row is not None:
        implication = {'first_name':str(row[0]).replace("'",""),'second_name':str(row[1]).replace("'","")}
        name_implications.append(implication)
        row = cursor.fetchone()

    return name_implications

def gen_null_names(cursor,table_name,threshold):
    query = f"SELECT name FROM {table_name} WHERE zScore>={threshold};"

    null_names = []

    cursor.execute(query)
    row = cursor.fetchone()
    while row is not None:
        null_names.append(str(row[0]).replace("'",""))
        row = cursor.fetchone()

    return null_names

def gen_null_sigs(cursor,table_name,threshold):
    query = f"SELECT parent,child FROM {table_name} WHERE zScore>={threshold};"

    null_sigs = []

    cursor.execute(query)
    row = cursor.fetchone()
    while row is not None:
        null_sigs.append({'parent':str(row[0]).replace("'",""),'child':str(row[1]).replace("'","")})
        row = cursor.fetchone()

    return null_sigs

def gen_null_rot_names(cursor,table_name,threshold):
    query = f"SELECT name FROM {table_name} WHERE zScore>={threshold};"

    null_names = []

    cursor.execute(query)
    row = cursor.fetchone()
    while row is not None:
        null_names.append(str(row[0]).replace("'",""))
        row = cursor.fetchone()

    return null_names

def gen_null_rot_sigs(cursor,table_name,threshold):
    query = f"SELECT parent,child FROM {table_name} WHERE zScore>={threshold};"

    null_sigs = []

    cursor.execute(query)
    row = cursor.fetchone()
    while row is not None:
        null_sigs.append({'parent':str(row[0]).replace("'",""),'child':str(row[1]).replace("'","")})
        row = cursor.fetchone()

    return null_sigs

def getTemplate():
    return jinja2.Template(open('./linter_rules.py.jinja','r').read())

if __name__ == '__main__':
    printToFile = False
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        printToFile = True

    threshold = 1.0

    if len(sys.argv) > 2:
        threshold = float(sys.argv[2])
    
    cursor = connect().cursor()

    sig_implications = gen_sig_implications(cursor,"sig_dual_freq3",threshold)
    name_implications = gen_name_implications(cursor,"name_dual_freq_3",threshold)

    null_sigs = gen_null_sigs(cursor,'zero_pairs_scored',threshold)
    null_names = gen_null_names(cursor,'zero_names_scored',threshold)

    null_rot_sigs = gen_null_rot_sigs(cursor,'zeroRotPairsScored_m',threshold)
    null_rot_names = gen_null_rot_names(cursor,'zeroRotNamesScored_m',threshold)

    template = getTemplate()

    if printToFile:
        with open(filename,'w') as out:
            out.write(template.render(
                {
                    'sig_implications':sig_implications,
                    'name_implications':name_implications,
                    'null_sigs':null_sigs,
                    'null_names':null_names,
                    'null_rot_sigs':null_rot_sigs,
                    'null_rot_names':null_rot_names}))
    else:
        print(template.render(
            {
                'sig_implications':sig_implications,
                'name_implications':name_implications,
                'null_sigs':null_sigs,
                'null_names':null_names,
                'null_rot_sigs':null_rot_sigs,
                'null_rot_names':null_rot_names}))
