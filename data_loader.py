import os
import zipfile

# Konfiguracja ścieżek
DATA_DIR = "data"
CSV_FILENAME = "student_habits_performance.csv"
KAGGLE_DATASET = "jayaantanaath/student-habits-vs-academic-performance"
KAGGLE_ZIP = "student-habits-vs-academic-performance.zip"

def download_data_if_needed() -> None:
    """Sprawdza, czy plik z danymi istnieje, i pobiera go w razie potrzeby"""
    if not os.path.exists(os.path.join(DATA_DIR, CSV_FILENAME)):
        print("📥 Dane nie znalezione lokalnie – rozpoczynam pobieranie z Kaggle...")

        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists('kaggle.json'):
            print("❌ Nie znaleziono pliku kaggle.json w katalogu głównego projektu – potrzebne do pobierania danych z Kaggle.")
            return
        os.environ['KAGGLE_CONFIG_DIR'] = os.getcwd()

        try:
            # Pobierz dataset
            os.system(f"kaggle datasets download -d {KAGGLE_DATASET} -p {DATA_DIR}")

            # Rozpakuj plik ZIP
            with zipfile.ZipFile(os.path.join(DATA_DIR, KAGGLE_ZIP), 'r') as zip_ref:
                zip_ref.extractall(DATA_DIR)

            print("✅ Dane zostały pobrane i rozpakowane.")
        except Exception as e:
            print("❌ Błąd podczas pobierania danych:", e)
    else:
        print("✅ Dane już istnieją lokalnie.")
