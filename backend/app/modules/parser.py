import io
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document

class DocumentParser:
    SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt"}

    @staticmethod
    def _normalize_text(text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line).strip()

    @staticmethod
    def parse_pdf(file_bytes: bytes) -> str:
        try:
            text_chunks = []
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    text_chunks.append(page.get_text())
        except Exception as exc:
            raise ValueError(f"Unable to parse PDF: {exc}") from exc

        return DocumentParser._normalize_text("\n".join(text_chunks))

    @staticmethod
    def parse_docx(file_bytes: bytes) -> str:
        try:
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join(para.text for para in doc.paragraphs if para.text)
        except Exception as exc:
            raise ValueError(f"Unable to parse DOCX: {exc}") from exc

        return DocumentParser._normalize_text(text)

    @staticmethod
    def parse_txt(file_bytes: bytes) -> str:
        try:
            text = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin-1", errors="ignore")
        return DocumentParser._normalize_text(text)

    @classmethod
    def parse_document(cls, file_bytes: bytes, filename: str) -> str:
        ext = Path(filename or "").suffix.lower().replace(".", "")
        if not ext:
            raise ValueError("The uploaded file does not have a valid extension.")

        if ext == "pdf":
            return cls.parse_pdf(file_bytes)
        if ext == "docx":
            return cls.parse_docx(file_bytes)
        if ext == "txt":
            return cls.parse_txt(file_bytes)
        if ext == "doc":
            raise ValueError("Legacy .doc files are not supported. Please upload .docx.")

        raise ValueError(f"Unsupported file extension: {ext}. Supported: pdf, docx, txt.")
