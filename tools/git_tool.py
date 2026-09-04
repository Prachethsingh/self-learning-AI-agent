"""
Git Tool

Provides Git version control capabilities for the agent.
"""

from typing import Any, Dict, List, Optional
import logging
import subprocess
import asyncio
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class GitTool:
    """
    Provides Git version control capabilities.
    """

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize the Git tool.

        Args:
            repo_path: Path to the Git repository (default: current directory)
        """
        if repo_path is None:
            self.repo_path = Path.cwd()
        else:
            self.repo_path = Path(repo_path).resolve()

        # Ensure it's a valid git repository
        if not (self.repo_path / ".git").exists():
            logger.warning(f"Directory {self.repo_path} is not a Git repository")
            # We'll still allow initialization

        logger.info(f"GitTool initialized for repository: {self.repo_path}")

    async def _run_git_command(
        self,
        command: List[str],
        cwd: Optional[Path] = None
    ) -> tuple[str, str, int]:
        """
        Run a git command and return stdout, stderr, and return code.

        Args:
            command: Git command as list of strings
            cwd: Working directory (default: repo_path)

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        if cwd is None:
            cwd = self.repo_path

        try:
            process = await asyncio.create_subprocess_exec(
                "git", *command,
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            return (
                stdout.decode('utf-8'),
                stderr.decode('utf-8'),
                process.returncode
            )
        except Exception as e:
            logger.error(f"Error running git command {' '.join(command)}: {e}")
            return "", str(e), 1

    async def execute(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Execute a Git operation.

        Args:
            parameters: Dictionary containing:
                - operation: Git operation to perform (status, add, commit, push, pull, log, etc.)
                - args: Additional arguments for the operation
            context: Context information

        Returns:
            Result of the Git operation
        """
        operation = parameters.get("operation", "status")
        args = parameters.get("args", [])

        logger.info(f"Executing Git operation: {operation}")

        try:
            if operation == "status":
                return await self._git_status()
            elif operation == "add":
                return await self._git_add(args)
            elif operation == "commit":
                return await self._git_commit(args)
            elif operation == "push":
                return await self._git_push(args)
            elif operation == "pull":
                return await self._git_pull(args)
            elif operation == "log":
                return await self._git_log(args)
            elif operation == "diff":
                return await self._git_diff(args)
            elif operation == "branch":
                return await self._git_branch(args)
            elif operation == "merge":
                return await self._git_merge(args)
            elif operation == "init":
                return await self._git_init()
            elif operation == "clone":
                return await self._git_clone(args)
            else:
                raise ValueError(f"Unsupported Git operation: {operation}")

        except Exception as e:
            logger.error(f"Error executing Git operation {operation}: {e}")
            raise

    async def _git_status(self) -> Dict[str, Any]:
        """Get git status."""
        stdout, stderr, return_code = await self._run_git_command(["status", "--porcelain"])

        if return_code != 0:
            raise RuntimeError(f"Git status failed: {stderr}")

        # Parse the status output
        changes = {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": []
        }

        for line in stdout.strip().split('\n'):
            if not line:
                continue
            index = line[0]
            working = line[1]
            filename = line[3:]

            if index == 'M' or working == 'M':
                changes["modified"].append(filename)
            if index == 'A':
                changes["added"].append(filename)
            if index == 'D' or working == 'D':
                changes["deleted"].append(filename)
            if index == '?' and working == '?':
                changes["untracked"].append(filename)

        return {
            "changes": changes,
            "clean": len(stdout.strip()) == 0,
            "stdout": stdout
        }

    async def _git_add(self, args: List[str]) -> Dict[str, Any]:
        """Add files to git staging."""
        if not args:
            args = ["."]  # Default to adding all files

        stdout, stderr, return_code = await self._run_git_command(["add"] + args)

        if return_code != 0:
            raise RuntimeError(f"Git add failed: {stderr}")

        return {
            "message": f"Added files: {', '.join(args)}",
            "stdout": stdout
        }

    async def _git_commit(self, args: List[str]) -> Dict[str, Any]:
        """Commit changes."""
        # Default commit message if none provided
        if not args or not any(arg.startswith('-m') for arg in args):
            args = ["-m", "Automated commit by self-learning agent"]

        stdout, stderr, return_code = await self._run_git_command(["commit"] + args)

        if return_code != 0:
            raise RuntimeError(f"Git commit failed: {stderr}")

        return {
            "message": "Changes committed successfully",
            "stdout": stdout
        }

    async def _git_push(self, args: List[str]) -> Dict[str, Any]:
        """Push changes to remote."""
        # Default to pushing to origin main/master
        if not args:
            args = ["origin", "main"]  # Try main first

        stdout, stderr, return_code = await self._run_git_command(["push"] + args)

        if return_code != 0:
            # Try master if main failed
            if "main" in args:
                args = ["origin", "master"]
                stdout, stderr, return_code = await self._run_git_command(["push"] + args)

        if return_code != 0:
            raise RuntimeError(f"Git push failed: {stderr}")

        return {
            "message": "Changes pushed successfully",
            "stdout": stdout
        }

    async def _git_pull(self, args: List[str]) -> Dict[str, Any]:
        """Pull changes from remote."""
        if not args:
            args = ["origin", "main"]  # Try main first

        stdout, stderr, return_code = await self._run_git_command(["pull"] + args)

        if return_code != 0:
            # Try master if main failed
            if "main" in args:
                args = ["origin", "master"]
                stdout, stderr, return_code = await self._run_git_command(["pull"] + args)

        if return_code != 0:
            raise RuntimeError(f"Git pull failed: {stderr}")

        return {
            "message": "Changes pulled successfully",
            "stdout": stdout
        }

    async def _git_log(self, args: List[str]) -> Dict[str, Any]:
        """Get git log."""
        # Default options
        default_args = ["--oneline", "-10"]  # Last 10 commits in short format
        if not args:
            args = default_args

        stdout, stderr, return_code = await self._run_git_command(["log"] + args)

        if return_code != 0:
            raise RuntimeError(f"Git log failed: {stderr}")

        commits = []
        for line in stdout.strip().split('\n'):
            if line:
                commits.append(line)

        return {
            "commits": commits,
            "count": len(commits),
            "stdout": stdout
        }

    async def _git_diff(self, args: List[str]) -> Dict[str, Any]:
        """Get git diff."""
        stdout, stderr, return_code = await self._run_git_command(["diff"] + args)

        if return_code != 0:
            raise RuntimeError(f"Git diff failed: {stderr}")

        return {
            "diff": stdout,
            "stdout": stdout
        }

    async def _git_branch(self, args: List[str]) -> Dict[str, Any]:
        """List or create branches."""
        stdout, stderr, return_code = await self._run_git_command(["branch"] + args)

        if return_code != 0:
            raise RuntimeError(f"Git branch failed: {stderr}")

        branches = []
        for line in stdout.strip().split('\n'):
            if line:
                branch = line.strip().lstrip('* ')
                branches.append(branch)

        return {
            "branches": branches,
            "current": [b for b in branches if b in stdout and stdout.split('\n')[branches.index(b)].startswith('*')][0] if branches else None,
            "stdout": stdout
        }

    async def _git_merge(self, args: List[str]) -> Dict[str, Any]:
        """Merge branches."""
        if not args:
            raise ValueError("No branch specified for merge")

        stdout, stderr, return_code = await self._run_git_command(["merge"] + args)

        if return_code != 0:
            raise RuntimeError(f"Git merge failed: {stderr}")

        return {
            "message": f"Successfully merged {' '.join(args)}",
            "stdout": stdout
        }

    async def _git_init(self) -> Dict[str, Any]:
        """Initialize a git repository."""
        stdout, stderr, return_code = await self._run_git_command(["init"])

        if return_code != 0:
            raise RuntimeError(f"Git init failed: {stderr}")

        return {
            "message": "Git repository initialized successfully",
            "stdout": stdout
        }

    async def _git_clone(self, args: List[str]) -> Dict[str, Any]:
        """Clone a repository."""
        if not args:
            raise ValueError("No repository URL specified for clone")

        stdout, stderr, return_code = await self._run_git_command(["clone"] + args)

        if return_code != 0:
            raise RuntimeError(f"Git clone failed: {stderr}")

        return {
            "message": f"Successfully cloned repository",
            "stdout": stdout
        }


# Factory function for easy instantiation
def create_git_tool(repo_path: Optional[str] = None) -> GitTool:
    """
    Create a Git tool instance.

    Args:
        repo_path: Path to the Git repository

    Returns:
        GitTool instance
    """
    return GitTool(repo_path=repo_path)