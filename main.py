from data_loader import download_data_if_needed

# Pobieranie danych
download_data_if_needed()

import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Wczytaj dane
df = pd.read_csv("data/student_habits_performance.csv")  # Upewnij się, że plik istnieje

# Inicjalizacja aplikacji Dash
app = dash.Dash(__name__)
app.title = "Student Habits vs Academic Performance"

# Lista opcji dla dropdownów
gender_options = [{'label': s, 'value': s} for s in df['gender'].unique()]
edu_options = [
    {'label': e, 'value': e} for e in df['parental_education_level'].dropna().unique()
]

# Layout aplikacji
app.layout = html.Div([
    html.H1("📊 Student Habits vs Academic Performance", style={"textAlign": "center"}),

    html.Div([
        html.Label("Płeć:"),
        dcc.Dropdown(id="gender-filter", options=gender_options, multi=True, placeholder="Wybierz płeć"),

        html.Label("Wykształcenie rodziców:"),
        dcc.Dropdown(id="edu-filter", options=edu_options, multi=True, placeholder="Wybierz poziom edukacji"),

        html.Label("Zakres godzin nauki (na dzień):"),
        dcc.RangeSlider(id="study-hours-slider",
                        min=0, max=10, step=1,
                        marks={i: str(i) for i in range(0, 11)},
                        value=[1, 5])
    ], style={"columnCount": 2, "padding": "20px"}),

    dcc.Graph(id="scatter-plot"),
    dcc.Graph(id="box-plot"),
    dcc.Graph(id="heatmap")
])

# Callback do aktualizacji wykresów
@app.callback(
    [Output("scatter-plot", "figure"),
     Output("box-plot", "figure"),
     Output("heatmap", "figure")],
    [Input("gender-filter", "value"),
     Input("edu-filter", "value"),
     Input("study-hours-slider", "value")]
)
def update_graphs(selected_gender, selected_edu, study_hours_per_day):
    filtered_df = df.copy()
    if selected_gender:
        filtered_df = filtered_df[filtered_df['gender'].isin(selected_gender)]
    if selected_edu:
        filtered_df = filtered_df[filtered_df['parental_education_level'].isin(selected_edu)]
    filtered_df = filtered_df[(filtered_df['study_hours_per_day'] >= study_hours_per_day[0]) & (filtered_df['study_hours_per_day'] <= study_hours_per_day[1])]

    scatter_fig = px.scatter(
        filtered_df, x="study_hours_per_day", y="exam_score", color="gender",
        hover_data=['social_media_hours', 'sleep_hours'],
        title="Wpływ czasu nauki na wynik egzaminu"
    )

    box_fig = px.box(
        filtered_df, x="gender", y="exam_score", color="gender",
        title="Rozkład wyników egzaminu względem płci"
    )

    heatmap_df = filtered_df[['study_hours_per_day', 'sleep_hours', 'social_media_hours', 'exam_score']].corr()
    heatmap_fig = px.imshow(
        heatmap_df, text_auto=True,
        title="Korelacje między cechami"
    )

    return scatter_fig, box_fig, heatmap_fig

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)
