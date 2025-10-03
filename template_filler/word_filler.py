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

"""Minimalistic Python app for filling Word templates from excel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from docx import Document

if TYPE_CHECKING:
    import os
    from collections.abc import Mapping

    from docx import Paragraph


def fill_template(template_path: str | os.PathLike, output_path: str | os.PathLike, data: Mapping[str, str]) -> None:
    """Fill Word template with the actual data from CSV file.

    Replaces all placeholders in paragraphs in format {key} with corresponding values from data dictionary.
    """
    template_doc = Document(template_path)

    # Process all placeholders in paragraphs
    _process_paragraphs(template_doc.paragraphs, data)

    template_doc.save(output_path)


def _process_paragraphs(paragraphs: list[Paragraph], data: Mapping[str, str]) -> None:
    """Process all paragraphs to replace placeholders with actual data."""
    for paragraph in paragraphs:
        for key, value in data.items():
            placeholder = "{" + key + "}"
            if placeholder in paragraph.text:
                for run in paragraph.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, str(value))
