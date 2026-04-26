import io
import fitz  # PyMuPDF
from docx import Document

class DocumentParser:
    @staticmethod
    def parse_pdf(file_bytes: bytes) -> str:
        text = ""
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text += page.get_text() + "\n"
        except Exception as e:
            text = f"Error parsing PDF: {e}"
        return text

    @staticmethod
    def parse_docx(file_bytes: bytes) -> str:
        text = ""
        try:
            doc = Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            text = f"Error parsing DOCX: {e}"
        return text

    @staticmethod
    def parse_txt(file_bytes: bytes) -> str:
        try:
            return file_bytes.decode("utf-8")
        except Exception as e:
            return f"Error parsing TXT: {e}"

    @classmethod
    def parse_document(cls, file_bytes: bytes, filename: str) -> str:
        ext = filename.split('.')[-1].lower()
        if ext == 'pdf':
            return cls.parse_pdf(file_bytes)
        elif ext in ['docx', 'doc']:
            return cls.parse_docx(file_bytes)
        elif ext == 'txt':
            return cls.parse_txt(file_bytes)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
