import sys
import io
import traceback

def try_execute(code_string, file_path='fake_data.csv'):
    """Safely execute Python code in a sandboxed environment."""
    # Create a limited global context
    restricted_globals = {
        '__file__': file_path,
        '__name__': '__main__',
        '__builtins__': {
            # add only if you utrust the code to be run on your machine
            "__import__": __import__,
            'print': print,
            'range': range,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict
        }
    }
    
    # Redirect stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    
    try:
        exec(code_string, restricted_globals)
        output = sys.stdout.getvalue()
        error = None
    except Exception as e:
        output = sys.stdout.getvalue()
        error = f"{sys.stderr.getvalue()}\n{traceback.format_exc()}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    return output, error