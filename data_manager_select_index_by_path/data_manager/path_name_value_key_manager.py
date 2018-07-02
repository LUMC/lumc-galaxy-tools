#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import yaml


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--value', action='store', type=str, help='value')
    parser.add_argument('--dbkey', action='store', type=str, help='dbkey')
    parser.add_argument('--name', action='store', type=str, help='name')
    parser.add_argument('--path', action='store', type=str, help='path',
                        required=True)
    parser.add_argument('--data_table_name', action='store', type=str,
                        help='Name of the data table',
                        required=True)
    parser.add_argument('--json_output_file', action='store', type=Path,
                        help='Json output file',
                        required=True)
    return parser


def check_tab(name: str, value: str):
    if '\t' in value:
        raise ValueError(
            '{0} is not a valid {1}. It may not contain a tab because '
            'these are used as seperators by galaxy .'.format(
                value, name))


def prefix_plus_extension_exists(directory: Path, prefix: str, extension: str):
    """checks if files exist with prefix in a directory. Returns Boolean"""
    matched_files = [directory_file for directory_file in directory.iterdir()
                     if
                     directory_file.name.startswith(
                         prefix) and directory_file.suffix == extension]
    # Empty list should return False
    return bool(matched_files)


class DataTable(object):

    def __init__(self,
                 index_path: Path,
                 data_table_name: str,
                 indexes_properties_file: Path,
                 name: str = None,
                 dbkey: str = None,
                 value: str = None,
                 ):
        self.index_path = index_path
        self.data_table_name = data_table_name
        self.name = name if name else self.index_path.with_suffix(
            '').name.__str__()
        self.value = value if value else self.name
        self.dbkey = dbkey if dbkey else self.value
        self.indexes_properties_file = indexes_properties_file

        self.check_params()

        self.index_properties = self.get_index_properties()

        self.check_index_file_presence()

    def check_params(self):

        check_tab('name', self.name)
        check_tab('index_path', self.index_path.absolute().__str__())
        check_tab('value', self.value)
        check_tab('dbkey', self.dbkey)

    def get_index_properties(self) -> dict:
        with self.indexes_properties_file.open('r') as properties_file:
            indexes = yaml.safe_load(properties_file)
        index_properties = indexes.get(self.data_table_name)
        if not index_properties:
            raise ValueError(
                "{0} not a supported table name".format(self.data_table_name))
        return index_properties

    def check_index_file_presence(self):
        index_name = self.index_properties.get('name')
        if not index_name:
            raise ValueError(
                "Property 'name' not defined for '{0}',"
                " please contact the developers to correct the mistake.")
        index_extensions = self.index_properties.get('extensions', [''])

        # Sometimes an index path is a prefix.
        # For example, with BWA. 'reference.fa' is the index.
        # But the actual index files are
        # 'reference.fa.amb', 'reference.fa.ann' etc.

        # If the index is not a prefix,
        # the index file is taken to be the path itself.
        index_is_a_prefix = self.index_properties.get('prefix', True)
        prefix_strip_extension = self.index_properties.get(
            'prefix_strip_extension', False)
        if index_is_a_prefix:
            if prefix_strip_extension:
                prefix = self.index_path.with_suffix("").name.__str__()
            else:
                prefix = self.index_path.name.__str__()
            for extension in index_extensions:
                if not prefix_plus_extension_exists(self.index_path.parent,
                                                    prefix, extension):
                    raise FileNotFoundError(
                        'Unable to find files with prefix "{0}" '
                        'and extension "{1}" in {2}. Is this a valid {3}?'
                        .format(
                            prefix,
                            extension,
                            self.index_path.parent,
                            index_name))
        else:
            if not self.index_path.exists():
                raise FileNotFoundError(
                    'Unable to find path {0}.'.format(self.index_path))

    @property
    def data_manager_dict(self) -> dict:
        data_table_entry = dict(value=self.value, dbkey=self.dbkey,
                                name=self.name, path=self.index_path.__str__())
        data_manager_dict = dict()
        data_manager_dict[self.data_table_name] = data_table_entry
        return data_manager_dict

    @property
    def data_manager_json(self) -> str:
        return json.dumps(self.data_manager_dict)


def main():
    options = argument_parser().parse_args()

    if options.json_output_file.exists():
        raise FileExistsError(
            "'{0}' already exists.".format(str(options.json_output_file)))

    index_properties_file = Path(__file__).parent / "indexes.yml"
    data_table = DataTable(index_path=options.path,
                           data_table_name=options.data_table_name,
                           name=options.name,
                           value=options.value,
                           dbkey=options.dbkey,
                           indexes_properties_file=index_properties_file)

    # save info to json file
    with open(options.json_output_file, 'w') as output_file:
        output_file.write(data_table.data_manager_json)
        output_file.write("\n")


if __name__ == "__main__":
    main()
