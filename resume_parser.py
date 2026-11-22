
"""Extract text from an uploaded PDF resume."""

from io import BytesIO


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from a text-based PDF."""

    if uploaded_file is None:
        return ""

    pdf_data = uploaded_file.getvalue()

    # First try PyMuPDF
    try:
        import fitz

        document = fitz.open(
            stream=pdf_data,
            filetype="pdf"
        )

        text = "\n".join(
            page.get_text() for page in document
        )

        document.close()

        if text.strip():
            return text.strip()

    except Exception:
        pass

    # Fallback: pypdf
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(pdf_data))

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

        return text.strip()

    except Exception as error:
        raise RuntimeError(
            f"Could not read PDF: {error}"
        )
