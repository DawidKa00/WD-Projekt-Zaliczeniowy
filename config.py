import os

# Konfiguracja serwera
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8050))

# Konfiguracja ścieżek do danych
DATA_DIR = "data"
CSV_FILENAME = "student_habits_performance.csv"
KAGGLE_DATASET = "jayaantanaath/student-habits-vs-academic-performance"
KAGGLE_ZIP = "student-habits-vs-academic-performance.zip"

# Lista wymaganych kolumn w zbiorze danych
REQUIRED_COLUMNS = [
    'gender', 'parental_education_level', 'study_hours_per_day',
    'exam_score', 'social_media_hours', 'sleep_hours',
    'attendance_percentage', 'part_time_job', 'mental_health_rating'
]

# Kolumny numeryczne używane w mapie ciepła
HEATMAP_NUMERIC_COLS = [
    'study_hours_per_day', 'sleep_hours', 'social_media_hours',
    'exam_score', 'attendance_percentage'
]

# Mapowanie motywów na adresy URL z dash-bootstrap-components
THEMES = {
    "Jasny": "FLATLY",
    "Ciemny": "DARKLY"
}
