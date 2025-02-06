import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import app

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_policy_questions(paragraph):
    """
    Generate actionable compliance questions based on the base policy paragraph.
    """
    prompt = f"""
    Analyze the following paragraph from a base policy document and generate specific, actionable questions that can be used to evaluate compliance in another document. Follow these guidelines:

    1. **Focus on Compliance**:
       - Generate questions that check if the client's document complies with the policy.
       - Questions should be answerable with "yes," "no," or specific details.

    2. **Actionable Questions**:
       - Use phrases like "Does the client...", "Where does the client...", "How does the client...".
       - Ensure questions are specific and directly related to the policy.

    3. **Policy Requirements**:
       - Highlight key requirements from the paragraph and turn them into questions.
       - Example: If the policy states "Data must be stored in Europe," generate the question "Where does the client store the data?"

    4. **Output Format**:
       - Return only the questions, one per line.
       - Do not include explanations or additional text.

    Paragraph: {paragraph}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a compliance question-generation assistant. Generate specific, actionable questions to evaluate compliance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3  # Low temperature for consistent results
        )
        
        questions = response.choices[0].message.content.strip()
        return questions
    
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return f"API Error: {str(e)}"

def process_text_files_for_questions(input_dir, output_question_excel):
    """
    Process .txt files in a folder, generate relevant policy-related questions, and save results to an Excel file.
    """
    question_data = []
    error_files = []

    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    output_dir = os.path.dirname(output_question_excel)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name in os.listdir(input_dir):
        if not file_name.endswith(".txt"):
            continue
            
        file_path = os.path.join(input_dir, file_name)
        print(f"\nProcessing for questions: {file_name}")

        try:
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

            questions = generate_policy_questions(content)
            question_data.append({
                "File Name": file_name,
                "Paragraph": content[:1000],  # Limit paragraph length in Excel
                "Questions": questions
            })

        except Exception as e:
            error_message = f"Error processing {file_name}: {str(e)}"
            print(error_message)
            error_files.append({"File Name": file_name, "Error": error_message})

    # Save results
    try:
        if question_data:
            question_df = pd.DataFrame(question_data)
            question_df.to_excel(output_question_excel, index=False, engine="openpyxl", sheet_name="Questions")
            print(f"\nSuccessfully saved policy questions to: {output_question_excel}")

        if error_files:
            error_df = pd.DataFrame(error_files)
            with pd.ExcelWriter(output_question_excel, engine="openpyxl", mode='a') as writer:
                error_df.to_excel(writer, sheet_name="Errors", index=False)
            print(f"Saved error log to separate sheet in: {output_question_excel}")

    except Exception as e:
        print(f"Error saving Excel file: {str(e)}")
        raise

if __name__ == "__main__":
    input_directory = app.OUTPUT_DIR 
    output_questions_path = app.OUTPUT_QUESTIONS_XLSX

    # Validate API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OpenAI API key not found. Please check your .env file.")

    try:
        process_text_files_for_questions(input_directory, output_questions_path)
    except Exception as e:
        print(f"\nScript failed: {str(e)}")
