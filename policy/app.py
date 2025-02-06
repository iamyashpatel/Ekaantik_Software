import os
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DOCX = os.path.join(BASE_DIR, "Policy-Page-1-25.docx")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_paragraphs")
OUTPUT_KEYWORDS_XLSX = os.path.join(BASE_DIR, "output_keywords.xlsx")
OUTPUT_QUESTIONS_XLSX = os.path.join(BASE_DIR, "output_policy_questions.xlsx")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created missing directory: {OUTPUT_DIR}")

def run_script(script_name):
    """Run a Python script as a subprocess."""
    script_path = os.path.join(BASE_DIR, script_name)

    if not os.path.exists(script_path):
        print(f"Error: {script_name} not found at {script_path}")
        return
    
    print(f"\nRunning {script_name}...\n")

    try:
        result = subprocess.run(
            [sys.executable, "-u", script_path],  # Force unbuffered output
            capture_output=True, 
            text=True, 
            check=True,
            cwd=BASE_DIR  # Set working directory explicitly
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise

if __name__ == "__main__":
    scripts_to_run = [
        # "convert1.py",
        # "keyword1.py", 
        # "question_generation.py", 
        "ragpipeline.py"
    ]

    for script in scripts_to_run:
        try:
            run_script(script)
        except subprocess.CalledProcessError:
            print(f"Stopping execution due to error in {script}")
            break

    print("\n✅ Script execution completed.")