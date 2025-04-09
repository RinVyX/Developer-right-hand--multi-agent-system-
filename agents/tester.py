import ollama
from utils.executor import try_execute

class TesterAgent:
    def __init__(self, db_connector):
        self.db = db_connector
    
    def test_code(self, input_artifact_id, code_content, user_request):
        output, error = try_execute(code_content)
        
        tester_prompt = f"""
As TesterAgent, evaluate this code against the original request:

REQUEST: {user_request}

CODE:
{code_content}

EXECUTION RESULT:
{'ERROR: ' + error if error else 'OUTPUT: ' + output}

Return ONLY one of these verdicts:
1. "APPROVED" - Code perfectly meets requirements
2. "MINOR_ISSUES" - Works but needs small improvements
3. "MAJOR_ISSUES" - Has significant problems
"""
        response = ollama.chat(
            model='deepseek-coder:6.7b',
            messages=[{"role": "user", "content": tester_prompt}],
            options={'temperature': 0}
        )
        
        test_result = response['message']['content'].strip()
        
        output_artifact_id = self.db.log_operation(
            agent_name="tester",
            input_artifact_id=input_artifact_id,
            output_content=test_result,
            output_type="test",
            execution_result=error or output,
            metadata={
                "verdict": test_result,
                "model": "deepseek-coder"
            }
        )
        
        return {
            "verdict": test_result,
            "artifact_id": output_artifact_id,
            "output": output,
            "error": error
        }