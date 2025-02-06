import openai
import os
from docx import Document
from dotenv import load_dotenv
import re
import app

load_dotenv()

def is_meaningful_paragraph(paragraph):
    """Determine if a paragraph is meaningful using OpenAI GPT."""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    text = paragraph.strip()
    if not text or len(text.split()) < 3:  # Too short, not meaningful
        return False
    
    if re.match(r'^\d+$', text):
        return False
    
    if re.match(r'^\s*(Page|Chapter|Section|Part|Date|Author)\s*[:\-]?\s*\d*$', text):
        return False

    return True

def group_paragraphs(paragraphs):
    """Group main points with sub-points together into a single paragraph."""
    grouped_paragraphs = []
    current_group = []

    main_point_pattern = re.compile(r'^\d+(\.)')  # Matches main points like 1., 2., 3., etc.
    sub_point_pattern = re.compile(r'^[a-zA-Z]\.|\d+\.$')  # Matches sub-points like a., b., 1., 2., etc.

    for paragraph in paragraphs:
        text = paragraph.text.strip()  # Use paragraph.text to access the text
        if main_point_pattern.match(text):
            if current_group:
                grouped_paragraphs.append('\n'.join(current_group))
            current_group = [text]  # Start a new group with the main point
        elif sub_point_pattern.match(text):
            current_group.append(text)
        elif is_meaningful_paragraph(text):
            current_group.append(text)

    if current_group:
        grouped_paragraphs.append('\n'.join(current_group))

    return grouped_paragraphs

def split_document_by_paragraph(file_path, output_dir):
    """Split a Word document into individual meaningful paragraphs and save each paragraph to a text file."""
    doc = Document(file_path)

    os.makedirs(output_dir, exist_ok=True)

    paragraphs = doc.paragraphs
    grouped_paragraphs = group_paragraphs(paragraphs)

    for index, group in enumerate(grouped_paragraphs, start=1):
        output_file = os.path.join(output_dir, f"group_{index}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(group)

if __name__ == "__main__":
    word_file_path = app.INPUT_DOCX # Replace with your Word file path
    output_directory = app.OUTPUT_DIR
    split_document_by_paragraph(word_file_path, output_directory)
    print(f"Document split into meaningful groups and saved in: {output_directory}")
