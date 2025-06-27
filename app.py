import dash
from dash import html
import dash_bootstrap_components as dbc

import data_manager
from layout import create_layout, create_error_layout
from callbacks import register_callbacks
from config import HOST, PORT

# Załaduj dane
data_manager.download_data_if_needed()
df = data_manager.load_validated_data()

# Ustal zawartość strony na podstawie danych
page_content = create_layout(df) if df is not None else create_error_layout()

# Zainicjuj aplikację Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True
)
app.title = "Nawyki studentów a wyniki w nauce"
server = app.server

# Ustaw główny i kompletny layout aplikacji
app.layout = html.Div([
    # Linkowanie arkusza stylów
    html.Link(id='main-stylesheet', rel='stylesheet', href=''),

    # Właściwa zawartość strony (dashboard lub strona błędu)
    page_content
])

# Zarejestruj callbacki
if df is not None:
    register_callbacks(app, df)

# Uruchom serwer
if __name__ == '__main__':
    print(f"🚀 Dashboard pod http://{HOST}:{PORT}")
    app.run(debug=True, host=HOST, port=PORT)