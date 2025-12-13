"""
Text2SQL Service - Convert natural language to SQL queries
Used by LLM to interact with databases via chat
"""

import re
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional

# Database schemas for context
SCHEMAS = {}

class Text2SQL:
    """Convert natural language queries to SQL"""
    
    # Common query patterns
    PATTERNS = {
        # SELECT patterns
        r"pokaż wszystk[ioey]?\s+(.+)": "SELECT * FROM {table}",
        r"lista\s+(.+)": "SELECT * FROM {table}",
        r"ile\s+(.+)": "SELECT COUNT(*) FROM {table}",
        r"policz\s+(.+)": "SELECT COUNT(*) FROM {table}",
        r"znajdź\s+(.+)\s+gdzie\s+(.+)": "SELECT * FROM {table} WHERE {condition}",
        r"szukaj\s+(.+)\s+z\s+(.+)": "SELECT * FROM {table} WHERE {column} LIKE '%{value}%'",
        
        # Aggregate patterns
        r"suma\s+(.+)\s+z\s+(.+)": "SELECT SUM({column}) FROM {table}",
        r"średnia\s+(.+)\s+z\s+(.+)": "SELECT AVG({column}) FROM {table}",
        r"maksymalna?\s+(.+)\s+z\s+(.+)": "SELECT MAX({column}) FROM {table}",
        r"minimalna?\s+(.+)\s+z\s+(.+)": "SELECT MIN({column}) FROM {table}",
        
        # INSERT/UPDATE patterns (admin only)
        r"dodaj\s+(.+)\s+do\s+(.+)": "INSERT INTO {table} VALUES ({values})",
        r"usuń\s+(.+)\s+z\s+(.+)": "DELETE FROM {table} WHERE {condition}",
        r"aktualizuj\s+(.+)\s+ustaw\s+(.+)": "UPDATE {table} SET {values}",
    }
    
    # Table name mappings (Polish -> English)
    TABLE_MAP = {
        "użytkownicy": "users",
        "użytkowników": "users",
        "dokumenty": "documents",
        "dokumentów": "documents",
        "faktury": "invoices",
        "faktur": "invoices",
        "sesje": "sessions",
        "sesji": "sessions",
        "logi": "logs",
        "logów": "logs",
        "konfiguracja": "config",
        "konfiguracji": "config",
        "pliki": "files",
        "plików": "files",
    }
    
    @classmethod
    def register_schema(cls, db_name: str, schema: Dict[str, List[str]]):
        """Register database schema for better query generation"""
        SCHEMAS[db_name] = schema
    
    @classmethod
    def text2sql(cls, text: str, db_name: str = "default", role: str = "user") -> Dict[str, Any]:
        """
        Convert natural language to SQL query
        
        Args:
            text: Natural language query
            db_name: Target database name
            role: User role (user/manager/admin) - affects allowed operations
        
        Returns:
            {"success": bool, "sql": str, "params": list, "operation": str}
        """
        text_lower = text.lower().strip()
        
        # Determine operation type
        operation = cls._detect_operation(text_lower)
        
        # Check permissions
        if operation in ["INSERT", "UPDATE", "DELETE"] and role not in ["admin", "manager"]:
            return {
                "success": False,
                "error": "Permission denied",
                "message": f"Operacja {operation} wymaga uprawnień admina lub managera"
            }
        
        # Try to match patterns
        for pattern, sql_template in cls.PATTERNS.items():
            match = re.search(pattern, text_lower)
            if match:
                sql, params = cls._build_query(sql_template, match.groups(), text_lower)
                return {
                    "success": True,
                    "sql": sql,
                    "params": params,
                    "operation": operation,
                    "original": text
                }
        
        # Fallback - try simple table lookup
        for polish, english in cls.TABLE_MAP.items():
            if polish in text_lower:
                return {
                    "success": True,
                    "sql": f"SELECT * FROM {english} LIMIT 100",
                    "params": [],
                    "operation": "SELECT",
                    "original": text
                }
        
        return {
            "success": False,
            "error": "Could not parse query",
            "message": f"Nie udało się zrozumieć zapytania: {text}"
        }
    
    @classmethod
    def _detect_operation(cls, text: str) -> str:
        """Detect SQL operation type from text"""
        if any(w in text for w in ["dodaj", "wstaw", "utwórz", "insert"]):
            return "INSERT"
        elif any(w in text for w in ["usuń", "skasuj", "delete"]):
            return "DELETE"
        elif any(w in text for w in ["aktualizuj", "zmień", "update"]):
            return "UPDATE"
        else:
            return "SELECT"
    
    @classmethod
    def _build_query(cls, template: str, groups: tuple, text: str) -> tuple:
        """Build SQL query from template and matched groups"""
        params = []
        sql = template
        
        # Map Polish table names
        if groups:
            table = groups[0].strip()
            table = cls.TABLE_MAP.get(table, table)
            sql = sql.replace("{table}", table)
            
            if len(groups) > 1:
                # Additional parameters (column, condition, etc.)
                for i, g in enumerate(groups[1:], 1):
                    sql = sql.replace(f"{{param{i}}}", g.strip())
        
        return sql, params


class SQL2Text:
    """Convert SQL results to natural language"""
    
    @classmethod
    def sql2text(cls, results: List[Dict], query: str, operation: str = "SELECT") -> str:
        """
        Convert SQL query results to natural language response
        
        Args:
            results: Query results (list of dicts)
            query: Original SQL query
            operation: SQL operation type
        
        Returns:
            Natural language response string
        """
        if not results:
            return "Nie znaleziono wyników."
        
        # Count query
        if "COUNT" in query.upper():
            count = results[0].get("COUNT(*)", 0) if results else 0
            return f"Znaleziono {count} rekordów."
        
        # Sum/Avg/Max/Min queries
        for agg in ["SUM", "AVG", "MAX", "MIN"]:
            if agg in query.upper():
                for key, value in results[0].items():
                    if value is not None:
                        agg_names = {"SUM": "Suma", "AVG": "Średnia", "MAX": "Maksimum", "MIN": "Minimum"}
                        return f"{agg_names[agg]}: {value}"
        
        # Regular SELECT
        count = len(results)
        if count == 1:
            return cls._format_single_result(results[0])
        else:
            return cls._format_multiple_results(results)
    
    @classmethod
    def _format_single_result(cls, row: Dict) -> str:
        """Format single row result"""
        parts = [f"{k}: {v}" for k, v in row.items() if v is not None]
        return " | ".join(parts)
    
    @classmethod
    def _format_multiple_results(cls, rows: List[Dict]) -> str:
        """Format multiple row results"""
        count = len(rows)
        preview = rows[:5]  # Show first 5
        
        lines = [f"Znaleziono {count} wyników:"]
        for i, row in enumerate(preview, 1):
            # Get key columns
            name = row.get("name") or row.get("title") or row.get("id", f"#{i}")
            lines.append(f"  {i}. {name}")
        
        if count > 5:
            lines.append(f"  ... i {count - 5} więcej")
        
        return "\n".join(lines)


# Singleton instances
text2sql = Text2SQL()
sql2text = SQL2Text()
