"""
Code Executor Tool
Safely executes Python code for calculations.
"""
import asyncio
from typing import Any

from loguru import logger
from RestrictedPython import compile_restricted, safe_globals


class CodeExecutor:
    """Secure Python code executor using RestrictedPython.
    
    Executes Python code in a sandboxed environment with limited
    built-in functions and no file system or network access.
    
    Features:
    - RestrictedPython for security
    - Timeout protection
    - Safe built-ins only (math, basic types, no I/O)
    - Async execution with asyncio
    """
    
    def __init__(self, timeout: int = 10):
        """Initialize code executor.
        
        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
    
    async def execute(self, code: str) -> dict[str, Any]:
        """Execute Python code safely with timeout protection.
        
        Args:
            code: Python code string to execute
            
        Returns:
            dict: Result with keys:
                - success (bool): Whether execution succeeded
                - output (Any): Result or printed output
                - error (str): Error message if failed
        """
        logger.info(f"Executing code (timeout={self.timeout}s)")
        logger.debug(f"Code:\n{code}")
        
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(self._execute_sync, code),
                timeout=self.timeout
            )
            return result
        
        except asyncio.TimeoutError:
            logger.error(f"Code execution timeout")
            return {
                "success": False,
                "output": None,
                "error": f"Timeout: {self.timeout}s",
            }
        
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "success": False,
                "output": None,
                "error": str(e),
            }
    
    def _execute_sync(self, code: str) -> dict[str, Any]:
        """Synchronous execution in restricted environment.
        
        Args:
            code: Python code to execute
            
        Returns:
            dict: Execution result
        """
        try:
            # Compile with restrictions
            byte_code = compile_restricted(code, '<inline>', 'exec')
            
            # Safe globals
            restricted_globals = safe_globals.copy()
            restricted_globals['__builtins__'] = self._get_safe_builtins()
            
            # Capture output
            output_lines = []
            
            def safe_print(*args, **kwargs):
                output_lines.append(" ".join(str(arg) for arg in args))
            
            restricted_globals['print'] = safe_print
            
            # Execute
            exec(byte_code, restricted_globals)
            
            # Get result
            result = restricted_globals.get('result')
            output = result if result is not None else "\n".join(output_lines)
            
            return {
                "success": True,
                "output": output,
                "error": None,
            }
        
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e),
            }
    
    def _get_safe_builtins(self) -> dict:
        """Get whitelist of safe built-in functions.
        
        Returns:
            dict: Mapping of safe function names to functions
        """
        return {
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'abs': abs,
            'round': round,
            'sum': sum,
            'min': min,
            'max': max,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'sorted': sorted,
            'print': print,
        }
