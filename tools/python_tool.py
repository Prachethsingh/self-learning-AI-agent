"""
Python Execution Tool

Provides safe Python code execution capabilities for the agent.
"""

from typing import Any, Dict, List, Optional
import logging
import subprocess
import tempfile
import os
import sys
import asyncio
import json

logger = logging.getLogger(__name__)


class PythonTool:
    """
    Provides safe Python code execution capabilities.
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize the Python execution tool.

        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout

    async def execute(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Execute Python code.

        Args:
            parameters: Dictionary containing:
                - code: Python code to execute
                - imports: List of imports to include (optional)
                - packages: List of packages to install (optional)
            context: Context information

        Returns:
            Result of the Python execution
        """
        code = parameters.get("code", "")
        imports = parameters.get("imports", [])
        packages = parameters.get("packages", [])

        if not code.strip():
            raise ValueError("No code provided for execution")

        logger.info(f"Executing Python code (length: {len(code)} chars)")

        try:
            # Install packages if specified
            if packages:
                await self._install_packages(packages)

            # Prepare the code with imports
            full_code = self._prepare_code(imports, code)

            # Execute the code
            result = await self._execute_code(full_code)

            return result

        except Exception as e:
            logger.error(f"Error executing Python code: {e}")
            raise

    async def _install_packages(self, packages: List[str]) -> None:
        """Install required packages using pip."""
        if not packages:
            return

        logger.info(f"Installing packages: {packages}")
        for package in packages:
            try:
                process = await asyncio.create_subprocess_exec(
                    sys.executable, "-m", "pip", "install", package,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    logger.warning(f"Failed to install {package}: {stderr.decode()}")
                else:
                    logger.info(f"Successfully installed {package}")

            except Exception as e:
                logger.error(f"Error installing package {package}: {e}")

    def _prepare_code(self, imports: List[str], code: str) -> str:
        """Prepare the code with necessary imports."""
        import_lines = []
        for imp in imports:
            import_lines.append(f"import {imp}")

        if import_lines:
            return "\n".join(import_lines) + "\n\n" + code
        else:
            return code

    async def _execute_code(self, code: str) -> Any:
        """Execute the Python code in a subprocess."""
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Execute the code
            process = await asyncio.create_subprocess_exec(
                sys.executable, temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Python execution timed out after {self.timeout} seconds")

            # Decode output
            stdout_text = stdout.decode('utf-8')
            stderr_text = stderr.decode('utf-8')

            # Check for errors
            if process.returncode != 0:
                raise RuntimeError(f"Python execution failed: {stderr_text}")

            # Try to parse output as JSON if possible
            try:
                return json.loads(stdout_text.strip())
            except json.JSONDecodeError:
                # Return as string if not JSON
                return stdout_text.strip() if stdout_text.strip() else None

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except OSError:
                pass


# Factory function for easy instantiation
def create_python_tool(timeout: int = 30) -> PythonTool:
    """
    Create a Python execution tool instance.

    Args:
        timeout: Maximum execution time in seconds

    Returns:
        PythonTool instance
    """
    return PythonTool(timeout=timeout)