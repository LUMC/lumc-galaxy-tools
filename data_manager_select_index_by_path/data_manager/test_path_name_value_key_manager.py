#!/usr/bin/env python3

import pytest
import json
from pathlib import Path

from path_name_value_key_manager import DataTable,check_tab

indexes_yml = Path(__file__).parent / "indexes.yml"
test_data = Path(__file__).parent / "../test-data"

def test_check_tab():
    check_tab("test", "This text does not contain a tab and succeeds")

@pytest.mark.xfail
def test_check_tab_fail():
    check_tab("test","This text does contain a \t and fails")


def data_table_test(index_path: Path,
                    data_table_name: str):
    dt = DataTable(index_path=index_path,
                   data_table_name=data_table_name,
                   indexes_properties_file=indexes_yml)
    data_manager_dict = dt.data_manager_dict
    assert (data_manager_dict.get(data_table_name) is not None)
    assert (data_manager_dict.get(data_table_name).get("path") == str(index_path))


def test_data_table():
    dt = DataTable(index_path=test_data / "bwa_mem_index/EboVir3.fa",
                   data_table_name="bwa_mem_indexes",
                   indexes_properties_file=indexes_yml)
    assert (dt.name == "EboVir3")
    assert (dt.value == "EboVir3")
    assert (dt.dbkey == "EboVir3")
    dm_json = json.loads(dt.data_manager_json)
    print(dm_json)
    assert (dm_json['bwa_mem_indexes'] == {"name": "EboVir3", "value": "EboVir3", "dbkey": "EboVir3",
                                           "path": str((test_data / "bwa_mem_index/EboVir3.fa"))})


@pytest.mark.xfail
def test_non_existing_table():
    data_table_test(test_data / "bwa_mem_index/EboVir3.fa",
                    data_table_name="bla_indexes")

def test_all_fasta_table():
    data_table_test(test_data /"EboVir3.fa",
                    data_table_name="all_fasta")

@pytest.mark.xfail
def test_index_path_not_exist():
    data_table_test(test_data /"NotExists.fa",
                    data_table_name="all_fasta")

def test_bowtie2_index():
    data_table_test(
        index_path=test_data / "bowtie2_index/EboVir3",
        data_table_name="bowtie2_indexes")


@pytest.mark.xfail
def test_bowtie2_index_fail():
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
