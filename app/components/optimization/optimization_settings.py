import streamlit as st
import numpy as np
from typing import List, Tuple
from backend.services.optimization_constrained_pipeline_service import OptimizationConstrainedPipelineService
from backend.services.fitting_service import FittingService
from backend.services.optimization_global_pipeline_service import OptimizationGlobalPipelineService
from backend.services.optimization_service import OptimizationService
from backend.services.well_result_service import WellResultService
from backend.models.database import SnowflakeDB
from app.components.optimization.display_constrained_results import DisplayConstrainedResults
from app.components.optimization.display_global_results import DisplayGlobalResults
from app.components.utils.plotter import Plotter


class OptimizationSettingsComponent:
    def __init__(self, db: SnowflakeDB):
        self.db = db
        self.qgl_min_global = 300
        self.p_qoil_global = 70.0
        self.p_qgl_global = 300.0
        self.qgl_limit_constrained = 1000
        self.qgl_min_constrained = 300
        self.p_qoil_constrained = 70.0
        self.p_qgl_constrained = 300.0

    '''
    Method to show the global optimization.
    Now receives the pre-processed data as a tuple: (QGL_lists, Qprod_lists, Metadata_list).
    '''
    def show_global_settings(self):

        with st.expander("Global Optimization Configuration", expanded=True):

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                self.p_qoil_global = st.number_input(
                    "Oil price (USD/bbl)",
                    min_value=0.1,
                    max_value=None,
                    value=70.0,
                    step=1.0,
                    key="p_qoil_global"
                )

            with row1_col2:
                self.p_qgl_global = st.number_input(
                    "Gas cost (USD/Mscf)",
                    min_value=0.1,
                    max_value=None,
                    value=300.0,
                    step=1.0,
                    key="p_qgl_global"
                )

            row2_col1, row2_col2 = st.columns(2)

            with row2_col1:
                self.qgl_min_global = st.number_input(
                    "Minimum QGL limit (Mscf)",
                    min_value=0,
                    max_value=None,
                    value=300,
                    step=100,
                    key="qgl_min_global"
                )

    def run_global_optimization(self, loaded_data):

        q_gl_list, q_fluid_list, wct_list, list_info = loaded_data

        if not q_gl_list:
             st.warning("No valid data loaded to execute global optimization.")
             return

        if st.button("Global Optimization"):
            with st.spinner("Processing data..."):
                try:

                    fitting_service = FittingService(q_gl_list, q_fluid_list, wct_list)
                    fit = fitting_service.perform_fitting_group()

                    optimization_service = OptimizationService(self.db)
                    plant_name = list_info[0] if list_info else "Unknown Plant"
                    optimization = optimization_service.get_latest()

                    st.subheader(f"Global optimization curve: {plant_name}")
                    st.info("Calculating global optimization curve...")

                    pipeline = OptimizationGlobalPipelineService(
                                                         q_gl_common_range=fit["q_gl_common_range"],
                                                         q_oil_rates_list=fit["q_oil_rates_list"],
                                                         qgl_min=self.qgl_min_global,
                                                         p_qoil=self.p_qoil_global,
                                                         p_qgl=self.p_qgl_global,
                                                         max_iterations=40,
                                                         max_qgl=20000)
                    optimization_results = pipeline.run()
                    st.info("Total QGL has stabilized. Finalizing global optimization.")

                    display_global_results = DisplayGlobalResults(optimization_results)
                    display_global_results.show()
                except Exception as e:
                    st.error(f"❌ Error during global optimization: {str(e)}")
                    st.exception(e)


    '''
    Method to show the constrained optimization.
    Now receives the pre-processed data as a tuple: (QGL_lists, Qprod_lists, Metadata_list).
    '''
    def show_constrained_settings(self):

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

    def run_constrained_optimization(self, loaded_data):
        q_gl_list, q_fluid_list, wct_list, list_info = loaded_data

        if not q_gl_list:
             st.warning("There are no valid data loaded to execute the constrained optimization.")
             return


        if st.button("Execute Constrained Optimization"):
            with st.spinner("Processing data..."):
                try:
                    fitting_service = FittingService(q_gl_list, q_fluid_list, wct_list)
                    fit = fitting_service.perform_fitting_group()

                    pipeline = OptimizationConstrainedPipelineService(
                                                         q_gl_common_range=fit['q_gl_common_range'],
                                                         q_oil_rates_list=fit["oil_rates_list"],
                                                         plot_data=fit["plot_data"],
                                                         list_info=list_info,
                                                         qgl_limit=self.qgl_limit_constrained,
                                                         qgl_min=self.qgl_min_constrained,
                                                         p_qoil=self.p_qoil_constrained,
                                                         p_qgl=self.p_qgl_constrained,
                                                         db=self.db
                    )
                    optimization_results = pipeline.run()
                    st.success("Constrained optimization completed!")


                    well_result_service = WellResultService(self.db)
                    well_results = well_result_service.get_latest_well_results()

                    display_constrained_results = DisplayConstrainedResults(optimization_results, well_results)
                    display_constrained_results.show()
                except Exception as e:
                    st.error(f"❌ Error during constrained optimization: {str(e)}")
                    st.exception(e)
