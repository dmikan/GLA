import snowflake.connector
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class SnowflakeDB:
    """Handles direct Snowflake connection and operations"""
    
    def __init__(self) -> None:
        # Configuración principal (obligatoria desde variables de entorno)
        self.config: Dict[str, str] = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT").replace("https://", "").replace(".snowflakecomputing.com", ""),
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
            "role": os.getenv("SNOWFLAKE_ROLE"),
        }
        
        # Asignar cada valor del diccionario como atributo individual
        self.account = self.config["account"]
        self.user = self.config["user"]
        self.password = self.config["password"]
        self.database = self.config["database"]
        self.schema = self.config["schema"]
        self.warehouse = self.config["warehouse"]
        self.role = self.config["role"]
    
    def _get_connection(self):
        return snowflake.connector.connect(**self.config)
    
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
            conn.close()
    

if __name__ == "__main__":
    print("variables de entorno cargadas:", load_dotenv())