"""
Database Tool

Provides database query capabilities for the agent.
"""

from typing import Any, Dict, List, Optional
import logging
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class DatabaseTool:
    """
    Provides database query capabilities.
    """

    def __init__(self, database_url: str):
        """
        Initialize the database tool.

        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        # For async operations
        if "postgresql://" in database_url:
            async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif database_url.startswith("sqlite"):
            async_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")
        else:
            async_url = database_url
        self.async_engine = create_async_engine(async_url)
        self.AsyncSessionLocal = sessionmaker(
            self.async_engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info("DatabaseTool initialized")

    async def execute_query(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Execute a database query.

        Args:
            parameters: Dictionary containing:
                - query: SQL query to execute
                - params: Query parameters (optional)
                - fetch: Whether to fetch results (default: True)
                - commit: Whether to commit transaction (default: False)
            context: Context information

        Returns:
            Query results or execution status
        """
        query = parameters.get("query", "")
        params = parameters.get("params", {})
        fetch = parameters.get("fetch", True)
        commit = parameters.get("commit", False)

        if not query.strip():
            raise ValueError("No query provided")

        logger.info(f"Executing database query: {query[:100]}...")

        try:
            async with self.AsyncSessionLocal() as session:
                # Execute the query
                result = await session.execute(text(query), params)

                if commit:
                    await session.commit()
                    logger.info("Transaction committed")

                if fetch:
                    # Fetch results
                    if result.returns_rows:
                        rows = result.fetchall()
                        # Convert to list of dictionaries
                        columns = result.keys()
                        data = [dict(zip(columns, row)) for row in rows]
                        logger.info(f"Query returned {len(data)} rows")
                        return {
                            "data": data,
                            "row_count": len(data),
                            "columns": list(columns)
                        }
                    else:
                        logger.info("Query executed successfully (no rows returned)")
                        return {
                            "affected_rows": result.rowcount,
                            "message": "Query executed successfully"
                        }
                else:
                    await session.commit()
                    return {
                        "message": "Query executed successfully",
                        "affected_rows": result.rowcount if hasattr(result, 'rowcount') else 0
                    }

        except Exception as e:
            logger.error(f"Error executing database query: {e}")
            raise

    async def get_table_schema(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Get the schema of a table.

        Args:
            parameters: Dictionary containing:
                - table_name: Name of the table
            context: Context information

        Returns:
            Table schema information
        """
        table_name = parameters.get("table_name", "")

        if not table_name:
            raise ValueError("No table name provided")

        logger.info(f"Getting schema for table: {table_name}")

        try:
            # Query to get table schema
            query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position
            """

            result = await self.execute_query({
                "query": query,
                "params": {"table_name": table_name},
                "fetch": True
            }, context)

            return result

        except Exception as e:
            logger.error(f"Error getting table schema: {e}")
            raise

    async def list_tables(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        List all tables in the database.

        Args:
            parameters: Dictionary (unused)
            context: Context information

        Returns:
            List of table names
        """
        logger.info("Listing database tables")

        try:
            query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """

            result = await self.execute_query({
                "query": query,
                "fetch": True
            }, context)

            table_names = [row["table_name"] for row in result.get("data", [])]
            return {
                "tables": table_names,
                "count": len(table_names)
            }

        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            raise

    async def close(self):
        """Close the database connections."""
        await self.async_engine.dispose()
        logger.info("Database connections closed")


# Factory function for easy instantiation
def create_database_tool(database_url: str) -> DatabaseTool:
    """
    Create a database tool instance.

    Args:
        database_url: Database connection URL

    Returns:
        DatabaseTool instance
    """
    return DatabaseTool(database_url=database_url)