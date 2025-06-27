import os
import zipfile
from typing import List, Optional
import pandas as pd

from config import DATA_DIR, CSV_FILENAME, KAGGLE_DATASET, KAGGLE_ZIP, REQUIRED_COLUMNS


def download_data_if_needed() -> None:
    """Sprawdza, czy plik z danymi istnieje, i pobiera go w razie potrzeby"""
    if not os.path.exists(os.path.join(DATA_DIR, CSV_FILENAME)):
        print("📥 Dane nie znalezione lokalnie – rozpoczynam pobieranie z Kaggle...")

        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists('kaggle.json'):
            print("❌ Nie znaleziono pliku kaggle.json w katalogu głównego projektu – potrzebne do pobierania danych z Kaggle.")
            return None
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
            return None
    else:
        print("✅ Dane już istnieją lokalnie.")
        return None

def load_validated_data() -> Optional[pd.DataFrame]:
    """Ładuje i waliduje dane z pliku CSV."""
    csv_path = os.path.join(DATA_DIR, CSV_FILENAME)
    try:
        # Próba wczytania danych z pliku CSV
        df = pd.read_csv(csv_path)

        # Walidacja, czy w danych znajdują się wszystkie wymagane kolumny
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            print(f"❌ Brak wymaganych kolumn: {missing_columns}")
            return None

        # Sprawdzenie, czy DataFrame nie jest pusty
        if df.empty:
            print("❌ Zbiór danych jest pusty.")
            return None

        print(f"✅ Dane załadowano pomyślnie. Rozmiar: {df.shape}")
        return df

    except FileNotFoundError:
        print(f"❌ Nie znaleziono pliku CSV: {csv_path}")
        return None
    except pd.errors.EmptyDataError:
        print(f"❌ Plik CSV jest pusty: {csv_path}")
        return None
    except Exception as e:
        print(f"❌ Wystąpił nieoczekiwany błąd podczas ładowania danych: {e}")
        return None

def filter_data(df: pd.DataFrame, selected_gender: Optional[List[str]],
                selected_edu: Optional[List[str]], study_hours_range: List[int],
                selected_job: Optional[List[str]]) -> pd.DataFrame:
    """Filtruje DataFrame na podstawie wyborów użytkownika."""
    # Sprawdzenie, czy DataFrame został załadowany
    if df is None or df.empty:
        return pd.DataFrame()

    # Stworzenie kopii DataFrame, aby uniknąć modyfikacji oryginalnych danych
    filtered_df = df.copy()

    # Filtr płci
    if selected_gender:
        filtered_df = filtered_df[filtered_df['gender'].isin(selected_gender)]

    # Filtr wykształcenia rodziców
    if selected_edu:
        filtered_df = filtered_df[filtered_df['parental_education_level'].isin(selected_edu)]

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
