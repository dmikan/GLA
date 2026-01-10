import streamlit as st
import pandas as pd
from app.components.utils.plotter import Plotter

class DisplayGlobalResults:
    def __init__(self, optimization_results: dict):
        self.plotter = None
        self.optimization_results = optimization_results

    def show(self):

        self._show_summary_metrics()

        self.plotter = Plotter(self.optimization_results)
        fig = self.plotter.create_global_curve()
        st.plotly_chart(fig, use_container_width=True)


    def _show_summary_metrics(self):
        col1, col2 = st.columns(2)
        summary: list = self.optimization_results['summary']
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
