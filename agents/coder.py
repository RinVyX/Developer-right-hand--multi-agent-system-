import ollama
from utils.code_cleaner import clean_generated_code

class CoderAgent:
    def __init__(self, db_connector):
        self.db = db_connector
    
    def generate_code(self, input_artifact_id, subtasks, attempt=0):
        coder_prompt = f"""
You are a CoderAgent. Implement these steps as Python code:

{subtasks}

Rules:
1. Output ONLY raw Python code
2. No explanations or comments
3. Include all necessary imports
4. The code will process a CSV file at path '__file__'
5. Make it work on first try (but include 1-2 subtle bugs if attempt < 2)
"""
        response = ollama.chat(
            model='deepseek-coder:6.7b',
            messages=[{"role": "user", "content": coder_prompt}],
            options={'temperature': 0.7 if attempt < 2 else 0.3}
        )
        
        raw_code = response['message']['content']
        clean_code = clean_generated_code(raw_code)
        
        output_artifact_id = self.db.log_operation(
            agent_name="coder",
            input_artifact_id=input_artifact_id,
            output_content=clean_code,
            output_type="code",
            metadata={
                "model": "deepseek-coder",
                "temperature": 0.7 if attempt < 2 else 0.3,
                "attempt": attempt
            }
        )
        
        return {
            "content": clean_code,
            "artifact_id": output_artifact_id
        }