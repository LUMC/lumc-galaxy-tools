#!/usr/bin/env python3

import json
import argparse
import os
import yaml

from pathlib import Path

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
    parser.add_argument( '--data_table_name', action='store', type=str, default=None, help='Name of the data table',required=True )
    parser.add_argument( '--json_output_file', action='store', type=Path, default=None, help='Json output file', required=True )
    return parser


def check_tab(name, value):
    if '\t' in value:
        raise ValueError(
            '{0} is not a valid {1}. It may not contain a tab because these are used as seperators by galaxy .'.format(
                value, name))

def prefix_plus_extension_exists(directory, prefix, extension):
    '''checks if files exist with prefix in a directory. Returns Boolean'''
    matched_files = []
    directory_files = os.listdir(directory)
    for directory_file in directory_files:
        if directory_file.startswith(prefix) and directory_file.endswith(extension):
            matched_files.append(directory_file)
    # Empty list should return False
    return bool(matched_files)

class DataTable(object):
    def __init__(self,
                 index_path,
                 data_table_name,
                 indexes_properties_file,
                 name=None,
                 dbkey=None,
                 value=None,
                 ):
        self.index_path = index_path
        self.data_table_name = data_table_name
        self.name = name if name else os.path.splitext(os.path.basename(index_path))[0]
        self.value = value if value else self.name
        self.dbkey = dbkey if dbkey else self.value
        self.indexes_properties_file = indexes_properties_file

        self.check_params()

        self.index_properties = self.get_index_properties()

        self.check_index_file_presence()


    def check_params(self):

        check_tab('name', self.name)
        check_tab('index_path',self.index_path)
        check_tab('value',self.value)
        check_tab('dbkey',self.dbkey)

    def get_index_properties(self):
        with open(self.indexes_properties_file) as properties_file:
            indexes = yaml.load(properties_file)
        index_properties = indexes.get(self.data_table_name)
        if not index_properties:
            raise ValueError("{0} not a supported table name".format(self.data_table_name))
        return index_properties

    def check_index_file_presence(self):
        index_name =  self.index_properties.get('name')
        if not index_name:
            raise ValueError("Property 'name' not defined for '{0}', please contact the developers to correct the mistake.")
        index_extensions = self.index_properties.get('extensions', [''])

        # Sometimes an index path is a prefix.
        # For example, with BWA. 'reference.fa' is the index. But the actual index files are
        # 'reference.fa.amb', 'reference.fa.ann' etc.

        # If the index is not a prefix, the index file is taken to be the path itself.
        index_is_a_prefix = self.index_properties.get('prefix', True)
        if index_is_a_prefix:
            basename = os.path.basename(self.index_path)
            dirname = os.path.dirname(self.index_path)
            prefix = basename
            for extension in index_extensions:
                if not prefix_plus_extension_exists(dirname, prefix, extension):
                    raise FileNotFoundError(
                        'Unable to find files with prefix "{0}" and extension "{1}" in {2}. Is this a valid {3}?'.format(
                            prefix, extension, dirname, index_name))
        else:
            if not os.path.exists(self.index_path):
                raise FileNotFoundError('Unable to find path {0}.'.format(self.index_path))

    def data_manager_json(self):
        data_table_entry = dict(value=self.value, dbkey=self.dbkey, name=self.name, path=self.index_path)
        data_manager_dict= dict()
        data_manager_dict[self.data_table_name] = data_table_entry
        return json.dumps(data_manager_dict)



def main():
    options = argument_parser().parse_args()

    if options.json_output_file.exists():
        raise FileExistsError("'{0}' already exists.".format(str(options.json_output_file)))

    data_table = DataTable(index_path= options.path,
                           data_table_name = options.data_table_name,
                           name= options.name,
                           value= options.value,
                           dbkey= options.dbkey,
                           indexes_properties_file= os.path.join(os.path.dirname(__file__), 'indexes.yml')
                           )

    #save info to json file
    with open( options.json_output_file, 'wb' ) as output_file:
        output_file.write( data_table.data_manager_json())
        output_file.write( "\n" )

if __name__ == "__main__":
    main()
