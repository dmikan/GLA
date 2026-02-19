import streamlit as st
from pathlib import Path
import pandas as pd
from io import StringIO
import os
from app.components.file_upload.manual_input_component import ManualInputComponent
from app.components.file_upload.csv_input_component import CSVInputComponent
from app.components.file_upload.prosper_input_component import ProsperInputComponent

class FileUploadComponent:

    def show(self):
        self._init_session_state()
        tmp_dir = self._get_tmp_dir() # folder to store csv
        option = self._choose_data_loading_method()

        #st.session_state.data_load_mode = None
        #st.session_state.temp_path = None

        if option == "Upload csv":
            csv_input = CSVInputComponent(tmp_dir)
            csv_input.load()
        elif option == "Manual input":
            manual_input = ManualInputComponent(tmp_dir)
            manual_input.load()
        elif option == "From Prosper":
            proper_input = ProsperInputComponent(tmp_dir)
            proper_input.load()
        return st.session_state.temp_path, st.session_state.data_load_mode


    def _init_session_state(self):
        # create session variables
        if 'uploaded_file' not in st.session_state:
            st.session_state.uploaded_file = None
        if 'temp_path' not in st.session_state:
            st.session_state.temp_path = None
        if 'data_load_mode' not in st.session_state:
            st.session_state.data_load_mode = None


    def _get_tmp_dir(self):
        '''
        Evaluate where the program is running: on SNF or on PC.
        Either way, it returns the tmp path to store the csv file
        '''
        is_snowflake = os.path.exists("/home/udf") # evaluate execution on SNF
        if is_snowflake:
            return Path("/tmp") # tmp in SNF, where the project is stored
        else:
            # when executing on pc
            project_root = Path(__file__).parent.parent.parent.parent
            local_path = project_root / "tmp"
            local_path.mkdir(parents=True, exist_ok=True)
            return local_path

    def _choose_data_loading_method(self):
        '''
        Display data loading method options
        '''
        option = st.radio(
            "Choose a data loading method:",
            options=["Upload csv", "Manual input", "From Prosper"],
            horizontal=True
        )
        return option


if  __name__== "__main__":

    var1 = Path(__file__).parent.parent.parent.parent
    print(var1)
