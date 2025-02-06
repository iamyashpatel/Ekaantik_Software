import os
import pandas as pd
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import app

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RAGPipeline:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.paragraphs = []
        self.keywords = []
        self.file_names = []
        self.paragraph_vectors = None
        
    def load_data(self, input_dir, keywords_excel):
        """Load paragraphs from text files and keywords from Excel"""
        print("Loading keywords from Excel...")
        try:
            keywords_df = pd.read_excel(keywords_excel, sheet_name="Keywords")
            keywords_dict = dict(zip(keywords_df["File Name"], keywords_df["Keywords"]))
            print(f"Loaded keywords for {len(keywords_dict)} files")
        except Exception as e:
            print(f"Error loading keywords file: {str(e)}")
            return 0

        print("\nLoading and processing text files...")
        self.paragraphs = []
        self.keywords = []
        self.file_names = []
        
        for file_name in os.listdir(input_dir):
            if not file_name.endswith('.txt'):
                continue
                
            file_path = os.path.join(input_dir, file_name)
            
            try:
                content = None
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            content = file.read().strip()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content and len(content.strip()) > 10:
                    keywords = keywords_dict.get(file_name, "")
                    
                    self.paragraphs.append(content)
                    self.keywords.append(keywords)
                    self.file_names.append(file_name)
                    
                    print(f"Processed: {file_name}")
                    print(f"Keywords: {keywords}\n")
                
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")
        
        if self.paragraphs:
            combined_text = [f"{para} {keys}" for para, keys in zip(self.paragraphs, self.keywords)]
            self.paragraph_vectors = self.vectorizer.fit_transform(combined_text)
        
        return len(self.paragraphs)
    
    def find_relevant_paragraphs(self, question, top_k=3):
        """Find the most relevant paragraphs for a given question"""
        question_vector = self.vectorizer.transform([question])
        
        similarity_scores = cosine_similarity(question_vector, self.paragraph_vectors).flatten()
        
        top_indices = np.argsort(similarity_scores)[-top_k:][::-1]
        
        return [(self.paragraphs[i], self.keywords[i], self.file_names[i], similarity_scores[i]) 
                for i in top_indices if similarity_scores[i] > 0]

    def generate_summary(self, full_answer):
        """Generate a summary of the full answer"""
        summary_prompt = f"""
        Summarize the following answer in a concise manner while preserving the main points:

        Answer: {full_answer}

        Provide a brief summary:
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are an assistant that summarizes answers concisely."},
                          {"role": "user", "content": summary_prompt}],
                max_tokens=150,
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def generate_answer(self, question, relevant_paragraphs):
        """Generate a detailed answer using the relevant paragraphs"""
        context = "\n\n".join([f"File: {file_name}\nParagraph (Relevance: {score:.2f}):\n{para}\n\nKeywords: {keys}" 
                              for para, keys, file_name, score in relevant_paragraphs])
        
        prompt = f"""
        Based on the following context paragraphs and their relevance scores, answer the question.
        Use information directly from the provided paragraphs and cite which file/paragraph you're using.
        If the paragraphs don't contain enough information to fully answer the question, say so.

        Question: {question}

        Context:
        {context}

        Please provide a detailed answer, citing specific files/paragraphs where possible.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a policy expert assistant. Provide accurate answers based on the given context."},
                          {"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.4
            )
            
            full_answer = response.choices[0].message.content.strip()
            
            summary = self.generate_summary(full_answer)
            
            return full_answer, summary
            
        except Exception as e:
            return f"Error generating answer: {str(e)}", ""

def process_questions_from_excel(excel_file, rag_pipeline):
    """Process the questions from the Excel file and generate answers"""
    try:
        excel_file_obj = pd.ExcelFile(excel_file)
        print(f"Available sheets in Excel: {excel_file_obj.sheet_names}")
        
        if "Questions" not in excel_file_obj.sheet_names:
            print(f"Sheet 'Questions' not found! Available sheets: {excel_file_obj.sheet_names}")
            return
        
        questions_df = pd.read_excel(excel_file_obj, sheet_name="Questions")
        print(f"Columns in 'Questions' sheet: {questions_df.columns}")
        
        questions = questions_df["Questions"].dropna().tolist()
        file_names = questions_df["File Name"].tolist()

        answers = []
        for idx, question_set in enumerate(questions):
            print(f"\nProcessing questions from file: {file_names[idx]}")

            question_list = question_set.split("\n")
            for question in question_list:
                question = question.strip()
                if question:
                    print(f"\nQuestion: {question}")
                    relevant_paragraphs = rag_pipeline.find_relevant_paragraphs(question)
                    
                    if not relevant_paragraphs:
                        answers.append({"File": file_names[idx], "Question": question, "Answer": "No relevant information found.", "Summary": ""})
                    else:
                        print("\nGenerating answer...")
                        full_answer, summary = rag_pipeline.generate_answer(question, relevant_paragraphs)
                        answers.append({"File": file_names[idx], "Question": question, "Answer": full_answer, "Summary": summary})
            
        answers_df = pd.DataFrame(answers)
        answers_df.to_excel("generated_answers_with_summary.xlsx", index=False)
        print("\nAnswers with summaries saved to 'generated_answers_with_summary.xlsx'.")
    
    except Exception as e:
        print(f"Error processing questions: {str(e)}")

def interactive_qa_session(rag_pipeline):
    """Run an interactive Q&A session using the RAG pipeline"""
    print("\nWelcome to the Policy Q&A System!")
    print("Type 'quit' to exit the session")
    
    while True:
        print("\nEnter your question:")
        question = input("> ").strip()
        
        if question.lower() == 'quit':
            break
            
        relevant_paragraphs = rag_pipeline.find_relevant_paragraphs(question)
        
        if not relevant_paragraphs:
            print("\nNo relevant information found for your question.")
            continue
            
        print("\nGenerating answer...")
        full_answer, summary = rag_pipeline.generate_answer(question, relevant_paragraphs)
        
        print("\nAnswer:")
        print(full_answer)
        print("\nSummary:")
        print(summary)

if __name__ == "__main__":
    rag = RAGPipeline()
    
    
    input_directory = app.OUTPUT_DIR  
    keywords_file = app.OUTPUT_KEYWORDS_XLSX  
    questions_file = app.OUTPUT_QUESTIONS_XLSX  
    
    try:
        
        num_paragraphs = rag.load_data(input_directory, keywords_file)
        print(f"\nLoaded and processed {num_paragraphs} paragraphs successfully!")
        
        if num_paragraphs > 0:
            print("Processing questions from Excel...")
            process_questions_from_excel(questions_file, rag)
        else:
            print("No valid paragraphs found. Please check your input directory.")
    
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
