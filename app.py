import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from waitress import serve

# Создаем простую выборку данных
df = pd.DataFrame({
    "Категория": ["A", "B", "C", "D"],
    "Значение": [4, 1, 3, 5]
})

# Дополнительные данные для разнообразия
df_line = pd.DataFrame({
    "Месяц": ["Январь", "Февраль", "Март", "Апрель"],
    "Продажи": [150, 200, 170, 220]
})

df_pie = pd.DataFrame({
    "Тип": ["Продукт 1", "Продукт 2", "Продукт 3"],
    "Доля": [45, 30, 25]
})

# Инициализация Dash-приложения с Bootstrap темой
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server  # Для Gunicorn

# Навигационная панель
navbar = dbc.NavbarSimple(
    brand="Моё Приложение Dash",
    brand_href="#",
    color="primary",
    dark=True,
    fluid=True,
)

# Карточки с информацией
card1 = dbc.Card(
    [
        dbc.CardHeader("Столбчатая диаграмма"),
        dbc.CardBody(
            [
                dcc.Graph(
                    id='bar-chart',
                    figure=px.bar(df, x='Категория', y='Значение', title="Пример столбчатой диаграммы")
                )
            ]
        ),
    ],
    style={"width": "100%", "margin-bottom": "20px"},
)

card2 = dbc.Card(
    [
        dbc.CardHeader("Линейный график"),
        dbc.CardBody(
            [
                dcc.Graph(
                    id='line-chart',
                    figure=px.line(df_line, x='Месяц', y='Продажи', title="Продажи по месяцам")
                )
            ]
        ),
    ],
    style={"width": "100%", "margin-bottom": "20px"},
)

card3 = dbc.Card(
    [
        dbc.CardHeader("Круговая диаграмма"),
        dbc.CardBody(
            [
                dcc.Graph(
                    id='pie-chart',
                    figure=px.pie(df_pie, names='Тип', values='Доля', title="Распределение продуктов")
                )
            ]
        ),
    ],
    style={"width": "100%", "margin-bottom": "20px"},
)

# Макет приложения
app.layout = dbc.Container(
    [
        navbar,
        dbc.Row(
            dbc.Col(
                html.H1("Интерактивные Визуализации с Dash", className="text-center my-4"),
                width=12
            )
        ),
        dbc.Row(
            [
                dbc.Col(card1, md=6),
                dbc.Col(card2, md=6),
            ],
            className="mb-4",
        ),
        dbc.Row(
            dbc.Col(card3, md=12),
            className="mb-4",
        ),
        dbc.Row(
            dbc.Col(
                dbc.Alert(
                    "Это Dash-приложение, запущенное в Docker с использованием Waitress и Nginx.",
                    color="secondary",
                    className="text-center",
                ),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Footer(
                    "© 2023 Моё Приложение Dash",
                    className="text-center",
                    style={"padding": "20px 0"}
                ),
                width=12
            )
        ),
    ],
    fluid=True,
)

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