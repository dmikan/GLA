import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ChartStyle:
    def __init__(self):
        self.bg_color = "#0E1117"
        self.grid_color = "#37474F"
        self.text_color = "#FFFFFF"
        self.line_color = "#00E676"
        self.marker_color = "#C8E6C9"
        self.optimal_line_color = "#FF5252"
        self.last_value_line_color = "#FF1744"

    '''
    Método para crear un gráfico de optimización global.
    Este método se encarga de crear un gráfico de optimización global utilizando Plotly.
    Se encarga de crear un gráfico de líneas con marcadores para la producción total y una línea horizontal para el último valor de producción.
    '''    
    def create_global_optimization_chart(self, optimization_results):
        last_production = optimization_results["total_production"][-1] if optimization_results["total_production"] else 0

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=optimization_results["total_qgl"],
                y=optimization_results["total_production"],
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
            margin=dict(l=50, r=50, b=80, t=80, pad=4),
            hovermode="x unified"
        )
        return fig
    
    
    '''
    Método para crear un gráfico de curvas de pozos.
    Este método se encarga de crear un gráfico de curvas de pozos utilizando Plotly.
    Se encarga de crear un gráfico de líneas con marcadores para la producción y la inyección de gas, así como líneas óptimas y puntos óptimos.
    '''
    def create_well_curves_chart(self, results, well_result):
        fig_prod = make_subplots(
            rows=2, 
            cols=3, 
            subplot_titles=[f"Well {well.well_name} - Oil Production" for well in well_result],
            horizontal_spacing=0.1,
            vertical_spacing=0.15
        )

        for idx, (well_data, pozo) in enumerate(zip(results['plot_data'], well_result)):
            row = (idx // 3) + 1
            col = (idx % 3) + 1
            
            fig_prod.add_trace(
                go.Scatter(
                    x=well_data["q_gl_range"],
                    y=well_data["q_oil_predicted"],
                    mode='lines',
                    name='Adjusted Curve',
                    line=dict(width=3, color=self.line_color),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group1'
                ),
                row=row, col=col
            )
            
            fig_prod.add_trace(
                go.Scatter(
                    x=well_data["q_gl_actual"],
                    y=well_data["q_oil_actual"],
                    mode='markers',
                    name='Real Data',
                    marker=dict(
                        color=self.marker_color, 
                        size=7, 
                        line=dict(width=1, color='DarkSlateGrey')
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group2'
                ),
                row=row, col=col
            )

            # 3. Óptimo según MRP 
            fig_prod.add_trace(
                go.Scatter(
                    x=[results["p_qgl_optim_list"][idx], results["p_qgl_optim_list"][idx]],
                    y=[0, results["p_qoil_optim_list"][idx]],
                    mode='lines',
                    name='Optimal QGL',
                    line=dict(color=self.marker_color, width=2, dash='dash'),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group5'
                ),
                row=row, col=col
            )
            
            optimal_qgl = pozo.optimal_gas_injection
            optimal_prod = pozo.optimal_production
            
            fig_prod.add_trace(
                go.Scatter(
                    x=[optimal_qgl, optimal_qgl],
                    y=[0, optimal_prod],
                    mode='lines',
                    name='Optimal QGL',
                    line=dict(color=self.optimal_line_color, width=2, dash='dash'),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group'
                ),
                row=row, col=col
            )
            
            fig_prod.add_trace(
                go.Scatter(
                    x=[optimal_qgl],
                    y=[optimal_prod],
                    mode='markers',
                    name='Optimal Point',
                    marker=dict(
                        color=self.optimal_line_color, 
                        size=10, 
                        symbol='x'
                    ),
                    showlegend=True if idx == 0 else False,
                    legendgroup='group4'
                ),
                row=row, col=col
            )
            
            fig_prod.update_xaxes(
                title_text="Gas Injection (q_gl)", 
                row=row, col=col,
                gridcolor=self.grid_color,
                linecolor=self.grid_color,
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color)
            )
            
            fig_prod.update_yaxes(
                title_text="Oil Production (bbl/d)", 
                row=row, col=col,
                gridcolor=self.grid_color,
                linecolor=self.grid_color,
                tickfont=dict(color=self.text_color),
                title_font=dict(color=self.text_color)
            )

        fig_prod.update_layout(
            height=800,
            width=1200,
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
            margin=dict(
                l=50,
                r=50,
                b=80,
                t=100,
                pad=4
            )
        )
        return fig_prod