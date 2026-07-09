"""DocumentRenderer port — renders a template to a document (docx/pdf) for doc_generate."""
from collections.abc import Mapping
from typing import Protocol

from domain.enums import DocumentTemplate
from domain.values import RenderedDocument


class DocumentRenderer(Protocol):
    def render(
        self, template: DocumentTemplate, fields: Mapping[str, object]
    ) -> RenderedDocument: ...
