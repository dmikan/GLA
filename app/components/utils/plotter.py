import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from math import ceil

class Plotter:
    def __init__(self, optimization_results: dict):
        self.bg_color = "#0E1117"
        self.grid_color = "#37474F"
        self.text_color = "#FFFFFF"
        self.line_color = "#00E676"
        self.marker_color = "#C8E6C9"
        self.optimal_line_color = "#FF5252"
        self.last_value_line_color = "#FF1744"
        self.fluid_line_color = "#E0970E"
        self.optimization_results = optimization_results

    '''
    Method to create a global optimization chart.
    This method is responsible for creating a global optimization chart using Plotly.
    It creates a line chart with markers for total production and a horizontal line for the last production value.
    '''
    def create_global_curve(self):
        last_production = self.optimization_results["total_production"][-1] if self.optimization_results["total_production"] else 0

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=self.optimization_results["total_qgl"],
                y=self.optimization_results["total_production"],
                mode='lines+markers',
                name='Total Production',
                line=dict(width=3, color=self.line_color),
                marker=dict(color=self.marker_color, size=7),
                showlegend=True
            )
        )

        fig.add_hline(
            y=last_production,
            line=dict(
                color=self.last_value_line_color,
                width=2,
                dash='dash'
            ),
            annotation_text=f'{last_production:.2f} bbl',
            annotation_position="bottom left",
            annotation_font=dict(color=self.last_value_line_color),
            name='Last Production'
        )

        fig.update_layout(
            xaxis=dict(
                title_text="Total Gas Injection Limit (qgl_limit)",
                gridcolor=self.grid_color,
                linecolor=self.grid_color,
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color),
                showgrid=True,
                gridwidth=1,
                dtick=1000,
                minor_griddash="dot",
            ),
            yaxis=dict(
                title_text="Total Oil Production (bbl)",
                gridcolor=self.grid_color,
                linecolor=self.grid_color,
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color)
            ),
            height=600,
            width=900,
            plot_bgcolor=self.bg_color,
            paper_bgcolor=self.bg_color,
            font=dict(color=self.text_color),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color=self.text_color)
            ),
            margin=dict(l=50, r=50, b=80, t=80, pad=4)
        )
        return fig


    '''
    Method to create a well curves chart.
    This method is responsible for creating a well curves chart using Plotly.
    It creates a line chart with markers for production and gas injection, as well as optimal lines and optimal points.
    '''
    def create_well_curves(self, well_results):
        cols = 3
        rows = int(ceil(len(well_results) / cols))
        PLOT_HEIGHT = 400 * rows
        VERTICAL_SPACING = 0.5 / rows
        MARGIN_TOP_PX = 140
        MARGIN_BOTTOM_PX = 80

        fig_prod = make_subplots(
            cols=cols,
            rows = rows,
            subplot_titles=[f"Well {well.well_name}" for well in well_results],
            horizontal_spacing=0.12,
            vertical_spacing=VERTICAL_SPACING
        )

        for idx, (well_data, well_result) in enumerate(zip(self.optimization_results['plot_data'], well_results)):
            row = (idx // 3) + 1
            col = (idx % 3) + 1

            optimal_qgl = well_result.optimal_gas_injection
            optimal_prod = well_result.optimal_production
            optimal_index = list(well_data["q_gl_common_range"]).index(optimal_qgl)
            optimal_fluid = list(well_data["q_fluid_predicted"])[optimal_index]

            MRP_qgl = self.optimization_results["p_qgl_optim_list"][idx]
            MRP_qgl_index = list(self.optimization_results["q_gl_common_range"]).index(MRP_qgl)
            MRP_fluid = list(well_data["q_fluid_predicted"])[MRP_qgl_index]


            fig_prod.add_trace(
                go.Scatter(
                    x=well_data["q_gl_common_range"],
                    y=well_data["q_fluid_predicted"],
                    mode='lines',
                    name='Adjusted Fluid Curve',
                    line=dict(width=3, color=self.fluid_line_color),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group1'
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=well_data["q_gl_common_range"],
                    y=well_data["q_oil_predicted"],
                    mode='lines',
                    name='Adjusted Oil Curve',
                    line=dict(width=3, color=self.line_color),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group2'
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=well_data["q_gl_original"],
                    y=well_data["q_fluid_original"],
                    mode='markers',
                    name='Real Data',
                    marker=dict(
                        color=self.marker_color,
                        size=7,
                        line=dict(width=1, color='DarkSlateGrey')
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group3'
                ),
                row=row, col=col
            )

            # 3. Óptimo según MRP
            fig_prod.add_trace(
                go.Scatter(
                    x=[self.optimization_results["p_qgl_optim_list"][idx], self.optimization_results["p_qgl_optim_list"][idx]],
                    y=[0, MRP_fluid],
                    mode='lines',
                    name='MRP Limit',
                    line=dict(color=self.marker_color, width=2, dash='dash'),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group4'
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=[self.optimization_results["p_qgl_optim_list"][idx]],
                    y=[self.optimization_results["p_qoil_optim_list"][idx]],
                    mode='markers',
                    name='MRP oil point',
                    marker=dict(
                        color=self.marker_color,
                        size=10,
                        symbol='x'
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group8'
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=[self.optimization_results["p_qgl_optim_list"][idx]],
                    y=[MRP_fluid],
                    mode='markers',
                    name='MRP fluid point',
                    marker=dict(
                        color=self.marker_color,
                        size=10,
                        symbol='x'
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group9'
                ),
                row=row, col=col
            )


            fig_prod.add_trace(
                go.Scatter(
                    x=[optimal_qgl, optimal_qgl],
                    y=[0, optimal_fluid],
                    mode='lines',
                    name='Optimal QGL',
                    line=dict(color=self.optimal_line_color, width=2, dash='dash'),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group5'
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=[optimal_qgl],
                    y=[optimal_prod],
                    mode='markers',
                    name='Optimal Oil Point',
                    marker=dict(
                        color=self.optimal_line_color,
                        size=10,
                        symbol='x'
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group6'
                ),
                row=row, col=col
            )

            fig_prod.add_trace(
                go.Scatter(
                    x=[optimal_qgl],
                    y=[optimal_fluid],
                    mode='markers',
                    name='Optimal Fluid Point',
                    marker=dict(
                        color=self.optimal_line_color,
                        size=10,
                        symbol='x'
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group7'
                ),
                row=row, col=col
            )

            fig_prod.update_xaxes(
                title_text="Gas Injection (q_gl)",
                row=row, col=col,
                gridcolor=self.grid_color,
                linecolor=self.grid_color,
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color),
                showline=True,
                mirror=True
            )

            fig_prod.update_yaxes(
                title_text="Oil Production (bbl/d)",
                row=row, col=col,
                gridcolor=self.grid_color,
                linecolor=self.grid_color,
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color),
                showline=True,
                mirror=True
            )

        fig_prod.update_layout(
            height=PLOT_HEIGHT,
            width=1200,
            plot_bgcolor=self.bg_color,
            paper_bgcolor=self.bg_color,
            font=dict(color=self.text_color),
            margin=dict(
                l=50,
                r=50,
                b=MARGIN_BOTTOM_PX,
                t=MARGIN_TOP_PX,
                pad=4
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.2,
                xanchor="right",
                x=1,
                font=dict(color=self.text_color)
            ),
        )
        return fig_prod
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
