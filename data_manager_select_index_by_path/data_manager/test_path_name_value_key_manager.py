#!/usr/bin/env python3

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

from path_name_value_key_manager import DataTable, check_tab, main

TEST_OUTPUT_DIR = tempfile.mkdtemp(".d",
                                   "tmp_data_manager_select_index_by_path")

indexes_yml = Path(__file__).parent / Path("indexes.yml")
test_data = Path(__file__).parent.parent / Path("test-data")


@pytest.fixture
def temp_json_path():
    with tempfile.NamedTemporaryFile(suffix=".json", dir =TEST_OUTPUT_DIR) as tmp:
        path = tmp.name
        # [1] Needed. mkstemp returns a tuple.
        # The second value is the absolute path
    yield path
    os.remove(path)

def test_application():
    for output_path in temp_json_path():
        index_path = test_data / Path("fasta_indexes/EboVir3.fa")
        sys.argv = ['',
                    "--path", str(index_path),
                    "--data_table_name", "fasta_indexes",
                    "--json_output_file", str(output_path)
                    ]
        main()
        data_manager_dict = \
            json.load(Path(output_path).open())["data_tables"]['fasta_indexes'][0]
        assert (data_manager_dict['path'] == str(index_path))
        assert (data_manager_dict['name'] == "EboVir3")
        assert (data_manager_dict['value'] == "EboVir3")
        assert (data_manager_dict['dbkey'] == "EboVir3")


def test_application_overwrite_file():
    for output_path in temp_json_path():
        Path(output_path).write_text("bla invalid json")
        index_path = test_data / Path("fasta_indexes/EboVir3.fa")
        sys.argv = ['',
                    "--path", str(index_path),
                    "--data_table_name", "fasta_indexes",
                    "--json_output_file", str(output_path)
                    ]
        main()
        data_manager_dict = \
            json.load(Path(output_path).open())["data_tables"]['fasta_indexes'][0]
        assert (data_manager_dict['path'] == str(index_path))
        assert (data_manager_dict['name'] == "EboVir3")
        assert (data_manager_dict['value'] == "EboVir3")
        assert (data_manager_dict['dbkey'] == "EboVir3")


def test_application_star_index():
    for output_path in temp_json_path():
        index_path = test_data / Path("star_index")
        sys.argv = ['',
                    "--path", str(index_path),
                    "--data_table_name", "rnastar_index2",
                    "--name", "Ebola virus Sierra Leone 2014",
                    "--dbkey", "G3683/KM034562.1/eboVir3",
                    "--value", "KM034562.1",
                    "--json_output_file", str(output_path),
                    "--extra-columns", "{with-gtf: '0'}"
                    ]
        main()
        data_manager_dict = json.load(Path(output_path).open())
        table = data_manager_dict["data_tables"]["rnastar_index2"][0]
        assert (table['path'] == str(index_path))
        assert (table['name'] == "Ebola virus Sierra Leone 2014")
        assert (table['value'] == "KM034562.1")
        assert (table['dbkey'] == "G3683/KM034562.1/eboVir3")
        assert (table['with-gtf'] == '0')


def test_application_star_index_fail_wrong_yaml():
    with pytest.raises(yaml.parser.ParserError):
        for output_path in temp_json_path():
            index_path = test_data / Path("star_index")
            sys.argv = ['',
                        "--path", str(index_path),
                        "--data_table_name", "rnastar_index2",
                        "--name", "Ebola virus Sierra Leone 2014",
                        "--dbkey", "G3683/KM034562.1/eboVir3",
                        "--value", "KM034562.1",
                        "--json_output_file", str(output_path),
                        "--extra-columns", "{with-gtf: '0'{[]{x"
                        ]
            main()


def test_check_tab():
    check_tab("test", "This text does not contain a tab and succeeds")


def test_check_tab_fail():
    with pytest.raises(ValueError,
                       match="\'This text does contain a "
                             "\t and fails\' is not a valid \'test\'"):
        check_tab("test", "This text does contain a \t and fails")


def data_table_test(index_path: Path,
                    data_table_name: str):
    dt = DataTable(index_path=index_path,
                   data_table_name=data_table_name,
                   indexes_properties_file=indexes_yml)
    data_manager_dict = dt.data_manager_dict
    assert (data_manager_dict["data_tables"].get(data_table_name) is not None)
    assert (data_manager_dict["data_tables"].get(data_table_name)[0].get(
        "path") == str(
        index_path))


def test_data_table():
    dt = DataTable(index_path=test_data / "bwa_mem_index/EboVir3.fa",
                   data_table_name="bwa_mem_indexes",
                   indexes_properties_file=indexes_yml)
    assert (dt.name == "EboVir3")
    assert (dt.value == "EboVir3")
    assert (dt.dbkey == "EboVir3")
    dm_json = json.loads(dt.data_manager_json)
    print(dm_json)
    assert (dm_json == {"data_tables": {"bwa_mem_indexes": [
        {"name": "EboVir3",
         "value": "EboVir3",
         "dbkey": "EboVir3",
         "path": str((
                 test_data / "bwa_mem_index/EboVir3.fa"))}]}})


def test_non_existing_table():
    with pytest.raises(ValueError,
                       match="\'bla_indexes\' not a supported table name"):
        data_table_test(test_data / "bwa_mem_index/EboVir3.fa",
                        data_table_name="bla_indexes")


def test_rnastar_index_fail_no_extra_column():
    with pytest.raises(ValueError,
                       match="Values for the following columns "
                             "should be supplied: 'with-gtf'."):
        data_table_test(
            index_path=test_data / "star_index",
            data_table_name="rnastar_index2")


def test_rnastar_index_fail_wrong_dir():
    with pytest.raises(FileNotFoundError):
        DataTable(
            index_path=test_data / "picard_index",
            data_table_name="rnastar_index2",
            extra_columns={'with-gtf': '0'},
            indexes_properties_file=indexes_yml)


def test_all_fasta_table_fail_extra_columns():
    with pytest.raises(ValueError,
                       match="The table 'all_fasta' "
                             "does not have extra columns"):
        DataTable(
            index_path=test_data / "EboVir3.fa",
            data_table_name="all_fasta",
            extra_columns={'with-gtf': '0'},
            indexes_properties_file=indexes_yml)


def test_all_fasta_table():
    data_table_test(test_data / "EboVir3.fa",
                    data_table_name="all_fasta")


def test_index_path_not_exist():
    with pytest.raises(FileNotFoundError, match="Unable to find path"):
        data_table_test(test_data / "NotExists.fa",
                        data_table_name="all_fasta")


def test_bowtie2_index():
    data_table_test(
        index_path=test_data / "bowtie2_index/EboVir3",
        data_table_name="bowtie2_indexes")


def test_bowtie2_index_fail():
    with pytest.raises(FileNotFoundError,
                       match="Unable to find files "
                             "with prefix \'EboVir3.fa\'"):
        data_table_test(
            index_path=test_data / "bowtie2_index/EboVir3.fa",
            data_table_name="bowtie2_indexes")


def test_bwa_index():
    data_table_test(index_path=test_data / "bwa_mem_index/EboVir3.fa",
                    data_table_name="bwa_mem_indexes")


def test_bowtie_index():
    data_table_test(test_data / "bowtie_index/EboVir3.fa",
                    data_table_name="bowtie_indexes")


def test_bowtie_index_color():
    data_table_test(test_data / "bowtie_index/color/EboVir3.fa",
                    data_table_name="bowtie_indexes_color")


def test_hisat2_index():
    data_table_test(test_data / "hisat2_index/EboVir3",
                    data_table_name="hisat2_indexes")


def test_picard_index():
    data_table_test(test_data / "picard_index/EboVir3.fa",
                    data_table_name="picard_indexes")


def test_sam_index():
    data_table_test(test_data / "fasta_indexes/EboVir3.fa",
                    data_table_name="fasta_indexes")
