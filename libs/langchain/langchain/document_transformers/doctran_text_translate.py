from typing import Any, Optional, Sequence

from langchain_core.schema import BaseDocumentTransformer, Document

from langchain.utils import get_from_env


class DoctranTextTranslator(BaseDocumentTransformer):
    """Translate text documents using doctran.

    Arguments:
        openai_api_key: OpenAI API key. Can also be specified via environment variable
        ``OPENAI_API_KEY``.
        language: The language to translate *to*.

    Example:
        .. code-block:: python

        from langchain.document_transformers import DoctranTextTranslator

        # Pass in openai_api_key or set env var OPENAI_API_KEY
        qa_translator = DoctranTextTranslator(language="spanish")
        translated_document = await qa_translator.atransform_documents(documents)
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        language: str = "english",
        openai_api_model: Optional[str] = None,
    ) -> None:
        self.openai_api_key = openai_api_key or get_from_env(
            "openai_api_key", "OPENAI_API_KEY"
        )
        self.openai_api_model = openai_api_model or get_from_env(
            "openai_api_model", "OPENAI_API_MODEL"
        )
        self.language = language

    def transform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> Sequence[Document]:
        raise NotImplementedError

    async def atransform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> Sequence[Document]:
        """Translates text documents using doctran."""
        try:
            from doctran import Doctran

            doctran = Doctran(
                openai_api_key=self.openai_api_key, openai_model=self.openai_api_model
            )
        except ImportError:
            raise ImportError(
                "Install doctran to use this parser. (pip install doctran)"
            )
        doctran_docs = [
            doctran.parse(content=doc.page_content, metadata=doc.metadata)
            for doc in documents
        ]
        for i, doc in enumerate(doctran_docs):
            doctran_docs[i] = await doc.translate(language=self.language).execute()
        return [
            Document(page_content=doc.transformed_content, metadata=doc.metadata)
            for doc in doctran_docs
        ]
