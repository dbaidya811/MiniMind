import sys
import io
import contextlib

class PythonExecutor:
    @staticmethod
    def execute_code(code_str: str) -> str:
        """Executes a snippet of Python code and captures standard output."""
        # Strip markdown syntax if present
        cleaned_code = code_str.replace("```python", "").replace("```", "").strip()
        
        stdout_trap = io.StringIO()
        stderr_trap = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(stdout_trap), contextlib.redirect_stderr(stderr_trap):
                # Execute in an isolated namespace
                exec_globals = {}
                exec(cleaned_code, exec_globals)
            
            output = stdout_trap.getvalue()
            error = stderr_trap.getvalue()
            
            if error:
                return f"[Runtime Error]:\n{error}"
            return output.strip() if output.strip() else "[Execution Successful with no console output]"
        except Exception as e:
            return f"[Execution Failed]: {str(e)}"