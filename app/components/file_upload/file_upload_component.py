import streamlit as st
from pathlib import Path
import pandas as pd
from io import StringIO
import os
from app.components.file_upload.manual_input_component import ManualInputComponent

class FileUploadComponent:
    def __init__(self):
        self.manual_input = ManualInputComponent()
        self._init_session_state()

    def _init_session_state(self):
        if 'uploaded_file' not in st.session_state:
            st.session_state.uploaded_file = None
        if 'temp_path' not in st.session_state:
            st.session_state.temp_path = None

    '''
    NUEVO MÉTODO: Determina el directorio de destino según el entorno.
    - En Snowflake: Retorna Path("/tmp") (único lugar escribible).
    - En Local: Retorna static/uploads (para mantener orden).
    '''
    def _get_upload_dir(self):
        # Detectamos si estamos en Snowflake buscando la carpeta típica de usuario UDF
        is_snowflake = os.path.exists("/home/udf")
        
        if is_snowflake:
            return Path("/tmp")
        else:
            # Lógica local original
            project_root = Path(__file__).parent.parent.parent.parent
            local_path = project_root / "static" / "uploads"
            local_path.mkdir(parents=True, exist_ok=True)
            return local_path

    def _save_uploaded_file(self, uploaded_file, upload_dir):
        content = uploaded_file.getvalue()
        # Intentamos decodificar, si falla usa latin-1 por seguridad
        try:
            csv_str = content.decode("utf-8")
        except UnicodeDecodeError:
            csv_str = content.decode("latin-1")
            
        df = pd.read_csv(StringIO(csv_str))
        nombre_planta = df.iloc[1, 0] if len(df) > 1 else "uploaded_data"
        
        # Limpiamos el nombre del archivo para evitar caracteres raros
        safe_name = "".join([c for c in str(nombre_planta) if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
        
        temp_path = upload_dir / f"data_{safe_name}.csv"
        
        # Guardamos usando el path determinado (sea /tmp o static)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        st.session_state.uploaded_file = df
        st.session_state.temp_path = temp_path
        return df, temp_path
    
    def _handle_manual_input(self, upload_dir):
        manual_data = self.manual_input.show()
        if manual_data is not None:
            df = manual_data
            nombre_planta = df.iloc[2, 0] if len(df) > 1 else "manual_data"
            safe_name = "".join([c for c in str(nombre_planta) if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
            
            temp_path = upload_dir / f"data_{safe_name}.csv"
            
            if st.button("Upload data"):
                try:
                    df.to_csv(temp_path, index=False, header=False)
                    # Mensaje discreto dependiendo del entorno
                    if "/tmp" in str(temp_path):
                        st.success(f"Datos procesados correctamente.")
                    else:
                        st.success(f"Datos guardados en {temp_path}")
                        
                    st.session_state.uploaded_file = df
                    st.session_state.temp_path = temp_path
                except Exception as e:
                    st.error(f"Error al guardar los datos: {e}")
        return None, None
    

    '''
    CORREGIDO: Ruta relativa para funcionar en GitHub/Snowflake y Local
    '''
    def _handle_prosper_data(self, upload_dir):
        available_fields = ["Prosper_data"]
        selected_field = st.selectbox("Seleccione la planta de petróleo", available_fields)
        
        if selected_field and st.button(f"Traer datos desde simulador"):
            try:
                # 1. Definimos la ruta de origen de forma RELATIVA
                # Buscamos la carpeta 'data' en la raíz del proyecto
                project_root = Path(__file__).parent.parent.parent.parent
                source_path = project_root / 'data' / 'data_field101.csv'
                
                if not source_path.exists():
                    st.error(f"No se encuentra el archivo fuente en el repositorio: data/data_field101.csv")
                    return None, None

                df = pd.read_csv(source_path)
                
                field_name = selected_field.lower().replace(" ", "_")
                # 2. Guardamos en el directorio de destino (que puede ser /tmp)
                temp_path = upload_dir / f"data_{field_name}.csv"
                df.to_csv(temp_path, index=False)
                
                st.session_state.uploaded_file = df
                st.session_state.temp_path = temp_path
                st.session_state.current_data_source = 'prosper'
                st.success("Datos cargados correctamente desde simulador.")
                return df, temp_path
            except Exception as e:
                st.error(f"Error: {e}")
        return None, None

    def show(self):
        self._init_session_state()
        
        # Obtenemos el directorio correcto AUTOMÁTICAMENTE
        upload_dir = self._get_upload_dir()
        
        option = st.radio(
            "Seleccione el método de carga de datos:",
            options=["Subir archivo CSV", "Ingreso manual", "Generar desde Prosper"],
            horizontal=True
        )

        if option == "Subir archivo CSV":
            uploaded_file = st.file_uploader("Sube tu archivo CSV con datos de producción", type="csv")
            if uploaded_file is not None:
                return self._save_uploaded_file(uploaded_file, upload_dir)[1]
                
        elif option == "Ingreso manual":
            self._handle_manual_input(upload_dir)
            
        elif option == "Generar desde Prosper":
            self._handle_prosper_data(upload_dir)
        
        return st.session_state.temp_path