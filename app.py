# app.py
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
from waitress import serve

# Создаем простую выборку данных
df = pd.DataFrame({
    "Категория": ["A", "B", "C", "D"],
    "Значение": [4, 1, 3, 5]
})

# Инициализация Dash-приложения
app = dash.Dash(__name__)

# Определение макета
app.layout = html.Div(children=[
    html.H1(children='Пример Dash-приложения'),

    html.Div(children='''
        Это Dash-приложение, запущенное в Docker с использованием Waitress и Nginx.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=px.bar(df, x='Категория', y='Значение', title="Пример графика")
    )
])

# Для Gunicorn
server = app.server

def main():
    serve(
        server,
        host='0.0.0.0',
        port=8000,
        threads=8,
        ident='my_dash_app',
        expose_tracebacks=True,
        _quiet=False,                 
    )

if __name__ == "__main__":
    main()