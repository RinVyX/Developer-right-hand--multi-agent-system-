import os

code_string = os.environ.get("CODE_TO_RUN", "")

# same safe logic from above:
def try_execute(code_string):
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

    restricted_globals = {"__builtins__": safe_builtins}

    try:
        exec(code_string, restricted_globals)
    except Exception as e:
        print(f"❌ EXECUTION ERROR:\n\n{e}")

try_execute(code_string)
