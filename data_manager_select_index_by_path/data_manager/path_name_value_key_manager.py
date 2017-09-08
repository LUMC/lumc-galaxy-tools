#!/usr/bin/env python

import json
import argparse
import os.path

def _add_data_table_entry( data_manager_dict, data_table_name, data_table_entry ):
    data_manager_dict['data_tables'] = data_manager_dict.get( 'data_tables', {} )
    data_manager_dict['data_tables'][ data_table_name ] = data_manager_dict['data_tables'].get( data_table_name, [] )
    data_manager_dict['data_tables'][ data_table_name ].append( data_table_entry )
    return data_manager_dict


def check_param(name, value, default=None,  check_tab=True):
    if value in [ None, '', '?' ]:
        if default:
            print "Using {0} for {1} as no value provided".format( default, name )
            value = default
        else:
            raise Exception( '{0} is not a valid {1}. You must specify a valid {1}.'.format( value, name ) )
    if check_tab and "\t" in value:
        raise Exception( '{0} is not a valid {1}. It may not contain a tab because these are used as seperators by galaxy .'.format( value, name ) )
    return value


def main():

    #value = "test_value"
    #name = "test_name"
    #print '{0} other {1} more{0}'.format(value, name )
    #print '{0} is not a valid {1}. It may not contain a tab.'.format( value, name )

    #Parse Command Line
    parser = argparse.ArgumentParser()
    parser.add_argument( '--value', action='store', type=str, default=None, help='value' )
    parser.add_argument( '--dbkey', action='store', type=str, default=None, help='dbkey' )
    parser.add_argument( '--name',  action='store', type=str, default=None, help='name' )
    parser.add_argument( '--path', action='store', type=str, default=None, help='path' )
    parser.add_argument( '--data_table_name', action='store', type=str, default=None, help='path' )
    parser.add_argument( '--json_output_file', action='store', type=str, default=None, help='path' )
    parser.add_argument( '--no_check_path', action='store_true', help='If provided. Only checks whether directory exists, but not if file in directory exists. (Useful for bowtie and other prefix indices.)')
    options = parser.parse_args()

    path = check_param("path", options.path)
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        raise Exception( 'Directory "{0}" does not exist, or no read permission'.format(dirname))
    else:
        if (not options.no_check_path) and (not os.path.exists(path)):
            raise Exception( 'Unable to find path {0}.'.format( path ) )
    basename = os.path.basename(path)
    filename = os.path.splitext(basename)[0]
    name = check_param("name", options.name, default=filename)
    value = check_param("value", options.value, default=name)
    dbkey = check_param("dbkey", options.dbkey, default=value)
    data_table_name = check_param("data_table_name", options.data_table_name)
    json_output_file = check_param("json_output_file", options.json_output_file, check_tab=False)

    if os.path.exists(json_output_file):
        params = json.loads( open( json_output_file ).read() )
        print "params", params
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
