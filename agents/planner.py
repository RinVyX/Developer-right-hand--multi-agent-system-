import ollama

class PlannerAgent:
    def __init__(self, db_connector):
        self.db = db_connector
    
    def create_plan(self, input_artifact_id, prompt):
        planner_prompt = f"""
You are a PlannerAgent in a multi-agent code generation system. 
Analyze this request and break it into technical subtasks:

{prompt}

Return ONLY a numbered list of specific technical steps needed to complete this request. Each step should be:
1. Atomic (can be implemented independently)
2. Clear and unambiguous
3. In imperative form (e.g., "Load the CSV file")
4. Technical (no high-level concepts)

Numbered list:
"""
        response = ollama.chat(
            model='mistral:latest',
            messages=[{"role": "user", "content": planner_prompt}],
            options={'temperature': 0.2}
        )
        
        subtasks = response['message']['content']
        
        output_artifact_id = self.db.log_operation(
            agent_name="planner",
            input_artifact_id=input_artifact_id,
            output_content=subtasks,
            output_type="plan",
            metadata={"model": "mistral", "temperature": 0.2}
        )
        
        return {
            "content": subtasks,
            "artifact_id": output_artifact_id
        }