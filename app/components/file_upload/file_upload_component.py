import streamlit as st
from pathlib import Path
import pandas as pd
from io import StringIO
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
    Método para guardar el archivo CSV subido por el usuario.
    Este método se encarga de guardar el archivo CSV subido por el usuario en un directorio temporal y cargar los datos en un DataFrame de pandas.
    Se encarga de decodificar el contenido del archivo, leerlo como un DataFrame y guardar el DataFrame en la sesión de Streamlit.
    '''        
    def _save_uploaded_file(self, uploaded_file, upload_dir):
        content = uploaded_file.getvalue()
        csv_str = content.decode("utf-8") 
        df = pd.read_csv(StringIO(csv_str))
        nombre_planta = df.iloc[1, 0] if len(df) > 1 else "uploaded_data"
        
        temp_path = upload_dir / f"data_{nombre_planta}.csv"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        st.session_state.uploaded_file = df
        st.session_state.temp_path = temp_path
        return df, temp_path
    
    '''
    Método para manejar la entrada manual de datos.
    Este método se encarga de mostrar el componente de entrada manual y guardar los datos ingresados en un archivo CSV temporal.
    Se encarga de mostrar un botón para subir los datos y guardar el DataFrame en la sesión de Streamlit.
    '''
    def _handle_manual_input(self, upload_dir):
        manual_data = self.manual_input.show()
        if manual_data is not None:
            df = manual_data
            nombre_planta = df.iloc[2, 0] if len(df) > 1 else "manual_data"
            
            temp_path = upload_dir / f"data_{nombre_planta}.csv"
            
            if st.button("Upload data"):
                try:
                    df.to_csv(temp_path, index=False, header=False)
                    st.success(f"Datos guardados exitosamente en {temp_path}")
                    st.session_state.uploaded_file = df
                    st.session_state.temp_path = temp_path
                except Exception as e:
                    st.error(f"Error al guardar los datos: {e}")
        return None, None
    

    '''
    Método para manejar la carga de datos desde el simulador Prosper.
    Este método se encarga de cargar los datos desde un archivo CSV específico y guardarlos en un DataFrame de pandas.
    Se encarga de guardar el DataFrame en la sesión de Streamlit y mostrar un mensaje de éxito.
    '''
    def _handle_prosper_data(self, upload_dir):
        available_fields = ["Prosper_data"]
        selected_field = st.selectbox("Seleccione la planta de petróleo", available_fields)
        
        if selected_field and st.button(f"Traer datos desde simulador"):
            try:
                field_file = 'C:/Users/djper/Documents/Repositories/GLTB/data/data_field101.csv'
                df = pd.read_csv(field_file)
                
                field_name = selected_field.lower().replace(" ", "_")
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


    '''
    Método para mostrar el componente de carga de archivos.
    Este método se encarga de mostrar el componente de carga de archivos y manejar la lógica de carga de datos.
    Se encarga de mostrar las opciones de carga de datos y manejar la entrada del usuario.
    Se encarga de llamar a los métodos de carga de datos y devolver el DataFrame cargado.
    '''
    def show(self):
        self._init_session_state()
        option = st.radio(
            "Seleccione el método de carga de datos:",
            options=["Subir archivo CSV", "Ingreso manual", "Generar desde Prosper"],
            horizontal=True
        )
        
        project_root = Path(__file__).parent.parent.parent.parent
        upload_dir = project_root / "static" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        if option == "Subir archivo CSV":
            uploaded_file = st.file_uploader("Sube tu archivo CSV con datos de producción", type="csv")
            if uploaded_file is not None:
                return self._save_uploaded_file(uploaded_file, upload_dir)[1]
        elif option == "Ingreso manual":
            self._handle_manual_input(upload_dir)
        elif option == "Generar desde Prosper":
            self._handle_prosper_data(upload_dir)
        
        return st.session_state.temp_path