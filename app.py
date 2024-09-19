import dash
from dash import dcc, html, Output, Input
import plotly.graph_objs as go
import redis
import numpy as np
import time
import dash_table
import psycopg2

r = redis.Redis(host='redis', port=6379, db=0)

app = dash.Dash(__name__)
server = app.server

def get_postgres_data():
    conn = psycopg2.connect("dbname=test user=admin password=admin host=postgres")
    cur = conn.cursor()
    cur.execute("SELECT name, email FROM test_data limit 100")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

index_layout = html.Div([
    dcc.Input(id='input-points', type='number', placeholder='Введите количество точек', value=1000),
    html.Button("Сгенерировать точки", id='generate-button'),
    html.Button("Отобразить график", id='plot-button'),
    html.Button("Только таблица", id='table-button'),
    dcc.Link('Перейти к таблице из PostgreSQL', href='/postgres-graph'),
    html.H3(id='key-count-output', children="Общее количество ключей в Redis: 0"),
    dcc.Graph(id='graph', style={'display': 'none'}),
    html.Div(id='output'),
    dash_table.DataTable(id='table-output', columns=[{"name": "Индекс", "id": "index"}, {"name": "Значение", "id": "value"}]),
    html.H4(id='time-output', children="Время формирования таблицы: 0.00 секунд", style={'margin-top': '20px'})
])

postgres_layout = html.Div([
    html.H1("Таблица из PostgreSQL"),
    dash_table.DataTable(id='postgres-data', columns=[{"name": "Индекс", "id": "index"}, {"name": "Значение", "id": "value"}]),
    html.H4(id='postgres-time-output', children="Время загрузки данных: 0.00 секунд", style={'margin-top': '20px'}),
    dcc.Link('Вернуться на главную', href='/')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/postgres-graph':
        return postgres_layout
    else:
        return index_layout

@app.callback(
    Output('output', 'children'),
    Output('key-count-output', 'children'),
    Input('generate-button', 'n_clicks'),
    Input('input-points', 'value')
)
def generate_points(n_clicks, num_points):
    if n_clicks is None or num_points is None:
        return "", "Общее количество ключей в Redis: 0"

    r.flushdb()
    start_time = time.time()
    
    pipeline = r.pipeline()
    for i in range(num_points):
        value = np.random.rand()
        pipeline.set(f"point:{i}", value)

    pipeline.execute()

    generation_time = time.time() - start_time
    keys = r.keys('point:*')
    key_count = len(keys)

    output_message = f"Сгенерировано {num_points} точек за {generation_time:.2f} секунд."
    
    return output_message, f"Общее количество ключей в Redis: {key_count}"

@app.callback(
    Output('graph', 'figure'),
    Output('graph', 'style'),
    Output('table-output', 'data'),
    Output('time-output', 'children'),
    Input('plot-button', 'n_clicks'),
    Input('table-button', 'n_clicks')
)
def update_graph_and_table(plot_clicks, table_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return {}, {'display': 'none'}, [], "Время формирования таблицы: 0.00 секунд"

    triggered_button = ctx.triggered[0]['prop_id'].split('.')[0]

    start_time = time.time()
    keys = r.keys('point:*')
    values = r.mget(keys)
    values = [float(value) for value in values if value is not None]

    retrieval_time = time.time() - start_time

    if triggered_button == 'plot-button':
        figure = go.Figure(data=go.Scatter(y=values, mode='lines+markers'))
        figure.update_layout(title='График значений из Redis',
                             xaxis_title='Индекс',
                             yaxis_title='Значение')
        return figure, {'display': 'block'}, [{"index": i, "value": values[i]} for i in range(len(values))], f"Время формирования таблицы: {retrieval_time:.2f} секунд"
    
    elif triggered_button == 'table-button':
        return {}, {'display': 'none'}, [{"index": i, "value": values[i]} for i in range(len(values))], f"Время формирования таблицы: {retrieval_time:.2f} секунд"

@app.callback(
    Output('postgres-data', 'data'),
    Output('postgres-time-output', 'children'),  
    Input('url', 'pathname')
)
def load_postgres_data(pathname):
    if pathname == '/postgres-graph':
        start_time = time.time()

        data = get_postgres_data()
        retrieval_time = time.time() - start_time 

        table_data = [{'index': i, 'value': f"{name} - {email}"} for i, (name, email) in enumerate(data)]
        
        return table_data, f"Время загрузки данных: {retrieval_time:.2f} секунд"
    
    return [], "Время загрузки данных: 0.00 секунд" 

if __name__ == '__main__':
    app.run_server(debug=True)