import streamlit as st
import pandas as pd
from app.components.utils.style_utils import ChartStyle

class DisplayConstrainedResults:
    def __init__(self):
        self.chart_style = ChartStyle()


    '''
    Method to display the optimization results.
    This method is responsible for displaying the optimization results, including summary metrics and well curves.
    '''
    def show(self, optimization_results, well_result):
        self._show_summary_metrics(optimization_results['summary'])
        st.markdown("---")
        self._plot_well_curves(optimization_results, well_result)
        st.subheader("Detailed Results by Well")
        self._show_well_results_table(well_result)

    '''
    Method to display the summary metrics of the optimization.
    This method is responsible for displaying the summary metrics of the optimization, including total production, total QGL used, and the configured QGL limit.
    It displays the metrics in columns for better visualization.
    '''

    def _show_summary_metrics(self, summary):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Production",
                f"{summary['total_production']:.2f} bbl"
            )

        with col2:
            st.metric(
                "Total QGL Used",
                f"{summary['total_qgl']:.2f} Mscf",
                delta=f"{(summary['total_qgl']/summary['qgl_limit']*100):.1f}% of the limit"
            )

        with col3:
            st.metric(
                "Configured QGL Limit",
                f"{summary['qgl_limit']:.2f} Mscf"
            )


    def _plot_well_curves(self, optimization_results, well_result):
        if not optimization_results.get('plot_data') or not well_result:
            st.warning("No data available to plot")
            return

        fig_prod = self.chart_style.create_well_curves_chart(optimization_results, well_result)
        st.plotly_chart(fig_prod, use_container_width=True)



    def _show_well_results_table(self, well_result):
        if not well_result:
            st.warning("No well data available to display")
            return

        try:
            well_data = [{
                "Well": getattr(result, 'well_name', 'N/A'),
                "Production": getattr(result, 'optimal_production', 0),
                "QGL": getattr(result, 'optimal_gas_injection', 0)
            } for result in well_result]

            df = pd.DataFrame(well_data)

            if "Well" not in df.columns:
                df = df.rename(columns={"well_name": "Well"})

            st.dataframe(df.set_index("Well").style.format({
                "Production": "{:.2f}",
                "QGL": "{:.2f}"
            }))

        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")
            st.write("Data received:", well_result)
