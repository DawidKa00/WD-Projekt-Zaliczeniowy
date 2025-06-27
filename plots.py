import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Figure

from config import HEATMAP_NUMERIC_COLS


def create_scatter_plot(filtered_df: pd.DataFrame, template: str) -> Figure:
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

def create_box_plot(filtered_df: pd.DataFrame, template: str) -> Figure:
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

def create_heatmap(filtered_df: pd.DataFrame, template: str) -> Figure:
    """Tworzy mapę ciepła korelacji."""
    # Jeśli przefiltrowane dane są puste, zwróć pusty wykres z informacją
    if filtered_df.empty:
        return px.imshow([[0]], title="Korelacje między cechami (Brak danych)")

    # Sprawdzenie, które z tych kolumn faktycznie istnieją w DataFrame
    available_columns = [col for col in HEATMAP_NUMERIC_COLS if col in filtered_df.columns]

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

def create_exam_score_histogram(filtered_df: pd.DataFrame, template: str) -> Figure:
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

def create_bar_avg_score_by_edu(filtered_df: pd.DataFrame, template: str) -> Figure:
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

def create_sleep_vs_score_lineplot(filtered_df: pd.DataFrame, template: str) -> Figure:
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

def create_attendance_violin_plot(filtered_df: pd.DataFrame, template: str) -> Figure:
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

def create_job_sunburst_chart(filtered_df: pd.DataFrame, template: str) -> Figure:
    # """Tworzy wykres słoneczny: struktura studentów wg pracy i płci."""
    # if filtered_df.empty or 'part_time_job' not in filtered_df.columns:
    #     return go.Figure().update_layout(title="Struktura studentów: praca vs płeć (Brak danych)", template=template)
    #
    # fig = px.sunburst(
    #     filtered_df,
    #     path=['part_time_job', 'gender'],
    #     title="Struktura studentów: Status pracy i płeć"
    # )
    # fig.update_layout(template=template, font_size=12)
    # return fig

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

def create_mental_health_polar_chart(filtered_df: pd.DataFrame, template: str) -> Figure:
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
