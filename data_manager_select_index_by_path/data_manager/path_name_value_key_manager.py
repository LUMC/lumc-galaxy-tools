#!/usr/bin/env python3

import json
import argparse
import os
import yaml

def argument_parser():

    #value = "test_value"
    #name = "test_name"
    #print '{0} other {1} more{0}'.format(value, name )
    #print '{0} is not a valid {1}. It may not contain a tab.'.format( value, name )

    #Parse Command Line
    parser = argparse.ArgumentParser()
    parser.add_argument( '--value', action='store', type=str, default=None, help='value' )
    parser.add_argument( '--dbkey', action='store', type=str, default=None, help='dbkey' )
    parser.add_argument( '--name',  action='store', type=str, default=None, help='name' )
    parser.add_argument( '--path', action='store', type=str, default=None, help='path',required=True )
    parser.add_argument( '--data_table_name', action='store', type=str, default=None, help='path',required=True )
    parser.add_argument( '--json_output_file', action='store', type=str, default=None, help='path', required=True )
    return parser

class DataTable:
    def __init__(self,
                 index_path,
                 data_table_name,
                 name=None,
                 dbkey=None,
                 value=None,
                 ):
        self.index_path = index_path
        self.data_table_name = data_table_name
        self.name = name if name else os.path.splitext(os.path.basename(index_path))[0]
        self.value = value if value else self.name
        self.dbkey = dbkey if dbkey else self.value

        self.check_params()


    def check_params(self):
        def check_tab(name, value):
            if '\t' in value:
                raise ValueError(
                    '{0} is not a valid {1}. It may not contain a tab because these are used as seperators by galaxy .'.format(value, name))

        check_tab('name', self.name)
        check_tab('index_path',self.index_path)
        check_tab('value',self.value)
        check_tab('dbkey',self.dbkey)

def _add_data_table_entry( data_manager_dict, data_table_name, data_table_entry ):
    data_manager_dict['data_tables'] = data_manager_dict.get( 'data_tables', {} )
    data_manager_dict['data_tables'][ data_table_name ] = data_manager_dict['data_tables'].get( data_table_name, [] )
    data_manager_dict['data_tables'][ data_table_name ].append( data_table_entry )
    return data_manager_dict


def prefix_exists(directory, prefix):
    '''checks if files exist with prefix in a directory. Returns Boolean'''
    matched_files = []
    directory_files = os.listdir(directory)
    for directory_file in directory_files:
        if directory_file.startswith(prefix):
            matched_files.append(directory_file)
    # Empty list should return False
    return bool(matched_files)

def prefix_plus_extension_exists(directory, prefix, extension):
    '''checks if files exist with prefix in a directory. Returns Boolean'''
    matched_files = []
    directory_files = os.listdir(directory)
    for directory_file in directory_files:
        if directory_file.startswith(prefix) and directory_file.endswith(extension):
            matched_files.append(directory_file)
    # Empty list should return False
    return bool(matched_files)

def main():
    options = argument_parser().parse_args()

    data_table = DataTable(index_path= options.path,
                           data_table_name = options.data_table_name,
                           name= options.name,
                           value= options.value,
                           dbkey= options.dbkey
                           )
    json_output_file =  options.json_output_file

    # Check if file or prefix exists
    indexes = yaml.load(file(os.path.join(os.path.dirname(__file__), 'indexes.yml')))
    index_dict = indexes.get(data_table_name,{})
    index_name = index_dict.get('name','index')
    index_extensions = index_dict.get('extensions', [''])
    no_prefix = index_dict.get('no_prefix', False)
    if not no_prefix:
        dirname = os.path.dirname(path)
        prefix = basename
        for extension in index_extensions:
            if not prefix_plus_extension_exists(dirname,prefix,extension):
                raise Exception( 'Unable to find files with prefix "{0}" and extension "{1}" in {2}. Is this a valid {3}?'.format( prefix, extension, dirname, index_name ) )
    else:
        if not os.path.exists(path):
            raise Exception( 'Unable to find path {0}.'.format( path ) )

    if os.path.exists(json_output_file):
        params = json.loads( open( json_output_file ).read() )
        print("params", params)
    else:
        params = {}

    data_manager_dict = {}
    data_table_entry = dict( value=value, dbkey=dbkey, name=name, path=path )
    _add_data_table_entry( data_manager_dict, data_table_name, data_table_entry )

    #save info to json file
    with open( json_output_file, 'wb' ) as output_file:
        output_file.write( json.dumps( data_manager_dict ) )
        output_file.write( "\n" )

if __name__ == "__main__":
    main()
