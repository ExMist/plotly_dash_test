import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px  # Убедитесь, что импортирован Plotly Express
import pandas as pd
import dash_bootstrap_components as dbc
from waitress import serve
from datetime import datetime
import random

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
    brand="RISKSCONS",
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

# Новая карточка для синтетических данных
card4 = dbc.Card(
    [
        dbc.CardHeader("Реальное время: Синтетические данные"),
        dbc.CardBody(
            [
                dcc.Graph(
                    id='live-synthetic-chart',
                    figure={
                        'data': [],
                        'layout': go.Layout(
                            title="Синтетические данные",
                            xaxis=dict(title='Время'),
                            yaxis=dict(title='Значение'),
                            margin=dict(l=40, r=20, t=40, b=40),
                        )
                    }
                ),
                dcc.Interval(
                    id='interval-component',
                    interval=5*1000,  # Обновление каждые 5 секунд
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
        ),
        dbc.Row(
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
                    "© 2024 Конс.Отчетность",
                    className="text-center",
                    style={"padding": "20px 0"}
                ),
                width=12
            )
        ),
    ],
    fluid=True,
)

# Callback для обновления графика с синтетическими данными в реальном времени
@app.callback(
    Output('live-synthetic-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_synthetic_data(n):
    try:
        # Инициализируем историю данных при первом запуске
        if not hasattr(update_synthetic_data, "history"):
            update_synthetic_data.history = pd.DataFrame(columns=['Время', 'Значение'])
            update_synthetic_data.current_value = 100  # Стартовое значение

        # Генерируем новое значение (например, случайное блуждание)
        delta = random.uniform(-5, 5)  # Случайное изменение между -5 и 5
        new_value = update_synthetic_data.current_value + delta
        update_synthetic_data.current_value = new_value

        # Текущий временной штамп
        timestamp = datetime.now().strftime('%H:%M:%S')

        # Добавляем новое значение в историю
        new_data = pd.DataFrame({
            'Время': [timestamp],
            'Значение': [new_value]
        })
        update_synthetic_data.history = pd.concat([update_synthetic_data.history, new_data], ignore_index=True)

        # Ограничиваем историю до последних 30 точек
        update_synthetic_data.history = update_synthetic_data.history.tail(30)

        # Создание фигуры графика
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=update_synthetic_data.history['Время'],
                    y=update_synthetic_data.history['Значение'],
                    mode='lines+markers',
                    name='Синтетические данные'
                )
            ],
            layout=go.Layout(
                title="Синтетические данные в реальном времени",
                xaxis=dict(title='Время'),
                yaxis=dict(title='Значение'),
                margin=dict(l=40, r=20, t=40, b=40),
            )
        )
        return fig
    except Exception as e:
        # В случае ошибки возвращаем пустую фигуру с сообщением
        return {
            'data': [],
            'layout': go.Layout(
                title="Ошибка при генерации данных",
                xaxis=dict(title='Время'),
                yaxis=dict(title='Значение'),
                annotations=[
                    dict(
                        text="Не удалось сгенерировать данные.",
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
            