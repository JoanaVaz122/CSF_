import pdfplumber
import sys

def extract_text_from_pdf(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() or ""  # handle pages with no text
    return full_text

def write_words_to_file(text, output_file_path):
    words = text.split("\n")
    with open(output_file_path, 'w', encoding='utf-8') as txt_file:
        for word in words:
            txt_file.write(word + '\n')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <pdf_file>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_file_path = "wordlist.txt"

    text = extract_text_from_pdf(pdf_path)
    write_words_to_file(text, output_file_path)