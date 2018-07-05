#!/usr/bin/env python3
"""Script to create data manager jsons"""

import argparse
import json
from pathlib import Path

import yaml


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--value', type=str, help='value')
    parser.add_argument('--dbkey', type=str, help='dbkey')
    parser.add_argument('--name', type=str, help='name')
    parser.add_argument('--path', type=Path, help='path',
                        required=True)
    parser.add_argument('--data_table_name', action='store', type=str,
                        help='Name of the data table',
                        required=True)
    parser.add_argument('--json_output_file', action='store', type=Path,
                        help='Json output file',
                        required=True)
    parser.add_argument("--extra-columns", type=str,
                        help='Yaml formatted string with extra columns '
                             'and their values. For example '
                             '\'{"with-gtf":"0"}\' for STAR indexes')
    return parser


def check_tab(name: str, value: str):
    if '\t' in value:
        raise ValueError(
            '\'{0}\' is not a valid \'{1}\'. It may not contain a tab because '
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
                 extra_columns: dict = None
                 ):
        self.index_path = index_path
        self.data_table_name = data_table_name
        self.name = name if name else str(self.index_path.with_suffix(
            '').name)
        self.value = value if value else self.name
        self.dbkey = dbkey if dbkey else self.value
        self.extra_columns = extra_columns if extra_columns is not None else {}
        self.indexes_properties_file = indexes_properties_file

        self.check_params()

        self.index_properties = self.get_index_properties()

        self.check_index_file_presence()

    def check_params(self):

        check_tab('name', self.name)
        check_tab('index_path', str(self.index_path.absolute().name))
        check_tab('value', self.value)
        check_tab('dbkey', self.dbkey)
        self.check_extra_columns()

    def check_extra_columns(self):
        index_properties = self.get_index_properties()
        index_extra_columns = set(index_properties.get("extra_columns", []))
        given_extra_columns = self.extra_columns.keys()
        if index_extra_columns != given_extra_columns:
            if len(index_extra_columns) > 0:
                raise ValueError(
                    "Values for the following columns should be "
                    "supplied: {0}.".format(
                        str(index_extra_columns).strip("{}")))
            if len(index_extra_columns) == 0:
                raise ValueError(
                    "The table \'{0}\' does not have extra columns".format(
                        self.data_table_name))
        for key, value in self.extra_columns.items():
            check_tab(key, value)

    def get_index_properties(self) -> dict:
        with self.indexes_properties_file.open('r') as properties_file:
            indexes = yaml.safe_load(properties_file)
        index_properties = indexes.get(self.data_table_name)
        if index_properties is None:
            raise ValueError(
                "\'{0}\' not a supported table name".format(
                    self.data_table_name))
        return index_properties

    def check_index_file_presence(self):
        index_name = self.index_properties.get(
            'name',
            '[Index name not found. Please report to developers]')
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
                prefix = str(self.index_path.with_suffix("").name)
            else:
                prefix = str(self.index_path.name)
            for extension in index_extensions:
                if not prefix_plus_extension_exists(self.index_path.parent,
                                                    prefix, extension):
                    raise FileNotFoundError(
                        'Unable to find files with prefix \'{0}\' '
                        'and extension \'{1}\' in {2}. Is this a valid {3}?'
                        .format(
                            prefix,
                            extension,
                            str(self.index_path.parent),
                            index_name))
        elif self.index_properties.get('folder') is not None:
            for file in self.index_properties.get('folder'):
                if not (self.index_path / Path(file)).exists():
                    raise FileNotFoundError(
                        "A file named \'{0}\' was not found in \'{1}\'".format(
                            file, str(self.index_path)))
        else:
            if not self.index_path.exists():
                raise FileNotFoundError(
                    'Unable to find path {0}.'.format(self.index_path))

    @property
    def data_manager_dict(self) -> dict:
        data_table_entry = dict(value=self.value, dbkey=self.dbkey,
                                name=self.name,
                                path=str(self.index_path),
                                **self.extra_columns)
        data_manager_dict = dict(data_tables=dict())
        data_manager_dict["data_tables"][
            self.data_table_name] = [data_table_entry]
        return data_manager_dict

    @property
    def data_manager_json(self) -> str:
        return json.dumps(self.data_manager_dict)


def main():
    options = argument_parser().parse_args()

    if options.json_output_file.exists():
        pass  # Do not raise error.

    if options.extra_columns is None:
        extra_columns = dict()
    else:
        try:
            extra_columns = yaml.safe_load(options.extra_columns)
        except yaml.parser.ParserError as e:
            raise yaml.parser.ParserError(
                "Invalid yaml string for --extra_indexes. \nError {0}".format(
                    e))

    index_properties_file = Path(__file__).parent / Path("indexes.yml")
    data_table = DataTable(index_path=options.path,
                           data_table_name=options.data_table_name,
                           name=options.name,
                           value=options.value,
                           dbkey=options.dbkey,
                           indexes_properties_file=index_properties_file,
                           extra_columns=extra_columns)

    # save info to json file
    with options.json_output_file.open('w') as output_file:
        output_file.write(data_table.data_manager_json)


if __name__ == "__main__":
    main()
