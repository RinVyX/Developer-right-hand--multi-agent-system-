import re

def clean_generated_code(code):
    """Remove LLM artifacts from generated code."""
    # Remove markdown code blocks
    code = re.sub(r'```(?:python)?\s*(.*?)\s*```', r'\1', code, flags=re.DOTALL)
    
    # Remove special tokens and artifacts
    code = re.sub(r'[｜<][^\n]*?[>|\n]', '', code)
    
    # Remove empty lines at start/end
    return code.strip()