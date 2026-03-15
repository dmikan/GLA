import snowflake.connector
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
# Import snowpark to detect if we are inside Snowflake
try:
    from snowflake.snowpark.context import get_active_session
except ImportError:
    # If snowpark is not installed locally, define a dummy function
    def get_active_session(): return None


load_dotenv()

class SnowflakeDB:
    """Handles direct Snowflake connection and operations (Hybrid: Local & Streamlit in Snowflake)"""
    
    def __init__(self) -> None:
        self.session = None
        self.is_snowflake_cloud = False
        self.config: Dict[str, str] = {}

        # ---------------------------------------------------------
        # TRY 1: Detect if we are INSIDE Snowflake (Streamlit)
        # ---------------------------------------------------------
        try:
            self.session = get_active_session()
            if self.session:
                self.is_snowflake_cloud = True # Flag to detect if we are inside Snowflake
        except Exception:
            pass

        # ---------------------------------------------------------
        # TRY 2: If we are NOT in the cloud, load local config
        # ---------------------------------------------------------
        if not self.is_snowflake_cloud:
            account = os.getenv("SNOWFLAKE_ACCOUNT")
            if not account:
                print("WARNING: No Snowflake session or environment variables detected.")
                return None

            self.config = {
                "account": account.replace("https://", "").replace(".snowflakecomputing.com", ""),
                "user": os.getenv("SNOWFLAKE_USER"),
                "password": os.getenv("SNOWFLAKE_PASSWORD"),
                "database": os.getenv("SNOWFLAKE_DATABASE"),
                "schema": os.getenv("SNOWFLAKE_SCHEMA"),
                "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
                "role": os.getenv("SNOWFLAKE_ROLE"),
            }
            
            # Assign attributes (only if we are in local)
            self.account = self.config["account"]
            self.user = self.config["user"]
            self.password = self.config["password"]
            self.database = self.config["database"]
            self.schema = self.config["schema"]
            self.warehouse = self.config["warehouse"]
            self.role = self.config["role"]
    
    def _get_connection(self):
        """Get a new connection to Snowflake (Smart switch)"""
        if self.is_snowflake_cloud and self.session:
            return self.session.connection
        if self.config:
            return snowflake.connector.connect(**self.config)
        raise ValueError("Could not establish connection (neither active session nor local credentials found)")


    def execute_query(self, query: str, params: tuple = None):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return result
            return []

        except Exception as e:
            print(f"Error executing query: {query} with params {params}")
            raise
        finally:
            # IMPORTANT: If it is a local connection, we close everything.
            # If it is a Snowflake session, we only close the cursor, not the global connection.
            if hasattr(cursor, 'close'):
                cursor.close()
            if not self.is_snowflake_cloud and hasattr(conn, 'close'):
                conn.close()
