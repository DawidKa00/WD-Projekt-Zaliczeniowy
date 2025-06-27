from dash import dcc, html
import pandas as pd
import dash_bootstrap_components as dbc


def create_layout(df: pd.DataFrame) -> html.Div:
    """Tworzy layout aplikacji na podstawie załadowanego DataFrame."""

    # Przygotowanie opcji dla filtrów
    gender_options = [
        {'label': str(gender), 'value': str(gender)}
        for gender in sorted(df['gender'].dropna().unique())
    ]

    edu_options = [
        {'label': str(edu), 'value': str(edu)}
        for edu in sorted(df['parental_education_level'].dropna().unique())
    ]

    # Dodanie opcji dla filtra pracy
    job_options = [
        {'label': str(job), 'value': str(job)}
        for job in sorted(df['part_time_job'].dropna().unique())
    ]

    # Określenie zakresu dla suwaka godzin nauki
    min_hours = int(df['study_hours_per_day'].min())
    max_hours = int(df['study_hours_per_day'].max())

    return html.Div(id="themed-layout", children=[
        # Nagłówek i przełącznik motywu
        html.Div([
            html.Label("🌗 Tryb wyświetlania:"),
            dcc.RadioItems(
                id="theme-selector",
                options=[{"label": "Jasny", "value": "Jasny"}, {"label": "Ciemny", "value": "Ciemny"}],
                value="Jasny", labelStyle={'display': 'inline-block', 'marginRight': '15px'}
            ),
        ], style={"marginBottom": "20px"}),
        dcc.Store(id='theme-store', data="Jasny"),  # Przechowuje wybrany motyw

        html.H1("📊 Nawyki studentów a wyniki w nauce", style={"textAlign": "center"}),

        # Sekcja KPI
        html.Div([
            html.H3("Kluczowe wskaźniki", style={"textAlign": "center"}),
            html.Div([
                dbc.Col([html.H4("Liczba studentów"), html.H2(id="kpi-student-count")]),
                dbc.Col([html.H4("Średni wynik"), html.H2(id="kpi-avg-score")]),
                dbc.Col([html.H4("Śr. godziny nauki"), html.H2(id="kpi-avg-study-hours")]),
            ], className="row text-center my-4")
        ]),

        # Sekcja filtrów
        html.Div([
            dbc.Row([
                dbc.Col(html.Div([html.Label("Płeć:"),
                                  dcc.Dropdown(id="gender-filter", options=gender_options, multi=True,
                                               placeholder="Wybierz...")])),
                dbc.Col(html.Div([html.Label("Wykształcenie rodziców:"),
                                  dcc.Dropdown(id="edu-filter", options=edu_options, multi=True,
                                               placeholder="Wybierz...")])),
                dbc.Col(html.Div([html.Label("Praca na część etatu:"),
                                  dcc.Dropdown(id="job-filter", options=job_options, multi=True,
                                               placeholder="Wybierz...")])),
            ])
        ], style={"marginBottom": "20px"}),

        html.Div([
            html.Label("Zakres godzin nauki (na dzień):"),
            dcc.RangeSlider(
                id="study-hours-slider", min=min_hours, max=max_hours, step=1,
                marks={i: str(i) for i in range(min_hours, max_hours + 1)},
                value=[min_hours, max_hours]
            )
        ], style={"marginBottom": "30px"}),

        # Sekcja z wykresami
        dbc.Row([
            dbc.Col(dcc.Graph(id="scatter-plot"), width=6),
            dbc.Col(dcc.Graph(id="box-plot"), width=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="heatmap"), width=6),
            dbc.Col(dcc.Graph(id="histogram_fig"), width=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="barchart_fig"), width=6),
            dbc.Col(dcc.Graph(id="line_fig"), width=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="attendance-violin-plot"), width=6),
            dbc.Col(dcc.Graph(id="job-sunburst"), width=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="mental-health-polar"), width=12)
        ], className="mb-4"),
    ])


def create_error_layout() -> html.Div:
    """Zwraca layout błędu, gdy dane nie mogą być załadowane."""
    return html.Div([
        html.H1("❌ Błąd: Brak dostępnych danych", style={"textAlign": "center", "color": "red"}),
        html.P("Nie można było załadować pliku 'student_habits_performance.csv'.", style={"textAlign": "center"}),
        html.P("Sprawdź, czy plik istnieje w katalogu 'data' i spróbuj ponownie.", style={"textAlign": "center"})
    ])