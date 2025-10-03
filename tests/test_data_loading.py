# Copyright Daniel Stancl.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING

import openpyxl
import pytest

from template_filler.data_loading import next_without_first_column, read_csv, read_data_file

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.mark.unit
def test_next_without_first_column(boring_iterator: Iterator[list[str]]) -> None:
    assert next_without_first_column(boring_iterator) == ["v1", "v2", "v3"]
    assert next_without_first_column(boring_iterator) == ["Name", "City", "Agreement Price"]
    assert next_without_first_column(boring_iterator) == ["Mr Adel", "Prague", "200.000"]


@pytest.mark.unit
def test_read_csv(boring_csv: str, boring_iterator: Iterator[list[str]]) -> None:
    header = next(iter(boring_iterator))[1:]
    _ = next(iter(boring_iterator))
    data = next(iter(boring_iterator))[1:]
    assert list(read_csv(boring_csv)) == [dict(zip(header, data))]


@pytest.mark.unit
def test_read_data_file_csv() -> None:
    """Test reading data from a CSV file."""
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write("label,col1,col2\n")
        f.write("verbose1,verbose2,verbose3\n")
        f.write("r1c1,r1c2,r1c3\n")
        f.write("r2c1,r2c2,r2c3\n")
        csv_path = f.name

    try:
        data = list(read_data_file(csv_path))
        assert len(data) == 2
        assert data[0] == {"col1": "r1c2", "col2": "r1c3"}
        assert data[1] == {"col1": "r2c2", "col2": "r2c3"}
    finally:
        os.unlink(csv_path)


@pytest.mark.unit
def test_read_data_file_xlsx() -> None:
    """Test reading data from an Excel file."""
    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    # Add header and data rows
    worksheet.append(["label", "col1", "col2"])
    worksheet.append(["verbose1", "verbose2", "verbose3"])
    worksheet.append(["r1c1", "r1c2", "r1c3"])
    worksheet.append(["r2c1", "r2c2", "r2c3"])

    # Save the workbook to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        xlsx_path = f.name

    workbook.save(xlsx_path)

    try:
        data = list(read_data_file(xlsx_path))
        assert len(data) == 2
        assert data[0] == {"col1": "r1c2", "col2": "r1c3"}
        assert data[1] == {"col1": "r2c2", "col2": "r2c3"}
    finally:
        os.unlink(xlsx_path)


@pytest.mark.unit
def test_read_data_file_unsupported_format() -> None:
    """Test error is raised for unsupported file formats."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("Some text\n")
        txt_path = f.name

    try:
        with pytest.raises(ValueError, match="Unsupported file format"):
            list(read_data_file(txt_path))
    finally:
        os.unlink(txt_path)


@pytest.mark.unit
def test_read_data_file_non_string_values() -> None:
    """Test handling of non-string values in Excel files."""
    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    # Add header and data rows
    worksheet.append(["label", "text", "number", "none"])
    worksheet.append(["verbose1", "verbose2", "verbose3", "verbose4"])
    worksheet.append(["r1c1", "text value", 123, None])

    # Save the workbook to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        xlsx_path = f.name

    workbook.save(xlsx_path)

    try:
        data = list(read_data_file(xlsx_path))
        assert len(data) == 1
        assert data[0] == {"text": "text value", "number": "123", "none": ""}
        # Verify that numeric value was converted to string and None to empty string
    finally:
        os.unlink(xlsx_path)
