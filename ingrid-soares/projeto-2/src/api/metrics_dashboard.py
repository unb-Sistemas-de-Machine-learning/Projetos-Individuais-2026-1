import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import os

# Simulação de dados: em uma aplicação real, aqui você conectaria ao banco do MLflow ou log de métricas
def get_metrics():
    # Exemplo de DataFrame de latência (poderia vir de um arquivo JSON/CSV atualizado pela API)
    return pd.DataFrame({
        'time': pd.date_range(start='2026-04-10', periods=5, freq='min'),
        'latencia': [0.12, 0.15, 0.11, 0.18, 0.14]
    })

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Observabilidade - ML Security"),
    dcc.Graph(
        id='live-update-graph',
        figure=px.line(get_metrics(), x='time', y='latencia', title="Latência de Inferência (s)")
    )
])

if __name__ == '__main__':
    # Roda em porta distinta para não conflitar com o FastAPI
    app.run_server(debug=True, port=8050)
