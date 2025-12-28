import streamlit as st
from backend.entities.database import SnowflakeDB
from backend.services.field_optimization_service import FieldOptimizationService
from backend.services.optimization_global_pipeline_service import OptimizationGlobalPipelineService
from backend.services.optimization_constrained_pipeline_service import OptimizationConstrainedPipelineService
from app.components.optimization.display_global_results import DisplayGlobalResults
from app.components.optimization.display_constrained_results import DisplayConstrainedResults
from backend.services.fitting_service import FittingService
from backend.services.well_optimization_service import WellOptimizationService
from backend.repositories.field_optimization_repository import FieldOptimizationRepository
from backend.repositories.well_optimization_repository import WellOptimizationRepository

class OptimizationExecutionComponent:
    def __init__(self, db: SnowflakeDB):
        self.db = db
        self.SESSION_KEY_GLOBAL = "global_optimization_results"
        self.SESSION_KEY_CONSTR = "constrained_optimization_results"
        self.SESSION_KEY_WELL = "well_results"


    def run_global_optimization(self, loaded_data, global_settings):
        q_gl_list, q_fluid_list, wct_list, list_info = loaded_data

        if not q_gl_list:
            st.warning("No valid data loaded to execute global optimization.")
            return

        just_calculated = False
        if st.button("Global Optimization"):
            with st.spinner("Processing data..."):
                try:
                    
                    fitting_service = FittingService(q_gl_list, q_fluid_list, wct_list)
                    fit = fitting_service.perform_fitting_group()

                    field_optimization_repository = FieldOptimizationRepository(self.db)
                    field_optimization_service = FieldOptimizationService(field_optimization_repository)
                    plant_name = list_info[0] if list_info else "Unknown Plant"
                    optimization = field_optimization_service.get_latest_field_optimization()

                    st.subheader(f"Global optimization curve: {plant_name}")
                    st.info("Calculating global optimization curve...")

                    pipeline = OptimizationGlobalPipelineService(
                                                                q_gl_common_range=fit["q_gl_common_range"],
                                                                q_oil_rates_list=fit["q_oil_rates_list"],
                                                                qgl_min=global_settings['qgl_min_global'],
                                                                p_qoil=global_settings['p_qoil_global'],
                                                                p_qgl=global_settings['p_qgl_global'],
                                                                max_iterations=40,
                                                                max_qgl=20000)
                    optimization_results = pipeline.run()
                    
                    # Save GLOBAL results in session_state
                    st.session_state[self.SESSION_KEY_GLOBAL] = optimization_results
                    
                    st.info("Total QGL has stabilized. Finalizing global optimization.")

                    display_global_results = DisplayGlobalResults(optimization_results)
                    display_global_results.show() 
                    just_calculated = True	

                except Exception as e:
                    st.error(f"❌ Error during global optimization: {str(e)}")
                    st.exception(e)
        
        if not just_calculated and self.SESSION_KEY_GLOBAL in st.session_state:
            optimization_results = st.session_state[self.SESSION_KEY_GLOBAL]
            display_global_results = DisplayGlobalResults(optimization_results)
            display_global_results.show()




    def run_constrained_optimization(self, loaded_data, constrained_settings):
        q_gl_list, q_fluid_list, wct_list, list_info = loaded_data

        if not q_gl_list:
            st.warning("There are no valid data loaded to execute the constrained optimization.")
            return

        just_calculated = False
        if st.button("Execute Constrained Optimization"):
            with st.spinner("Processing data..."):
                try:
                    fitting_service = FittingService(q_gl_list, q_fluid_list, wct_list)
                    fit = fitting_service.perform_fitting_group()

                    pipeline = OptimizationConstrainedPipelineService(
                                                                    q_gl_common_range=fit['q_gl_common_range'],
                                                                    q_oil_rates_list=fit["q_oil_rates_list"],
                                                                    plot_data=fit["plot_data"],
                                                                    list_info=list_info,
                                                                    qgl_limit=constrained_settings['qgl_limit_constrained'],
                                                                    qgl_min=constrained_settings['qgl_min_constrained'],
                                                                    p_qoil=constrained_settings['p_qoil_constrained'],
                                                                    p_qgl=constrained_settings['p_qgl_constrained'],
                                                                    db=self.db
                                    )
                    optimization_results = pipeline.run()
                    
                    # Save CONSTR results in session_state
                    st.session_state[self.SESSION_KEY_CONSTR] = optimization_results
                    
                    st.success("Constrained optimization completed!")

                    well_optimization_repository = WellOptimizationRepository(self.db)
                    well_optimization_service = WellOptimizationService(well_optimization_repository)
                    well_results = well_optimization_service.get_latest_well_optimizations()
                    
                    # Save WELL results in session_state
                    st.session_state[self.SESSION_KEY_WELL] = well_results

                    display_constrained_results = DisplayConstrainedResults(optimization_results, well_results)
                    display_constrained_results.show()
                    just_calculated = True

                except Exception as e:
                    st.error(f"❌ Error during constrained optimization: {str(e)}")
                    st.exception(e)

        # Logic to show saved CONSTR results
        if not just_calculated and self.SESSION_KEY_CONSTR in st.session_state and self.SESSION_KEY_WELL in st.session_state:
            optimization_results = st.session_state[self.SESSION_KEY_CONSTR]
            well_results = st.session_state[self.SESSION_KEY_WELL]
            display_constrained_results = DisplayConstrainedResults(optimization_results, well_results)
            display_constrained_results.show()