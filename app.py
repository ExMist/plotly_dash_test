import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
from waitress import serve
import requests
from datetime import datetime

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

# Новая карточка для реального времени
card4 = dbc.Card(
    [
        dbc.CardHeader("Реальное время: Цена Bitcoin"),
        dbc.CardBody(
            [
                dcc.Graph(
                    id='live-bitcoin-chart',
                    figure={
                        'data': [],
                        'layout': go.Layout(
                            title="Цена Bitcoin (USD)",
                            xaxis=dict(title='Время'),
                            yaxis=dict(title='Цена (USD)'),
                            margin=dict(l=40, r=20, t=40, b=40),
                        )
                    }
                ),
                dcc.Interval(
                    id='interval-component',
                    interval=10*1000,  # Обновление каждые 10 секунд
                    n_intervals=0
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
        ),dbc.Row(
            [
                dbc.Col(card3, md=6),
                dbc.Col(card4, md=6),
            ],
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

# Callback для обновления графика Bitcoin в реальном времени
@app.callback(
    Output('live-bitcoin-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_bitcoin_price(n):
    try:
        # Запрос к CoinGecko API для получения текущей цены Bitcoin
        response = requests.get('https://api.coingecko.com/api/v3/simple/price',
                                params={'ids': 'bitcoin', 'vs_currencies': 'usd'})
        data = response.json()
        price = data['bitcoin']['usd']
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Создание DataFrame для графика
        df_live = pd.DataFrame({
            'Время': [timestamp],
            'Цена': [price]
        })
        
        # Чтение текущих данных графика из хранилища (если используется dcc.Store)
        # Здесь мы будем просто добавлять данные в глобальную переменную
        if not hasattr(update_bitcoin_price, "history"):
            update_bitcoin_price.history = pd.DataFrame(columns=['Время', 'Цена'])
        
        update_bitcoin_price.history = update_bitcoin_price.history.append(df_live, ignore_index=True)
        
        # Ограничение истории до последних 30 точек
        update_bitcoin_price.history = update_bitcoin_price.history.tail(30)
        
        # Создание фигуры графика
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=update_bitcoin_price.history['Время'],
                    y=update_bitcoin_price.history['Цена'],
                    mode='lines+markers',
                    name='Bitcoin'
                )
            ],
            layout=go.Layout(
                title="Цена Bitcoin (USD)",
                xaxis=dict(title='Время'),
                yaxis=dict(title='Цена (USD)'),
                margin=dict(l=40, r=20, t=40, b=40),
            )
        )
        return fig
    except Exception as e:
        # В случае ошибки возвращаем пустую фигуру с сообщением
        return {
            'data': [],
            'layout': go.Layout(
                title="Ошибка при получении данных",
                xaxis=dict(title='Время'),
                yaxis=dict(title='Цена (USD)'),
                annotations=[
                    dict(
                        text="Не удалось получить данные из API.",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                        font=dict(size=20)
                    )
                ]
            )
        }

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
