import streamlit as st
from backend.entities.database import SnowflakeDB
from app.components.optimization.display_constrained_results import DisplayConstrainedResults
from app.components.optimization.display_global_results import DisplayGlobalResults


class OptimizationSettingsComponent:
    def __init__(self):
        self.qgl_min_global = 300
        self.p_qoil_global = 70.0
        self.p_qgl_global = 300.0
        self.qgl_limit_constrained = 1000
        self.qgl_min_constrained = 300
        self.p_qoil_constrained = 70.0
        self.p_qgl_constrained = 300.0
        self.SESSION_KEY_GLOBAL = "global_optimization_results"
        self.SESSION_KEY_CONSTR = "constrained_optimization_results"
        self.SESSION_KEY_WELL = "well_results"

    '''
    Method to show the global optimization.
    Now receives the pre-processed data as a tuple: (QGL_lists, Qprod_lists, Metadata_list).
    '''
    def choose_global_settings(self):
        
        with st.expander("Global Optimization Configuration", expanded=True):

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                self.p_qoil_global = st.number_input(
                    "Oil price (USD/bbl)",
                    min_value=0.1,
                    max_value=None,
                    value=100.0,
                    step=1.0,
                    key="p_qoil_global"
                )

            with row1_col2:
                self.p_qgl_global = st.number_input(
                    "Gas cost (USD/Mscf)",
                    min_value=0.1,
                    max_value=None,
                    value=1.0,
                    step=1.0,
                    key="p_qgl_global"
                )

            row2_col1, row2_col2 = st.columns(2)

            with row2_col1:
                self.qgl_min_global = st.number_input(
                    "Minimum QGL limit (Mscf)",
                    min_value=0.1,
                    max_value=None,
                    value=1.0,
                    step=1.0,
                    key="qgl_min_global"
                )

        return dict(
            p_qoil_global=self.p_qoil_global,
            p_qgl_global=self.p_qgl_global,
            qgl_min_global=self.qgl_min_global
        )

    '''
    Method to show the constrained optimization.
    Now receives the pre-processed data as a tuple: (QGL_lists, Qprod_lists, Metadata_list).
    '''
    def choose_constrained_settings(self):

        with st.expander("Configuration of Optimization", expanded=True):

            # First row with 2 columns
            row1_col1, row1_col2 = st.columns(2)

            with row1_col1:
                self.qgl_limit_constrained = st.number_input(
                    "Total QGL limit (Mscf)",
                    min_value=0,
                    max_value=None,
                    value=1000,
                    step=100,
                    key="qgl_limit"
                )

            with row1_col2:
                self.qgl_min_constrained = st.number_input(
                    "Minimum QGL limit (Mscf)",
                    min_value=0.1,
                    max_value=None,
                    value=1.0,
                    step=1.0,
                    key="qgl_min"
                )

            # Segunda fila con 2 columnas
            row2_col1, row2_col2 = st.columns(2)

            with row2_col1:
                self.p_qoil_constrained = st.number_input(
                    "Oil price (USD/bbl)",
                    min_value=0.1,
                    max_value=None,
                    value=100.0,
                    step=1.0,
                    key="p_qoil"
                )

            with row2_col2:
                self.p_qgl_constrained = st.number_input(
                    "Gas price (USD/Mscf)",
                    min_value=0.1,
                    max_value=None,
                    value=1.0,
                    step=1.0,
                    key="p_qgl"
                )

        return dict(
            qgl_limit_constrained=self.qgl_limit_constrained,
            qgl_min_constrained=self.qgl_min_constrained,
            p_qoil_constrained=self.p_qoil_constrained,
            p_qgl_constrained=self.p_qgl_constrained
        )
