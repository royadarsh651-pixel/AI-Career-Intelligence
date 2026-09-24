from pypdf import PdfReader


def extract_text_from_pdf(file_path):
    """Extract text from all pages of a PDF file."""

    reader = PdfReader(file_path)

    extracted_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text.append(text)

    return "\n".join(extracted_text)