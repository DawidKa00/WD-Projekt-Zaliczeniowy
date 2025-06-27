from dash import dcc, html
import pandas as pd


def create_layout(df: pd.DataFrame) -> html.Div:
    # Jeśli dane nie zostały załadowane, wyświetl komunikat o błędzie
    if df is None or df.empty:
        return html.Div([
            html.H1("❌ Błąd: Brak dostępnych danych", style={"textAlign": "center", "color": "red"}),
            html.P("Sprawdź plik z danymi i spróbuj ponownie.", style={"textAlign": "center"})
        ])

    def themed_div(children):
        return html.Div(
            children=children,
            id="themed-layout",  # ID callbacku do zmiany stylu
            style={
                "padding": "20px",
                "padding-left": "200px",
                "padding-right": "200px",
                "backgroundColor": "white",
                "color": "black"
            }
        )

    # Przygotowanie opcji dla filtrów (list rozwijanych)
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

    # Definicja struktury HTML dashboardu
    layout = themed_div([

        html.Div([
            html.Label("🌗 Tryb wyświetlania:", style={"fontWeight": "bold"}),
            dcc.RadioItems(
                id="theme-selector",
                options=[
                    {"label": "Jasny", "value": "Jasny"},
                    {"label": "Ciemny", "value": "Ciemny"}
                ],
                value="Jasny",
                labelStyle={'display': 'inline-block', 'marginRight': '15px'}
            ),
            dcc.Store(id='theme-store', data="Jasny")
        ], style={"marginBottom": "20px"}),

        # Nagłówek główny
        html.H1("📊 Nawyki studentów a wyniki w nauce",
                style={"textAlign": "center", "marginBottom": "30px"}),

        # Sekcja KPI
        html.Div([
            html.H3("📊 Kluczowe wskaźniki", style={"textAlign": "center", "marginBottom": "20px"}),
            html.Div([
                html.Div([
                    html.H4("Liczba studentów", style={"textAlign": "center", "color": "#1f77b4"}),
                    html.H2(id="kpi-student-count", style={"textAlign": "center", "margin": "0"})
                ], style={"width": "30%", "display": "inline-block", "textAlign": "center", "padding": "10px"}),

                html.Div([
                    html.H4("Średni wynik", style={"textAlign": "center", "color": "#ff7f0e"}),
                    html.H2(id="kpi-avg-score", style={"textAlign": "center", "margin": "0"})
                ], style={"width": "30%", "display": "inline-block", "textAlign": "center", "padding": "10px"}),

                html.Div([
                    html.H4("Średnie godziny nauki", style={"textAlign": "center", "color": "#2ca02c"}),
                    html.H2(id="kpi-avg-study-hours", style={"textAlign": "center", "margin": "0"})
                ], style={"width": "30%", "display": "inline-block", "textAlign": "center", "padding": "10px"}),
            ], style={"display": "flex", "justifyContent": "space-around", "marginBottom": "30px"})
        ]),

        # Sekcja z filtrami
        html.Div([
            # Filtr płci
            html.Div([
                html.Label("Płeć:", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="gender-filter",
                    options=gender_options,
                    multi=True,
                    placeholder="Wybierz płeć",
                    style={},
                    className=""
                )
            ], style={"width": "30%", "display": "inline-block", "marginRight": "5%"}),

            # Filtr wykształcenia rodziców
            html.Div([
                html.Label("Wykształcenie rodziców:", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="edu-filter",
                    options=edu_options,
                    multi=True,
                    placeholder="Wybierz poziom edukacji",
                    style={},
                    className=""
                )
            ], style={"width": "30%", "display": "inline-block", "marginRight": "5%"}),

            # Filtr pracy
            html.Div([
                html.Label("Praca na część etatu:", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="job-filter",
                    options=job_options,
                    multi=True,
                    placeholder="Wybierz status pracy",
                    style={},
                    className=""
                )
            ], style={"width": "30%", "display": "inline-block"}),
        ], style={"marginBottom": "20px"}),

        # Suwak do filtrowania godzin nauki
        html.Div([
            html.Label("Zakres godzin nauki (na dzień):", style={"fontWeight": "bold"}),
            dcc.RangeSlider(
                id="study-hours-slider",
                min=min_hours,
                max=max_hours,
                step=1,
                marks={i: str(i) for i in range(min_hours, max_hours + 1)},  # Etykiety na suwaku
                value=[min_hours, max_hours]  # Domyślna wartość (cały zakres)
            )
        ], style={"marginBottom": "30px"}),

        # Sekcja z wykresami (placeholdery)
        # Wykres rozrzutu
        html.H3("📍 Wpływ nauki na wynik egzaminu"),
        html.P(
            "Ten wykres pokazuje zależność między dzienną liczbą godzin nauki a uzyskanym wynikiem egzaminu. Każdy punkt reprezentuje jednego studenta."),
        dcc.Graph(id="scatter-plot"),

        # Wykres pudełkowy
        html.H3("📍 Rozkład wyników wg płci"),
        html.P(
            "Wykres pudełkowy przedstawia różnice w rozkładzie wyników egzaminów pomiędzy grupami płci. Widzimy medianę, kwartyle oraz wartości odstające."),
        dcc.Graph(id="box-plot"),

        # Mapa korelacji
        html.H3("📍 Korelacje między cechami"),
        html.P(
            "Mapa ciepła pokazuje siłę i kierunek zależności pomiędzy cechami numerycznymi, takimi jak godziny nauki, snu, korzystanie z social mediów oraz wynik egzaminu."),
        dcc.Graph(id="heatmap"),

        # Histogram wyników
        html.H3("📍 Rozkład wyników egzaminu wg płci"),
        html.P(
            "Histogram przedstawia, jak rozkładają się wyniki egzaminów w zależności od płci. Pomaga zidentyfikować różnice w poziomie osiągnięć."),
        dcc.Graph(id="histogram_fig"),

        # Bar chart wg edukacji rodziców
        html.H3("📍 Średnie wyniki wg poziomu edukacji rodziców"),
        html.P(
            "Wykres słupkowy prezentuje średnie wyniki egzaminów w zależności od poziomu wykształcenia rodziców. Pokazuje możliwy wpływ środowiska domowego."),
        dcc.Graph(id="barchart_fig"),

        # Liniowy: sen vs wynik
        html.H3("📍 Liczba godzin snu a wynik egzaminu"),
        html.P(
            "Wykres pokazuje, jak średni wynik egzaminu zmienia się wraz ze wzrostem liczby godzin snu. Dane są zagregowane po zaokrąglonych wartościach."),
        dcc.Graph(id="line_fig"),

        # Nowe wykresy
        html.H3("📍 Rozkład frekwencji wg kategorii wyników"),
        html.P(
            "Wykres skrzypcowy pokazujący rozkład frekwencji na zajęciach dla różnych kategorii wyników egzaminu."),
        dcc.Graph(id="attendance-violin-plot"),

        html.H3("📍 Struktura studentów: praca i płeć"),
        html.P(
            "Wykres słoneczny przedstawiający hierarchiczną strukturę studentów według statusu pracy i płci."),
        dcc.Graph(id="job-sunburst"),

        html.H3("📍 Profil metryk wg kondycji psychicznej"),
        html.P(
            "Wykres polarny (radar) pokazujący różne metryki studentów w zależności od oceny kondycji psychicznej."),
        dcc.Graph(id="mental-health-polar")

    ])
    return layout


def create_error_layout() -> html.Div:
    """Zwraca layout błędu, gdy dane nie mogą być załadowane."""
    return html.Div([
        html.H1("❌ Błąd: Brak dostępnych danych", style={"textAlign": "center", "color": "red"}),
        html.P("Nie można było załadować pliku 'student_habits_performance.csv'.", style={"textAlign": "center"}),
        html.P("Sprawdź, czy plik istnieje w katalogu 'data' i spróbuj ponownie.", style={"textAlign": "center"})
    ])