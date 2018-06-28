#!/usr/bin/env python3

import pytest
import json
from pathlib import Path

from path_name_value_key_manager import DataTable,check_tab,prefix_plus_extension_exists


indexes_yml = Path(__file__).parent / "indexes.yml"
test_data = Path(__file__).parent / "../test-data"

def test_bowtie2_index():
    dt = DataTable(
        index_path=test_data / "bowtie2_index/EboVir3",
        data_table_name= "bowtie2_indexes",
        indexes_properties_file= indexes_yml
        )
    data_manager_dict = dt.data_manager_dict
    assert(data_manager_dict.get("bowtie2_indexes") != None)




