import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from flask import Flask
import pandas as pd
import random
from datetime import datetime

# Инициализация приложения
external_stylesheets = [dbc.themes.BOOTSTRAP]
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

# Макет приложения
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H2("Конс.Отчетность", className="text-center"),
                width=12
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='live-synthetic-chart'),
                    width=8
                ),
                dbc.Col(
                    # Чат-бот интерфейс
                    dbc.Card(
                        [
                            dbc.CardHeader("Чат-бот"),
                            dbc.CardBody(
                                [
                                    html.Div(id='chat-content', style={'height': '400px', 'overflowY': 'scroll', 'border': '1px solid #ccc', 'padding': '10px'}),
                                    dbc.InputGroup(
                                        [
                                            dbc.Input(id='chat-input', type='text', placeholder='Введите сообщение...'),
                                            dbc.Button("Отправить", id='send-button', color='primary'),
                                        ],
                                        className="mt-2",
                                    ),
                                ]
                            ),
                        ],
                        style={"height": "100%"}
                    ),
                    width=4
                ),
            ]
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
        # Компонент для обновления графика
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # обновление каждые 5 секунд
            n_intervals=0
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

# Callback для обработки чата
@app.callback(
    Output('chat-content', 'children'),
    [Input('send-button', 'n_clicks')],
    [State('chat-input', 'value'),
     State('chat-content', 'children')]
)
def update_chat(n_clicks, user_input, chat_history):
    if n_clicks is None:
        # Первоначальная загрузка, можно вернуть пустой чат
        return []
    if user_input:
        if chat_history is None:
            chat_history = []
        # Добавляем сообщение пользователя
        chat_history.append(html.Div([
            html.Strong("Вы: "),
            html.Span(user_input)
        ], style={'textAlign': 'right', 'marginBottom': '10px'}))
        
        # Генерация ответа бота (эко-бот для примера)
        bot_response = generate_bot_response(user_input)
        chat_history.append(html.Div([
            html.Strong("Бот: "),
            html.Span(bot_response)
        ], style={'textAlign': 'left', 'marginBottom': '10px'}))
        
        return chat_history
    return chat_history

def generate_bot_response(user_message):
    # Простая логика ответа бота
    return f"Вы сказали: {user_message}"

def main():
    app.run_server(host='0.0.0.0', port=8000, debug=True)

if __name__ == "__main__":
    main()