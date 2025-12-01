import snowflake.connector
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv

# Importamos esto para detectar si estamos dentro de Snowflake
try:
    from snowflake.snowpark.context import get_active_session
except ImportError:
    # Si no tienes snowpark instalado en local, definimos una función dummy
    def get_active_session(): return None

load_dotenv()

class SnowflakeDB:
    """Handles direct Snowflake connection and operations (Hybrid: Local & Streamlit in Snowflake)"""
    
    def __init__(self) -> None:
        self.session = None
        self.is_snowflake_cloud = False
        self.config: Dict[str, str] = {}

        # ---------------------------------------------------------
        # INTENTO 1: Detectar si estamos DENTRO de Snowflake (Streamlit)
        # ---------------------------------------------------------
        try:
            self.session = get_active_session()
            if self.session:
                self.is_snowflake_cloud = True
                # print("DEBUG: Detectado entorno Snowflake Nativo.")
        except Exception:
            pass

        # ---------------------------------------------------------
        # INTENTO 2: Si NO estamos en la nube, cargamos config Local
        # ---------------------------------------------------------
        if not self.is_snowflake_cloud:
            # print("DEBUG: Detectado entorno Local. Cargando variables de entorno.")
            
            # Validación preventiva para evitar el error 'NoneType has no attribute replace'
            account = os.getenv("SNOWFLAKE_ACCOUNT")
            if not account:
                # Si estamos aquí, no hay sesión activa Y no hay variables de entorno.
                # Esto pasaba antes y causaba el crash. Ahora lo manejamos suavemente.
                print("ADVERTENCIA: No se detectó sesión de Snowflake ni variables de entorno.")
                return

            self.config = {
                "account": account.replace("https://", "").replace(".snowflakecomputing.com", ""),
                "user": os.getenv("SNOWFLAKE_USER"),
                "password": os.getenv("SNOWFLAKE_PASSWORD"),
                "database": os.getenv("SNOWFLAKE_DATABASE"),
                "schema": os.getenv("SNOWFLAKE_SCHEMA"),
                "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
                "role": os.getenv("SNOWFLAKE_ROLE"),
            }
            
            # Asignar atributos (solo si estamos en local)
            self.account = self.config["account"]
            self.user = self.config["user"]
            self.password = self.config["password"]
            self.database = self.config["database"]
            self.schema = self.config["schema"]
            self.warehouse = self.config["warehouse"]
            self.role = self.config["role"]
    
    def get_connection(self):
        """Get a new connection to Snowflake (Smart switch)"""
        
        # CASO A: Estamos en Snowflake (Streamlit in Snowflake)
        if self.is_snowflake_cloud and self.session:
            return self.session.connection
            
        # CASO B: Estamos en Local
        if self.config:
            return snowflake.connector.connect(**self.config)
            
        raise ValueError("No se pudo establecer conexión (ni Session activa ni credenciales locales encontradas)")
    
    def execute(self, query: str, params: tuple = None, return_last_id: bool = False):
        """Versión mejorada con logging"""
        conn = self.get_connection()
        
        # En Snowflake nativo, 'conn' ya es una conexión abierta. 
        # En local, es un objeto nuevo.
        # No cerramos la conexión si viene de la sesión activa de Snowflake (para no matar la app),
        # pero sí cerramos el cursor.
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            # Debug: Ver estructura de resultados
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return result
            
            return []
        except Exception as e:
            print(f"Error executing query: {query} with params {params}")
            raise
        finally:
            # IMPORTANTE: Si es conexión local, cerramos todo.
            # Si es sesión de Snowflake, solo cerramos el cursor, no la conexión global.
            if hasattr(cursor, 'close'):
                cursor.close()
            if not self.is_snowflake_cloud and hasattr(conn, 'close'):
                conn.close()

if __name__ == "__main__":
    db = SnowflakeDB()
    print(f"Iniciado correctamente. Modo Cloud: {db.is_snowflake_cloud}")