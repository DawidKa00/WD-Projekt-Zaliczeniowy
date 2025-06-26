from typing import List, Tuple, Optional
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Figure

from data_loader import download_data_if_needed
import dash_bootstrap_components as dbc


def create_scatter_plot(filtered_df: pd.DataFrame, template) -> go.Figure:
    """Tworzy wykres rozrzutu pokazujący zależność między godzinami nauki a wynikiem egzaminu."""
    # Jeśli przefiltrowane dane są puste, zwróć pusty wykres z informacją
    if filtered_df.empty:
        return px.scatter(title="Wpływ czasu nauki na wynik egzaminu (Brak danych)")

    # Tworzenie wykresu rozrzutu
    return px.scatter(
        filtered_df,
        x="study_hours_per_day",
        y="exam_score",
        color="gender",
        hover_data=['social_media_hours', 'sleep_hours'],  # Dodatkowe informacje po najechaniu myszką
        template=template,
        title="Wpływ czasu nauki na wynik egzaminu",
        labels={
            'gender': 'Płeć',
            'study_hours_per_day': 'Godziny nauki dziennie',
            'exam_score': 'Wynik egzaminu',
            'social_media_hours': 'Social media hours',
            'sleep_hours': 'Godziny snu'
        }
    )


class StudentPerformanceDashboard:
    """Klasa reprezentująca dashboard do analizy nawyków studentów w kontekście ich wyników w nauce."""

    def __init__(self):
        """Konstruktor klasy. Inicjalizuje aplikację Dash i przygotowuje miejsce na dane."""

        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.FLATLY]
        )
        self.app.title = "Nawyki studentów a wyniki w nauce"

        self.current_theme = dbc.themes.BOOTSTRAP

        self.themes = {
            "Jasny": dbc.themes.FLATLY,
            "Ciemny": dbc.themes.DARKLY
        }

    def run(self, debug=False):
        """Uruchamia aplikację."""
        self.app.run_server(debug=debug)

    @property
    def server(self):
        """Zwraca serwer Flask wymagany do deployu."""
        return self.app.server

    def load_data(self) -> bool:
        """Ładuje i waliduje dane z pliku CSV."""
        download_data_if_needed()

        try:
            # Próba wczytania danych z pliku CSV
            self.df = pd.read_csv("data/student_habits_performance.csv")

            # Walidacja, czy w danych znajdują się wszystkie wymagane kolumny
            required_columns = [
                'gender', 'parental_education_level', 'study_hours_per_day',
                'exam_score', 'social_media_hours', 'sleep_hours',
                'attendance_percentage', 'part_time_job', 'mental_health_rating'
            ]

            # Sprawdzenie, których kolumn brakuje
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            if missing_columns:
                print(f"❌ Brak wymaganych kolumn: {missing_columns}")
                return False  # Zwraca False, jeśli brakuje kolumn

            # Sprawdzenie, czy DataFrame nie jest pusty
            if self.df.empty:
                print("❌ Zbiór danych jest pusty")
                return False  # Zwraca False, jeśli dane są puste

            print(f"✅ Dane załadowano pomyślnie. Rozmiar: {self.df.shape}")
            return True  # Zwraca True, jeśli dane zostały załadowane poprawnie

        except FileNotFoundError:
            print("❌ Nie znaleziono pliku CSV. Upewnij się, że plik istnieje w katalogu 'data'.")
            return False
        except pd.errors.EmptyDataError:
            print("❌ Plik CSV jest pusty. Sprawdź zawartość pliku.")
            return False
        except pd.errors.ParserError as e:
            print(f"❌ Błąd podczas parsowania pliku CSV: {e}")
            return False
        except Exception as e:
            print(f"❌ Wystąpił nieoczekiwany błąd podczas ładowania danych: {e}")
            return False

    def filter_data(self, selected_gender: Optional[List[str]],
                    selected_edu: Optional[List[str]],
                    study_hours_range: List[int], selected_job: Optional[List[str]]) -> pd.DataFrame:
        """Filtruje DataFrame na podstawie wyborów użytkownika w dashboardzie."""
        # Sprawdzenie, czy DataFrame został załadowany
        if self.df is None or self.df.empty:
            return pd.DataFrame()  # Zwraca pusty DataFrame, jeśli nie ma danych

        # Stworzenie kopii DataFrame, aby uniknąć modyfikacji oryginalnych danych
        filtered_df = self.df.copy()

        # Filtr płci
        if selected_gender:
            filtered_df = filtered_df[filtered_df['gender'].isin(selected_gender)]

        # Filtr wykształcenia rodziców
        if selected_edu:
            filtered_df = filtered_df[
                filtered_df['parental_education_level'].isin(selected_edu)
            ]

        # Filtr pracy na część etatu
        if selected_job:
            filtered_df = filtered_df[filtered_df['part_time_job'].isin(selected_job)]

        # Filtr zakresu godzin nauki
        if len(study_hours_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['study_hours_per_day'] >= study_hours_range[0]) &
                (filtered_df['study_hours_per_day'] <= study_hours_range[1])
                ]

        return filtered_df

    def create_box_plot(self, filtered_df: pd.DataFrame, template) -> go.Figure:
        """Tworzy wykres pudełkowy dla wyników egzaminu w podziale na płeć."""
        # Jeśli przefiltrowane dane są puste, zwróć pusty wykres z informacją
        if filtered_df.empty:
            return px.box(title="Rozkład wyników egzaminu względem płci (Brak danych)")

        # Tworzenie wykresu pudełkowego
        return px.box(
            filtered_df,
            x="gender",
            y="exam_score",
            color="gender",
            template=template,
            title="Rozkład wyników egzaminu względem płci",
            labels={
                'gender': 'Płeć',
                'exam_score': 'Wynik egzaminu'
            }
        )

    def create_heatmap(self, filtered_df: pd.DataFrame, template) -> go.Figure:
        """Tworzy mapę ciepła korelacji."""
        # Jeśli przefiltrowane dane są puste, zwróć pusty wykres z informacją
        if filtered_df.empty:
            return px.imshow([[0]], title="Korelacje między cechami (Brak danych)")

        # Wybór tylko kolumn numerycznych do obliczenia korelacji
        numeric_columns = ['study_hours_per_day', 'sleep_hours', 'social_media_hours', 'exam_score',
                           'attendance_percentage']
        # Sprawdzenie, które z tych kolumn faktycznie istnieją w DataFrame
        available_columns = [col for col in numeric_columns if col in filtered_df.columns]

        # Mapa korelacji wymaga co najmniej dwóch kolumn
        if len(available_columns) < 2:
            return px.imshow([[0]], title="Korelacje między cechami (Niewystarczające dane)")

        # Obliczenie macierzy korelacji
        heatmap_df = filtered_df[available_columns].corr()
        # Tworzenie mapy ciepła
        return px.imshow(
            heatmap_df,
            text_auto=True,  # Automatyczne wyświetlanie wartości korelacji na mapie
            template=template,
            title="Korelacje między cechami",
            aspect="auto",  # Automatyczne dopasowanie proporcji
        )

    def create_exam_score_histogram(self, filtered_df: pd.DataFrame, template) -> go.Figure:
        """Tworzy histogram rozkładu wyników egzaminu z podziałem na płeć."""
        if filtered_df.empty:
            return px.histogram(title="Rozkład wyników egzaminu (Brak danych)")

        return px.histogram(
            filtered_df,
            x="exam_score",
            color="gender",
            nbins=20,
            barmode='overlay',
            opacity=0.6,
            template=template,
            title="Rozkład wyników egzaminu wg płci",
            labels={
                "exam_score": "Wynik egzaminu",
                "gender": "Płeć"
            }
        )

    def create_bar_avg_score_by_edu(self, filtered_df: pd.DataFrame, template) -> go.Figure:
        """Tworzy wykres słupkowy średnich wyników wg wykształcenia rodziców."""
        if filtered_df.empty:
            return px.bar(title="Średnie wyniki wg poziomu edukacji rodziców (Brak danych)")

        avg_scores = (
            filtered_df
            .groupby("parental_education_level")["exam_score"]
            .mean()
            .sort_values()
            .reset_index()
        )

        return px.bar(
            avg_scores,
            x="parental_education_level",
            y="exam_score",
            template=template,
            title="Średnie wyniki egzaminów wg wykształcenia rodziców",
            labels={
                "parental_education_level": "Poziom wykształcenia rodziców",
                "exam_score": "Średni wynik egzaminu"
            }
        )

    def create_sleep_vs_score_lineplot(self, filtered_df: pd.DataFrame, template) -> go.Figure:
        """Tworzy wykres liniowy: średni wynik egzaminu w zależności od liczby godzin snu."""
        if filtered_df.empty:
            return px.line(title="Średni wynik vs liczba godzin snu (Brak danych)")

        df_grouped = (
            filtered_df
            .copy()
            .assign(sleep_hours_rounded=lambda df: df['sleep_hours'].round())
            .groupby("sleep_hours_rounded")["exam_score"]
            .mean()
            .reset_index()
        )

        return px.line(
            df_grouped,
            x="sleep_hours_rounded",
            y="exam_score",
            markers=True,
            template=template,
            title="Średni wynik egzaminu w zależności od liczby godzin snu",
            labels={
                "sleep_hours_rounded": "Godziny snu (zaokrąglone)",
                "exam_score": "Średni wynik egzaminu"
            }
        )

    def create_attendance_violin_plot(self, filtered_df: pd.DataFrame, template) -> go.Figure:
        """Tworzy wykres skrzypcowy pokazujący rozkład frekwencji dla różnych przedziałów wyników."""
        if filtered_df.empty:
            return px.violin(title="Rozkład frekwencji wg wyników egzaminu (Brak danych)")

        # Tworzenie kategorii wyników
        filtered_df = filtered_df.copy()
        filtered_df['score_category'] = pd.cut(
            filtered_df['exam_score'],
            bins=[0, 60, 75, 85, 100],
            labels=['Słaby (0-60)', 'Średni (60-75)', 'Dobry (75-85)', 'Bardzo dobry (85-100)']
        )

        return px.violin(
            filtered_df.dropna(subset=['score_category']),
            x="score_category",
            y="attendance_percentage",
            color="score_category",
            template=template,
            title="Rozkład frekwencji w różnych kategoriach wyników",
            labels={
                'score_category': 'Kategoria wyniku egzaminu',
                'attendance_percentage': 'Procentowa frekwencja na zajęciach'
            }
        )

    def create_job_sunburst_chart(self, filtered_df: pd.DataFrame, template) -> go.Figure:
        """Tworzy wykres słoneczny (sunburst) pokazujący strukturę studentów wg pracy i płci."""
        if filtered_df.empty:
            return go.Figure().add_annotation(
                text="Struktura studentów: praca vs płeć (Brak danych)",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )

        # Przygotowanie danych dla sunburst
        job_gender_counts = (
            filtered_df.groupby(['part_time_job', 'gender'])
            .size()
            .reset_index(name='count')
        )

        # Tworzenie struktury hierarchicznej
        sunburst_data = []

        # Dodanie poziomów: praca -> płeć
        for _, row in job_gender_counts.iterrows():
            sunburst_data.append({
                'ids': f"{row['part_time_job']} - {row['gender']}",
                'labels': f"{row['gender']}",
                'parents': f"{row['part_time_job']}",
                'values': row['count']
            })

        # Dodanie głównych kategorii pracy
        job_totals = filtered_df.groupby('part_time_job').size().reset_index(name='total')
        for _, row in job_totals.iterrows():
            sunburst_data.append({
                'ids': f"{row['part_time_job']}",
                'labels': f"Praca: {row['part_time_job']}",
                'parents': "",
                'values': row['total']
            })

        df_sunburst = pd.DataFrame(sunburst_data)

        fig = go.Figure(go.Sunburst(
            ids=df_sunburst['ids'],
            labels=df_sunburst['labels'],
            parents=df_sunburst['parents'],
            values=df_sunburst['values'],
            branchvalues="total"
        ))

        fig.update_layout(
            title="Struktura studentów: Status pracy i płeć",
            template=template,
            font_size=12
        )

        return fig

    def create_mental_health_polar_chart(self, filtered_df: pd.DataFrame, template) -> go.Figure:
        """Tworzy wykres polarny (radar) pokazujący różne metryki wg kondycji psychicznej."""
        if filtered_df.empty or 'mental_health_rating' not in filtered_df.columns:
            return go.Figure().add_annotation(
                text="Metryki wg kondycji psychicznej (Brak danych)",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
            )

        # Grupowanie po kondycji psychicznej i obliczanie średnich
        mental_groups = filtered_df.groupby('mental_health_rating').agg({
            'exam_score': 'mean',
            'study_hours_per_day': 'mean',
            'sleep_hours': 'mean',
            'attendance_percentage': 'mean',
            'social_media_hours': lambda x: 10 - x.mean()  # Odwrócona skala dla social media
        }).reset_index()

        # Normalizacja do skali 0-10 dla lepszej wizualizacji
        mental_groups['exam_score_norm'] = mental_groups['exam_score'] / 10
        mental_groups['study_hours_norm'] = mental_groups['study_hours_per_day'] * 2
        mental_groups['sleep_hours_norm'] = mental_groups['sleep_hours'] * 1.25
        mental_groups['attendance_norm'] = mental_groups['attendance_percentage'] / 10

        fig = go.Figure()

        categories = ['Wynik egzaminu', 'Godziny nauki', 'Godziny snu', 'Frekwencja', 'Mniej social media']

        # Dodanie linii dla różnych poziomów kondycji psychicznej
        colors = ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen', 'blue', 'purple', 'pink', 'brown']

        for i, row in mental_groups.iterrows():
            values = [
                row['exam_score_norm'],
                row['study_hours_norm'],
                row['sleep_hours_norm'],
                row['attendance_norm'],
                row['social_media_hours']
            ]

            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],  # Zamknięcie wykresu
                theta=categories + [categories[0]],
                fill='toself',
                name=f'Kondycja psychiczna: {int(row["mental_health_rating"])}',
                line_color=colors[i % len(colors)],
                opacity=0.6
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            showlegend=True,
            title="Profil różnych metryk wg oceny kondycji psychicznej",
            template=template
        )

        return fig

    def setup_layout(self):
        """Konfiguruje układ (layout) dashboardu."""

        # Jeśli dane nie zostały załadowane, wyświetl komunikat o błędzie
        if self.df is None or self.df.empty:
            self.app.layout = html.Div([
                html.H1("❌ Błąd: Brak dostępnych danych", style={"textAlign": "center", "color": "red"}),
                html.P("Sprawdź plik z danymi i spróbuj ponownie.", style={"textAlign": "center"})
            ])
            return

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
            for gender in sorted(self.df['gender'].dropna().unique())
        ]

        edu_options = [
            {'label': str(edu), 'value': str(edu)}
            for edu in sorted(self.df['parental_education_level'].dropna().unique())
        ]

        # Dodanie opcji dla filtra pracy
        job_options = [
            {'label': str(job), 'value': str(job)}
            for job in sorted(self.df['part_time_job'].dropna().unique())
        ]

        # Określenie zakresu dla suwaka godzin nauki
        min_hours = int(self.df['study_hours_per_day'].min())
        max_hours = int(self.df['study_hours_per_day'].max())

        # Definicja struktury HTML dashboardu
        self.app.layout = themed_div([

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

    def setup_callbacks(self):
        """Konfiguruje callbacki"""

        @self.app.callback(
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
        def update_graphs(selected_gender: Optional[List[str]],
                          selected_edu: Optional[List[str]],
                          study_hours_range: List[int],
                          selected_job: Optional[List[str]],
                          current_theme) -> Tuple[
            Figure, Figure, Figure, Figure, Figure, Figure, Figure, Figure, Figure, int, str, str]:
            """Aktualizuje wszystkie wykresy na podstawie wybranych filtrów."""

            template = "plotly_dark" if current_theme == "Ciemny" else "plotly_white"

            # 1. Filtruj dane na podstawie bieżących wartości filtrów
            filtered_df = self.filter_data(selected_gender, selected_edu, study_hours_range, selected_job)

            # 2. Wygeneruj nowe wykresy na podstawie przefiltrowanych danych
            # Obliczenia dla KPI
            if filtered_df.empty:
                student_count = 0
                avg_score = "N/A"
                avg_study_hours = "N/A"
            else:
                student_count = len(filtered_df)
                avg_score = f"{filtered_df['exam_score'].mean():.2f}"
                avg_study_hours = f"{filtered_df['study_hours_per_day'].mean():.2f}"

            scatter_fig = create_scatter_plot(filtered_df, template)
            box_fig = self.create_box_plot(filtered_df, template)
            heatmap_fig = self.create_heatmap(filtered_df, template)
            histogram_fig = self.create_exam_score_histogram(filtered_df, template)
            barchart_fig = self.create_bar_avg_score_by_edu(filtered_df, template)
            line_fig = self.create_sleep_vs_score_lineplot(filtered_df, template)

            attendance_fig = self.create_attendance_violin_plot(filtered_df, template)
            job_fig = self.create_job_sunburst_chart(filtered_df, template)
            mental_fig = self.create_mental_health_polar_chart(filtered_df, template)

            # 3. Zwróć zaktualizowane figury do odpowiednich komponentów
            return (scatter_fig, box_fig, heatmap_fig, histogram_fig, barchart_fig, line_fig, attendance_fig, job_fig,
                    mental_fig, student_count, avg_score, avg_study_hours)

        @self.app.callback(
            Output("theme-store", "data"),
            Input("theme-selector", "value")
        )
        def update_theme_store(selected_theme):
            return selected_theme

        @self.app.callback(
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

        @self.app.callback(
            [Output("gender-filter", "style"),
             Output("edu-filter", "style"),
             Output("job-filter", "style")],
            Input("theme-store", "data")
        )
        def update_filter_styles(current_theme):
            style = self.get_input_style(current_theme)
            return style, style, style

        @self.app.callback(
            [Output("gender-filter", "className"),
             Output("edu-filter", "className"),
             Output("job-filter", "className")],
            Input("theme-store", "data")
        )
        def update_dropdown_class(theme):
            class_name = "dark-dropdown" if theme == "Ciemny" else ""

            return class_name, class_name, class_name

    def get_input_style(self, current_theme):
        if current_theme == "Ciemny":
            return {
                "backgroundColor": "#2a2a2a",
                "color": "white",
                "border": "1px solid #444"
            }
        else:  # Jasny
            return {
                "backgroundColor": "white",
                "color": "black"
            }

    def run(self, debug: bool = True, host: str = '127.0.0.1', port: int = 8050):
        """Uruchamia aplikację dashboardu."""
        # Najpierw spróbuj załadować dane. Jeśli się nie uda, zakończ działanie.
        if not self.load_data():
            print("❌ Nie udało się załadować danych. Zamykanie aplikacji...")
            return

        # Konfiguracja
        self.setup_layout()
        self.setup_callbacks()

        # Uruchom serwer Dash
        print(f"🚀 Uruchamianie dashboardu pod adresem http://{host}:{port}")
        self.app.run(debug=debug, host=host, port=port)

dashboard = StudentPerformanceDashboard()
server = dashboard.server

# Uruchomienie aplikacji
if __name__ == '__main__':
    dashboard = StudentPerformanceDashboard()
    dashboard.run(debug=True)

