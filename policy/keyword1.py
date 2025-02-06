import os
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import app

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_keywords(paragraph):
    """
    Extract the most important keywords from a paragraph using OpenAI's GPT model.
    """
    if not paragraph or len(paragraph.strip()) < 10:
        return "Text too short"
    

    prompt = f"""
    Analyze the following paragraph and extract exactly 5-7 of the most significant keywords or phrases, following these strict criteria:

    Primary Focus (extract terms related to):
    - Policy definitions and frameworks
    - Compliance requirements and standards
    - Validation methodologies
    - Regulatory guidelines
    - Assessment criteria
    - Control mechanisms
    - Verification procedures

    Requirements:
    1. Each keyword must be a specific, concrete term (not generic words like "policy" or "check")
    2. Keywords must be actual terms mentioned in or directly implied by the text
    3. Prioritize compound terms that capture complete concepts (e.g., "risk assessment framework" over just "risk")
    4. Include only terms that serve a clear policy or compliance function
    5. Maintain the exact terminology used in the source text

    Format Rules:
    - Return ONLY the keywords
    - Separate keywords with commas
    - Use NO additional text or explanations
    - Keep exact technical terms as written in the text
    - Include NO general or contextual terms

    Paragraph: {paragraph}
    """

    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a keyword extraction assistant. Return only keywords separated by commas, no other text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.1  
        )
        
        keywords = response.choices[0].message.content
        
        keywords = keywords.replace('\n', '').strip()
        if keywords.endswith(','):
            keywords = keywords[:-1]
            
        return keywords
        
    except Exception as e:
        print(f"Error in API call: {str(e)}")
        return f"API Error: {str(e)}"

def process_text_files(input_dir, output_excel_file):
    """
    Process .txt files in a folder, extract paragraphs and keywords, and save results to an Excel file.
    """
    data = []
    error_files = []

    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    output_dir = os.path.dirname(output_excel_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process each file
    for file_name in os.listdir(input_dir):
        if not file_name.endswith(".txt"):
            continue
            
        file_path = os.path.join(input_dir, file_name)
        print(f"\nProcessing: {file_name}")

        try:
            # Read file with error handling for different encodings
            content = None
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as file:
                        content = file.read().strip()
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                raise UnicodeDecodeError(f"Could not decode file with any encoding: {file_name}")

            if not content:
                print(f"Skipping empty file: {file_name}")
                continue

            max_retries = 3
            keywords = None
            
            for attempt in range(max_retries):
                keywords = extract_keywords(content)
                if keywords and not keywords.startswith("API Error"):
                    break
                if attempt < max_retries - 1:
                    print(f"Retrying keyword extraction for {file_name} (attempt {attempt + 2})")

            data.append({
                "File Name": file_name,
                "Paragraph": content[:1000],  
                "Keywords": keywords
            })

        except Exception as e:
            error_message = f"Error processing {file_name}: {str(e)}"
            print(error_message)
            error_files.append({"File Name": file_name, "Error": error_message})

    try:
        if data:
            df = pd.DataFrame(data)
            df.to_excel(output_excel_file, index=False, engine="openpyxl", sheet_name="Keywords")
            print(f"\nSuccessfully saved results to: {output_excel_file}")

        if error_files:
            error_df = pd.DataFrame(error_files)
            with pd.ExcelWriter(output_excel_file, engine="openpyxl", mode='a') as writer:
                error_df.to_excel(writer, sheet_name="Errors", index=False)
            print(f"Saved error log to separate sheet in: {output_excel_file}")

    except Exception as e:
        print(f"Error saving Excel file: {str(e)}")
        raise

if __name__ == "__main__":
    input_directory = app.OUTPUT_DIR
    output_excel_path = app.OUTPUT_KEYWORDS_XLSX

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OpenAI API key not found. Please check your .env file.")

    try:
        process_text_files(input_directory, output_excel_path)
    except Exception as e:
        print(f"\nScript failed: {str(e)}")
