import streamlit as st
import pandas as pd
from io import StringIO

class CSVInputComponent:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
        self.csv_uploaded_by_user = None # to store csv file supplied by user

    def _show_csv_loader_widget(self):
        self.csv_uploaded_by_user = st.file_uploader("Upload csv file with production data", type="csv")

    def load(self):
        self._show_csv_loader_widget()
        # Create csv in the specified temp_dir
        if self.csv_uploaded_by_user is not None:
            content = self.csv_uploaded_by_user.getvalue()
            tmp_path = self.tmp_dir / f"data_csv_file.csv"
            with open(tmp_path, "wb") as f:
                f.write(content)
            if tmp_path is not None and tmp_path:
                st.session_state.data_load_mode = "csv_upload"
                st.session_state.temp_path = tmp_path
                st.session_state.uploaded_file = self.csv_uploaded_by_user
                #st.write(st.session_state.uploaded_file)
