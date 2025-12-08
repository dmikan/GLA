import streamlit as st
import pandas as pd
from app.components.utils.plotter import Plotter
from app.styles.custom_styles import inject_global_css

class DisplayConstrainedResults:
    def __init__(self, optimization_results, well_results):
        self.plotter = None
        self.optimization_results = optimization_results
        self.well_results = well_results


    '''
    Method to display the optimization results.
    This method is responsible for displaying the optimization results, including summary metrics and well curves.
    '''
    def show(self):
        inject_global_css()

        st.markdown("---")
        st.subheader("Summary Metrics")
        self._show_summary_metrics()
        st.markdown("---")
        st.subheader("Production Curves")
        self._plot_well_curves()
        st.markdown("---")
        st.subheader("Detailed Results by Well")
        self._show_well_results_table()

    '''
    Method to display the summary metrics of the optimization.
    This method is responsible for displaying the summary metrics of the optimization, including total production, total QGL used, and the configured QGL limit.
    It displays the metrics in columns for better visualization.
    '''
    
    def _show_summary_metrics(self):
        col1, col2, col3 = st.columns(3)
        summary = self.optimization_results['summary']
        used_percentage = (summary['total_qgl'] / summary['qgl_limit']) * 100

        # Card 1: Total Production
        with col1:
            html = f"""
            <div class="metric-card">
                <div class="metric-title">Total Production</div>
                <div class="metric-value">{summary['total_production']:.2f} <span class="metric-unit">bbl</span></div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

        # Card 2: Total QGL Used (with status tag)
        with col2:
            html = f"""
            <div class="metric-card">
                <div class="metric-title">Total QGL Used</div>
                <div class="metric-value">{summary['total_qgl']:.2f} <span class="metric-unit">Mscf</span></div>
                <div class="status-tag">{used_percentage:.1f}% of the limit</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

        # Card 3: Configured QGL Limit
        with col3:
            html = f"""
            <div class="metric-card">
                <div class="metric-title">Configured QGL Limit</div>
                <div class="metric-value">{summary['qgl_limit']:.2f} <span class="metric-unit">Mscf</span></div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)




    def _plot_well_curves(self):
        if not self.optimization_results.get('plot_data') or not self.well_results:
            st.warning("No data available to plot")
            return
        self.plotter = Plotter(self.optimization_results)
        fig_prod = self.plotter.create_well_curves(self.well_results)
        st.plotly_chart(fig_prod, use_container_width=True)




    def _show_well_results_table(self):
        if not self.well_results:
            st.warning("No well data available to display")
            return
        try:
            well_data = [{
                "Well": getattr(result, 'well_name', 'N/A'),
                "Production": getattr(result, 'optimal_production', 0),
                "QGL": getattr(result, 'optimal_gas_injection', 0)
            } for result in self.well_results]

            df = pd.DataFrame(well_data)

            if "Well" not in df.columns:
                df = df.rename(columns={"well_name": "Well"})

            st.dataframe(df.set_index("Well").style.format({
                "Production": "{:.2f}",
                "QGL": "{:.2f}"
            }))

        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")
            st.write("Data received:", self.well_results)
