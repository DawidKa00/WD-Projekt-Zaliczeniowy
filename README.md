# 📊 Student Habits vs Academic Performance – Interaktywny Dashboard

## Opis projektu

Celem projektu jest stworzenie kompletnej wizualizacji danych w formie interaktywnego dashboardu z wykorzystaniem biblioteki Dash. Analizowany zbiór danych dotyczy nawyków studentów i ich wpływu na wyniki w nauce.

Dashboard zawiera przemyślaną prezentację danych, różnorodne typy wykresów oraz możliwość interakcji z użytkownikiem.

## 📁 Użyty zbiór danych

Student Habits vs Academic Performance – symulowany, realistyczny zbiór danych zawierający 1000 rekordów studentów, opisanych na podstawie m.in.:
* codziennego czasu nauki i snu,
* korzystania z social mediów i Netflixa,
* jakości diety i zdrowia psychicznego,
* obecności na zajęciach i uczestnictwa w aktywnościach dodatkowych,
* poziomu wykształcenia rodziców,
* jakości internetu,
* wyniku egzaminu (exam_score).

Zbiór nadaje się do zadań z zakresu EDA, regresji, klasyfikacji, a także do zastosowań edukacyjnych.

## 🧰 Technologie

* Python 3.x
* Dash
* Pandas
* Plotly Express

## 📈 Funkcjonalności dashboardu

* Wiele typów wykresów (scatter plot, bar chart, pie chart, histogram, boxplot, heatmap)
* Filtry interaktywne (np. wybór płci, poziomu edukacji rodziców, zakresu godzin nauki)
* Zmienna koloryzacja i formatowanie (legendy, tytuły, opisy osi)
* Responsywny układ dashboardu
* Opis i interpretacja każdego wykresu


## ▶️ Uruchomienie aplikacji lokalnie

1. Sklonuj repozytorium:

`git clone https://github.com/DawidKa00/WD-Projekt-Zaliczeniowy` \
`cd student-dashboard`

2. Zainstaluj zależności:

    `pip install -r requirements.txt`


3. Uruchom aplikację:

    `python app.py`

Dashboard będzie dostępny pod adresem http://127.0.0.1:8050/.
