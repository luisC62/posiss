import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from math import sqrt


# Constant parameters
url = 'http://api.open-notify.org/iss-now.json' # ISS position API
R = 6371 # Earth radius, in km
h = 408 # Height of the ISS over sea level, in km
H = R + h # Orbit radius of the ISS, in km


app = dash.Dash(__name__)

app.layout = html.Div(className= 'maincontainer', children=[
        html.H1('Posición de la estación espacial internacional (ISS)', style = {'textAlign': 'center'}),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(id='interval-component',
                     interval=10*1000, # in milliseconds
                     n_intervals=0),
        # dcc.Store inside the app that stores the intermediate value
        dcc.Store(id='intermediate-value', storage_type='local')
        ])

@app.callback([Output('live-update-text', 'children'),
              Output('live-update-graph', 'figure'),
              Output('intermediate-value', 'data')],
              [Input('interval-component', 'n_intervals'),
               Input('intermediate-value', 'data')])
def actualizar_datos(n, data):
    df_src=pd.read_json(url)
    lat = df_src.loc['latitude', 'iss_position']
    lon = df_src.loc['longitude', 'iss_position']
    timestamp = df_src.loc['latitude', 'timestamp']
    info = 'Tiempo UTC: ' +  str(timestamp) + ', Latitud = ' + str(lat) + ', Longitud: ' + str(lon) + ', Velocidad: '
    
    if n==0:
        df_work = pd.DataFrame(columns=['latitude', 'longitude', 'timestamp', 'speed'])
        df_work = df_work.append({'latitude': lat, 'longitude': lon, 'timestamp': timestamp, 'speed': 0}, ignore_index=True)
        info = info + ' km/s'
    else: 
        df_work = pd.read_json(data)
        df_work = df_work.append({'latitude': lat, 'longitude': lon, 'timestamp': timestamp}, ignore_index=True)
        lat2 = df_work.loc[n,'latitude']
        lon2 = df_work.loc[n,'longitude']
        t2 = df_work.loc[n,'timestamp']
        lat1 = df_work.loc[n - 1,'latitude']
        lon1 = df_work.loc[n - 1,'longitude']
        t1 = df_work.loc[n - 1,'timestamp']
        delta_t = (t2 - t1).total_seconds()
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        vel = H * 3.1416 * sqrt(delta_lat**2 + delta_lon**2) / (180 * delta_t)
        velocidad = round(vel, 3)
        df_work.loc[n, 'speed'] = velocidad
        info = info + str(velocidad) + ' km/s'


    children= html.H4(info, style = {'textAlign': 'center'})
    data = df_work.to_json()
    figure = px.scatter_geo(df_work, lat='latitude', lon='longitude',
                                projection = "natural earth",
                                hover_name='timestamp',
                                hover_data= df_work,
                                width = 1600, height = 800)
    
    
     
    return children, figure, data
    


if __name__ == '__main__':
    app.run_server(debug=True)