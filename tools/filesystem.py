"""
File System Tool

Provides safe file system operations for the agent.
"""

from typing import Any, Dict, List, Optional
import logging
import os
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)


class FileSystemTool:
    """
    Provides safe file system operations.
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the file system tool.

        Args:
            base_path: Base directory for file operations (for security)
        """
        if base_path is None:
            # Use current working directory as default
            self.base_path = Path.cwd()
        else:
            self.base_path = Path(base_path).resolve()

        # Ensure base path exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"FileSystemTool initialized with base path: {self.base_path}")

    def _safe_path(self, path: str) -> Path:
        """
        Convert a path to a safe path within the base directory.

        Args:
            path: The path to make safe

        Returns:
            A safe Path object within the base directory

        Raises:
            ValueError: If the path tries to escape the base directory
        """
        # Convert to Path object
        target_path = Path(path)

        # If it's already absolute, check if it's within base_path
        if target_path.is_absolute():
            resolved_path = target_path.resolve()
        else:
            # Relative path - resolve relative to base_path
            resolved_path = (self.base_path / target_path).resolve()

        # Check if the resolved path is within base_path
        try:
            resolved_path.relative_to(self.base_path.resolve())
            return resolved_path
        except ValueError:
            raise ValueError(f"Access denied: path {path} is outside allowed directory {self.base_path}")

    async def read_file(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Read a file.

        Args:
            parameters: Dictionary containing:
                - file_path: Path to the file to read
                - encoding: File encoding (default: utf-8)
            context: Context information

        Returns:
            Contents of the file
        """
        file_path = parameters.get("file_path", "")
        encoding = parameters.get("encoding", "utf-8")

        if not file_path:
            raise ValueError("No file path provided")

        logger.info(f"Reading file: {file_path}")

        try:
            safe_path = self._safe_path(file_path)

            if not safe_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read the file
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None, lambda: safe_path.read_text(encoding=encoding)
            )

            return {
                "content": content,
                "file_path": str(safe_path),
                "size": safe_path.stat().st_size
            }

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    async def write_file(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Write a file.

        Args:
            parameters: Dictionary containing:
                - file_path: Path to the file to write
                - content: Content to write to the file
                - encoding: File encoding (default: utf-8)
                - mode: Write mode ('w' for write, 'a' for append)
            context: Context information

        Returns:
            Result of the write operation
        """
        file_path = parameters.get("file_path", "")
        content = parameters.get("content", "")
        encoding = parameters.get("encoding", "utf-8")
        mode = parameters.get("mode", "w")

        if not file_path:
            raise ValueError("No file path provided")

        logger.info(f"Writing to file: {file_path}")

        try:
            safe_path = self._safe_path(file_path)

            # Ensure parent directory exists
            safe_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, lambda: safe_path.write_text(content, encoding=encoding)
            )

            return {
                "file_path": str(safe_path),
                "bytes_written": len(content.encode(encoding)),
                "mode": mode
            }

        except Exception as e:
            logger.error(f"Error writing to file {file_path}: {e}")
            raise

    async def list_directory(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        List contents of a directory.

        Args:
            parameters: Dictionary containing:
                - directory_path: Path to the directory to list
                - recursive: Whether to list recursively (default: False)
                - include_hidden: Whether to include hidden files (default: False)
            context: Context information

        Returns:
            List of files and directories
        """
        directory_path = parameters.get("directory_path", "")
        recursive = parameters.get("recursive", False)
        include_hidden = parameters.get("include_hidden", False)

        if not directory_path:
            # Default to base path
            directory_path = "."

        logger.info(f"Listing directory: {directory_path}")

        try:
            safe_path = self._safe_path(directory_path)

            if not safe_path.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")

            if not safe_path.is_dir():
                raise NotADirectoryError(f"Not a directory: {directory_path}")

            # List directory contents
            items = []

            if recursive:
                for item in safe_path.rglob("*"):
                    # Skip hidden files if not included
                    if not include_hidden and any(part.startswith('.') for part in item.parts):
                        continue
                    items.append({
                        "path": str(item.relative_to(self.base_path)),
                        "full_path": str(item),
                        "is_file": item.is_file(),
                        "is_dir": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else 0
                    })
            else:
                for item in safe_path.iterdir():
                    # Skip hidden files if not included
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    items.append({
                        "path": str(item.relative_to(self.base_path)),
                        "full_path": str(item),
                        "is_file": item.is_file(),
                        "is_dir": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else 0
                    })

            return {
                "directory": str(safe_path.relative_to(self.base_path)),
                "items": items,
                "count": len(items)
            }

        except Exception as e:
            logger.error(f"Error listing directory {directory_path}: {e}")
            raise

    async def delete_file(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Delete a file.

        Args:
            parameters: Dictionary containing:
                - file_path: Path to the file to delete
            context: Context information

        Returns:
            Result of the delete operation
        """
        file_path = parameters.get("file_path", "")

        if not file_path:
            raise ValueError("No file path provided")

        logger.info(f"Deleting file: {file_path}")

        try:
            safe_path = self._safe_path(file_path)

            if not safe_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if safe_path.is_dir():
                raise IsADirectoryError(f"Cannot delete directory with delete_file: {file_path}. Use delete_directory instead.")

            # Delete the file
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: safe_path.unlink())

            return {
                "file_path": str(safe_path),
                "deleted": True
            }

        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            raise

    async def create_directory(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Create a directory.

        Args:
            parameters: Dictionary containing:
                - directory_path: Path to the directory to create
                - parents: Whether to create parent directories (default: True)
                - exist_ok: Whether to OK if directory exists (default: True)
            context: Context information

        Returns:
            Result of the create operation
        """
        directory_path = parameters.get("directory_path", "")
        parents = parameters.get("parents", True)
        exist_ok = parameters.get("exist_ok", True)

        if not directory_path:
            raise ValueError("No directory path provided")

        logger.info(f"Creating directory: {directory_path}")

        try:
            safe_path = self._safe_path(directory_path)

            # Create the directory
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, lambda: safe_path.mkdir(parents=parents, exist_ok=exist_ok)
            )

            return {
                "directory_path": str(safe_path),
                "created": True
            }

        except Exception as e:
            logger.error(f"Error creating directory {directory_path}: {e}")
            raise


# Factory function for easy instantiation
def create_filesystem_tool(base_path: Optional[str] = None) -> FileSystemTool:
    """
    Create a file system tool instance.

    Args:
        base_path: Base directory for file operations (for security)

    Returns:
        FileSystemTool instance
    """
    return FileSystemTool(base_path=base_path)