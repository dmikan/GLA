import streamlit as st
import numpy as np
from backend.services.optimization_constrained_pipeline_service import OptimizationConstrainedPipelineService
from backend.services.fitting_service import FittingService
from backend.services.optimization_global_pipeline_service import OptimizationGlobalPipelineService
from backend.services.data_loader_service import DataLoader
from backend.services.optimization_service import OptimizationService
from backend.services.well_result_service import WellResultService
from backend.models.database import SnowflakeDB
from components.optimization.optimization_constrained_results import OptimizationConstrainedResults
from components.optimization.optimization_global_results import OptimizationGlobalResults
from components.utils.style_utils import ChartStyle

class OptimizationChartsComponent:
    def __init__(self):
        self.constrained_results = OptimizationConstrainedResults()
        self.global_results = OptimizationGlobalResults()
        self.chart_style = ChartStyle()

    '''
    Método para mostrar la optimización global.
    Este método se encarga de mostrar la optimización global, incluyendo la configuración de precios y la curva de optimización global.
    Se encarga de mostrar la curva de optimización global y los resultados de la optimización.
    '''    
    def show_global_optimization(self, temp_path: str, db: SnowflakeDB):
        with st.expander("Configuración de Optimización", expanded=True):
            
            row1_col1, row1_col2 = st.columns(2)         
            with row1_col1:
                p_qoil = st.number_input(
                    "Precio del petróleo (USD/bbl)", 
                    min_value=0.1, 
                    max_value=None, 
                    value=70.0,
                    step=1.0,
                    key="p_qoil_global"
                )
            
            with row1_col2:
                p_qgl = st.number_input(
                    "Costo del gas (USD/Mscf)", 
                    min_value=0.1, 
                    max_value=None, 
                    value=300.0,
                    step=1.0,
                    key="p_qgl_global"
                )

            row2_col1, row2_col2 = st.columns(2)
                     
            with row2_col1:
                qgl_min = st.number_input(
                    "Límite mínimo de QGL en cada pozo (Mscf)", 
                    min_value=0, 
                    max_value=None, 
                    value=300,
                    step=100,
                    key="qgl_min_global"
                )        
        
        if st.button("Optimización Global"):    
            with st.spinner("Procesando datos..."):
                try:
                    loader = DataLoader(file_path=str(temp_path))
                    q_gl_list, q_oil_list, _ = loader.load_data()

                    fitting_service = FittingService(q_gl_list, q_oil_list)
                    fit = fitting_service.perform_fitting_group()
                    
                    optimization_service = OptimizationService(db)
                    optimization = optimization_service.get_latest()

                    st.subheader(f"Curva de Optimización Global: {optimization.plant_name}")
                    st.info("Calculando curva de optimización global...")

                    pipeline = OptimizationGlobalPipelineService(
                                                    q_gl_range=fit["qgl_range"],
                                                    y_pred_list=fit["y_pred_list"], 
                                                    qgl_min=qgl_min,
                                                    p_qoil=p_qoil,
                                                    p_qgl=p_qgl,
                                                    max_iterations=40,
                                                    max_qgl=20000)   
                    optimization_results = pipeline.run()
                    st.info("El QGL total se ha estabilizado. Terminanda optimización.")

                    self.global_results.show(optimization_results) 
                except Exception as e:
                    st.error(f"❌ Error durante la optimización: {str(e)}")
                    st.exception(e)
     
                          

    '''
    Método para mostrar la optimización restringida.
    Este método se encarga de mostrar la optimización restringida, incluyendo la configuración de precios y el límite de QGL.
    Se encarga de mostrar la optimización restringida y los resultados de la optimización.
    '''
    def show_constrained_optimization(self, temp_path: str, db: SnowflakeDB):
        with st.expander("Configuración de Optimización", expanded=True):
            
            # Primera fila con 2 columnas
            row1_col1, row1_col2 = st.columns(2)

            with row1_col1:
                qgl_limit = st.number_input(
                    "Límite total de QGL (Mscf)", 
                    min_value=0, 
                    max_value=None, 
                    value=1000,
                    step=100,
                    key="qgl_limit"
                )

            with row1_col2:
                qgl_min = st.number_input(
                    "Límite mínimo de QGL en cada pozo (Mscf)", 
                    min_value=0, 
                    max_value=None, 
                    value=300,
                    step=100,
                    key="qgl_min"
                )

            # Segunda fila con 2 columnas
            row2_col1, row2_col2 = st.columns(2)

            with row2_col1:
                p_qoil = st.number_input(
                    "Precio del petróleo (USD/bbl)", 
                    min_value=0.1, 
                    max_value=None, 
                    value=70.0,
                    step=1.0,
                    key="p_qoil"
                )
        
            with row2_col2:
                p_qgl = st.number_input(
                    "Costo del gas (USD/Mscf)", 
                    min_value=0.1, 
                    max_value=None, 
                    value=5.0,
                    step=0.5,
                    key="p_qgl"
                )

        if st.button("Ejecutar Optimización"):
            with st.spinner("Procesando datos..."):
                try:
                    loader = DataLoader(file_path=str(temp_path))
                    q_gl_list, q_oil_list, list_info = loader.load_data()

                    fitting_service = FittingService(q_gl_list, q_oil_list)
                    fit = fitting_service.perform_fitting_group()

                    pipeline = OptimizationConstrainedPipelineService(
                                                    csv_file_path=str(temp_path),
                                                    q_gl_range=fit['qgl_range'],
                                                    y_pred_list=fit["y_pred_list"],
                                                    plot_data=fit["plot_data"],
                                                    list_info=list_info,
                                                    qgl_limit=qgl_limit,
                                                    qgl_min=qgl_min,
                                                    p_qoil=p_qoil,
                                                    p_qgl=p_qgl,
                                                    db=db
                    )
                    optimization_results = pipeline.run()                  
                    st.success("¡Optimización completada!")

                    
                    well_result_service = WellResultService(db)
                    well_result = well_result_service.get_latest_well_results()   
                    
                    self.constrained_results.show(optimization_results, well_result)
                except Exception as e:
                    st.error(f"❌ Error durante la optimización: {str(e)}")
                    st.exception(e)


