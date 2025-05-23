import io
import contextlib

def try_execute(code_string: str):
    safe_builtins = {
        "__import__": __import__,
        "print": print,
        "range": range,
        "len": len,
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "enumerate": enumerate,
        "zip": zip,
        "min": min,
        "max": max,
        "abs": abs,
        "sum": sum,
    }

    restricted_globals = {
        "__builtins__": safe_builtins,
    }

    output_buffer = io.StringIO()
    error_buffer = io.StringIO()

    try:
        with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(error_buffer):
            exec(code_string, restricted_globals)
        return output_buffer.getvalue(), None
    except Exception as e:
        return output_buffer.getvalue(), str(e)
