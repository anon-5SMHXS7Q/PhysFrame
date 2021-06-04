from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser

conn = None

def read_db_config(filename='config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)
 
    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
 
    return db
 
def connect():
    """ Connect to MySQL database """
    global conn

    db_config = read_db_config()
    conn = None
    try:
        print('Connecting to MySQL database...')
        conn = MySQLConnection(**db_config)
 
        if conn.is_connected():
            print('Connection established.')
            return conn
        else:
            print('Connection failed.')
 
    except Error as error:
        print(error)
        if conn is not None and conn.is_connected():
          conn.close()
          print('Connection closed.')
 
def disconnect():
  if conn is not None and conn.is_connected():
    conn.close()
    print('Connection closed.')