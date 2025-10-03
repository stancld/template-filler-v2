"""Data load processing utilities."""

from __future__ import annotations

import csv
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


def read_csv(path: str | os.PathLike) -> Iterator[dict[str, str]]:
    """Read a CSV file and iterate over individual rows."""
    with open(path) as f:
        reader = csv.reader(f)
        # Get header row but skip the first column (label column)
        header = next(reader)[1:]
        # Skip the first row after header (contains verbose placeholder names)
        next(reader)
        for line in reader:
            # Skip the first column (label column) in each data row
            yield dict(zip(header, line[1:]))


def read_excel(path: str | os.PathLike) -> Iterator[dict[str, str]]:
    """Read an Excel file and iterate over individual rows."""
    import openpyxl  # noqa: PLC0415 (Import openpyxl only when needed (lazy loading))

    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook.active
    if worksheet is None:
        raise ValueError("Excel file contains no active worksheet")

    rows = worksheet.iter_rows(values_only=True)

    # Get header row but skip the first column (label column)
    header = [str(col) for col in next(rows)[1:]]
    # Skip the first row after header (contains verbose placeholder names)
    next(rows)
    for row in rows:
        # Skip the first column (label column) in each data row
        # Convert any non-string values to strings
        data_row = [str(cell) if cell is not None else "" for cell in row[1:]]
        yield dict(zip(header, data_row))


def read_data_file(path: str | os.PathLike) -> Iterator[dict[str, str]]:
    """Read a data file (CSV or Excel) and iterate over individual rows.

    Supports .csv, .xlsx, and .xls file formats.
    """
    # Get file extension
    file_ext = os.path.splitext(path)[1].lower()
    if file_ext == ".csv":
        yield from read_csv(path)
    elif file_ext in (".xlsx", ".xls"):
        yield from read_excel(path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Please use .csv, .xlsx, or .xls files.")


def next_without_first_column(iterator: Iterator[list[str]]) -> list[str]:
    """Return next values from the iterator and drop the first column."""
    return next(iterator)[1:]
