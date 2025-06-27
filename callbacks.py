from typing import List, Optional, Tuple
from dash import Input, Output
import pandas as pd
from plotly.graph_objs import Figure
import dash_bootstrap_components as dbc

import data_manager
import plots
from config import THEMES


def register_callbacks(app, df: pd.DataFrame):
    """Rejestruje wszystkie callbacki aplikacji."""

    # Ten callback do zmiany motywu jest rejestrowany zawsze.
    @app.callback(
        Output("main-stylesheet", "href"),
        Input("theme-store", "data")
    )
    def update_main_stylesheet(theme_name: str) -> str:
        """Aktualizuje główny arkusz stylów Bootstrap."""
        if theme_name in THEMES:
            return dbc.themes.__dict__[THEMES[theme_name]]
        return dbc.themes.FLATLY

    # Rejestruj główne callbacki tylko, jeśli DataFrame został pomyślnie załadowany.
    if df is not None:
        @app.callback(
            Output("theme-store", "data"),
            Input("theme-selector", "value")
        )
        def update_theme_store(selected_theme: str) -> str:
            """Zapisuje wybrany motyw w dcc.Store."""
            return selected_theme

        # Ten callback odpowiada za styl dropdownów w ciemnym motywie.
        @app.callback(
            [Output("gender-filter", "className"),
             Output("edu-filter", "className"),
             Output("job-filter", "className")],
            Input("theme-store", "data")
        )
        def update_dropdown_class(theme_name: str) -> Tuple[str, str, str]:
            """Dodaje specjalną klasę CSS do dropdownów w trybie ciemnym."""
            class_name = "dark-dropdown" if theme_name == "Ciemny" else ""
            return class_name, class_name, class_name

    @app.callback(
        Output("themed-layout", "style"),
        Input("theme-store", "data")
    )
    def update_layout_style(current_theme):
        padding = {"padding": "20px", "paddingLeft": "5%", "paddingRight": "5%"}

        if current_theme == "Ciemny":
            return {
                "backgroundColor": "#1e1e1e",
                "color": "white",
                **padding
            }
        else:  # Jasny
            return {
                "backgroundColor": "white",
                "color": "black",
                **padding
            }

    @app.callback(
        [Output("scatter-plot", "figure"),
         Output("box-plot", "figure"),
         Output("heatmap", "figure"),
         Output("histogram_fig", "figure"),
         Output("barchart_fig", "figure"),
         Output("line_fig", "figure"),
         Output("attendance-violin-plot", "figure"),
         Output("job-sunburst", "figure"),
         Output("mental-health-polar", "figure"),
         Output("kpi-student-count", "children"),
         Output("kpi-avg-score", "children"),
         Output("kpi-avg-study-hours", "children")],
        [Input("gender-filter", "value"),
         Input("edu-filter", "value"),
         Input("study-hours-slider", "value"),
         Input("job-filter", "value"),
         Input("theme-store", "data")]
    )
    def update_all_visuals(
            selected_gender: Optional[List[str]],
            selected_edu: Optional[List[str]],
            study_hours_range: List[int],
            selected_job: Optional[List[str]],
            theme_name: str
    ) -> Tuple[Figure, Figure, Figure, Figure, Figure, Figure, Figure, Figure, Figure, str, str, str]:
        """Główny callback aktualizujący wszystkie wykresy i KPI."""

        template = "plotly_dark" if theme_name == "Ciemny" else "plotly_white"

        # 1. Filtrowanie danych
        filtered_df = data_manager.filter_data(
            df, selected_gender, selected_edu, study_hours_range, selected_job
        )

        # 2. Obliczenia KPI
        if filtered_df.empty:
            student_count = "0"
            avg_score = "N/A"
            avg_study_hours = "N/A"
        else:
            student_count = str(len(filtered_df))
            avg_score = f"{filtered_df['exam_score'].mean():.2f}"
            avg_study_hours = f"{filtered_df['study_hours_per_day'].mean():.2f}"

        # 3. Tworzenie wykresów
        scatter_fig = plots.create_scatter_plot(filtered_df, template)
        box_fig = plots.create_box_plot(filtered_df, template)
        heatmap_fig = plots.create_heatmap(filtered_df, template)
        histogram_fig = plots.create_exam_score_histogram(filtered_df, template)
        barchart_fig = plots.create_bar_avg_score_by_edu(filtered_df, template)
        line_fig = plots.create_sleep_vs_score_lineplot(filtered_df, template)
        attendance_fig = plots.create_attendance_violin_plot(filtered_df, template)
        job_fig = plots.create_job_sunburst_chart(filtered_df, template)
        mental_fig = plots.create_mental_health_polar_chart(filtered_df, template)

        return (
            scatter_fig, box_fig, heatmap_fig, histogram_fig, barchart_fig, line_fig,
            attendance_fig, job_fig, mental_fig,
            student_count, avg_score, avg_study_hours
        )