import pandas as pd
import numpy as np
from typing import List, Tuple, Union

class DataLoader:
    """
    Clase para cargar y preprocesar datos de producción (QGL y Qprod) 
    desde archivos CSV, soportando diferentes formatos.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    '''
    Método para cargar datos interfaz UI.
    Retorna (QGL_lists, Qprod_lists, Metadata_list).
    '''    
    def load_data_ui(self) -> Tuple[List[List[float]], List[List[float]], List[str]]:
        try:
            df_info = pd.read_csv(self.file_path, nrows=3, header=None)
            df_data = pd.read_csv(self.file_path, skiprows=4, header=None)
        except Exception as e:
            print(f"Error reading UI data from {self.file_path}: {e}")
            return [], [], []

        field_name = df_info.iloc[2, 0] 
        well_names = df_info.iloc[2, 1:].dropna().tolist() 
        column_labels_qgl = df_data.columns[1::2]
        column_label_prod = df_data.columns[2::2]
        list_of_wells_qgl = df_data.loc[:, column_labels_qgl].T.to_numpy().tolist()
        list_of_well_prods = df_data.loc[:, column_label_prod].T.to_numpy().tolist()
        list_of_wells_qgl = [[x for x in q_gl if not np.isnan(x)] for q_gl in list_of_wells_qgl]
        list_of_well_prods = [[x for x in q_oil if not np.isnan(x)] for q_oil in list_of_well_prods]
        return list_of_wells_qgl, list_of_well_prods, [field_name] + well_names

    '''
    Método para cargar datos desde un archivo CSV.
    Retorna (QGL_lists, Qprod_lists).
    '''    
    def load_data_csv(self) -> Tuple[List[List[float]], List[List[float]]]:
        try:
            df_data = pd.read_csv(self.file_path, skiprows=1, header=None)
        except Exception as e:
            print(f"Error reading CSV data from {self.file_path}: {e}")
            return [], []

        column_labels_qgl = df_data.columns[1::2]
        column_label_prod = df_data.columns[2::2]
        list_of_wells_qgl = df_data.loc[:, column_labels_qgl].T.to_numpy().tolist()
        list_of_well_prods = df_data.loc[:, column_label_prod].T.to_numpy().tolist()
        list_of_wells_qgl = [[x for x in q_gl if not np.isnan(x)] for q_gl in list_of_wells_qgl]
        list_of_well_prods = [[x for x in q_oil if not np.isnan(x)] for q_oil in list_of_well_prods]
        return list_of_wells_qgl, list_of_well_prods