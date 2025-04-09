import ollama

class DocumentationAgent:
    def __init__(self, db_connector):
        self.db = db_connector
    
    def create_docs(self, input_artifact_id, code_content):
        documentation_prompt = f"""
Add documentation to this Python code:

{code_content}

Include:
1. Inline comments explaining key steps
2. A docstring at the top describing:
   - Purpose
   - Inputs
   - Outputs
   - Usage example
3. Keep all original code functionality

Return ONLY the documented code:
"""
        response = ollama.chat(
            model='codellama:latest',
            messages=[{"role": "user", "content": documentation_prompt}],
            options={'temperature': 0.2}
        )
        
        documented_code = response['message']['content']
        
        output_artifact_id = self.db.log_operation(
            agent_name="documentation",
            input_artifact_id=input_artifact_id,
            output_content=documented_code,
            output_type="documentation",
            metadata={"model": "codellama"}
        )
        
        return {
            "content": documented_code,
            "artifact_id": output_artifact_id
        }