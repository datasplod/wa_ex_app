import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px
import numpy as np
from numpy import log10
from dash.dependencies import Input, Output

#https://bootswatch.com #theme from here link with name
#or download .min version and add to assets folder in same folder as .py script
#https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/

#create plots
#path = r"C:\Users\nw431\OneDrive - University of Exeter\1_PhD Research\Project1_Carbon Model\Seagrass env variables\1_Environmental_variables\notebooks\outputs\geo_exposures_by_ecoregion.csv"
path = "geo_exposures_by_ecoregion.csv"
df = pd.read_csv(path)
#df['Log_Exposure'] = np.round(log10(df['exposure']), 2) #create log columns to plot
#df['Log_Extremes'] = np.round(log10(df['extr_exposure']), 2) #create log columns to plot
df.rename(columns = {'extr_exposure':'extremes'}, inplace = True)
df['Exposure (log)'] = np.round(log10(df['exposure']), 2) #create log columns to plot
df['Extremes (log)'] = np.round(log10(df['extremes']), 2)


#scatter plot
scatter = px.scatter(
    df, 
    x = 'exposure', 
    y = 'extremes', 
    color = 'ECOREGION', 
    template = 'simple_white',
    #trendline="ols",
    #trendline_scope="overall"
    title = 'Correlation between exposure and extreme values'
)
scatter.update_layout(showlegend = False)

#create the app

app = dash.Dash(__name__,
external_stylesheets=[dbc.themes.BOOTSTRAP])

#extract values for ecoregion dropdown
exp_dropdown = df['ECOREGION'].unique()
opts = [{'label': i, 'value': i} for i in exp_dropdown]

#prepare dataset for exposure type dropdown

df_melt = pd.melt(df, id_vars =['Dataset_ID', 'Lat', 'Long', 'ECOREGION', 'Site_name'], value_vars =['Exposure (log)', 'Extremes (log)'], var_name = 'exp_type')
exp_type = df_melt['exp_type'].unique()
top_opts = [{'label':i, 'value':i} for i in exp_type]

app.layout = html.Div([
        dbc.Row(dbc.Col(html.H1("Seagrass Exposure Visualisation"),
                        #width={'size': 6, 'offset': 4},
                        width = 4,
                        className="text-center"
                        ),
                        justify = 'center'
                ),
        dbc.Row(dbc.Col(html.H5("A dashboard to visualise the outputs of the wave exposure calculation for Zostera marina seagrass sites"),
                        #width={'size': 3, 'offset': 4},
                        width =4,
                        className="text-center"
                        ),
                        justify='center'
                ),  
        dbc.Row(
            [               
                dbc.Col(html.Div([html.Br(),"1. Select whether to view exposure or extreme exposures on the map", html.Br(),
                "2. Pan and zoom around the map to view the exposure for Zostera marina sites", html.Br(), 
                "3. Select an eco-region on the right to compare the distribution of exposure to all other sites"]
                                 ),
                        width={'size':5, 'offset':1}
                        ),
                        
                dbc.Col(html.Div("Select an eco-region"
                                 ),
                        width={'size':6, 'offset':8}
                        )
                
            ],
            align="center",
            justify = 'right' 
        ), 
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id = 'dropdown', options = opts, value = exp_dropdown[0]
                            ),
                        width={'size': 4,  "offset": 8, 'order': 2}
                        ),
                dbc.Col(dcc.Dropdown(
                    id = 'exp_dpdn', 
                    options = top_opts,
                    value = exp_type[0]
                            ),
                        width={'size': 4,  "offset": 0, 'order': 2},
                        #clearable = False
                        align = 'start'
                        ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id = 'map', figure = {}),
                        width=8, 
                        lg={'size': 8,  "offset": 0, 'order': 'first'},
                        #style={'height':'100%', 'background-color':'darkblue'},
                        ),
                   
                dbc.Col(dcc.Graph(id='hist-graph', figure={}),
                        width=4, lg={'size': 4,  "offset": 0, 'order': 'last'},
                        #style={'height':'100%', 'background-color':'darkblue'},
                        ),
            ],
            className="g-0",
            #style = {'height':'100%'}
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(id = 'scatter', figure = scatter),
            width = 4, lg = {'size': 4,  "offset": 8},
            )
        )
])

# Set up the callback function
#first callback
@app.callback(
    Output('map', 'figure'),
    Input('exp_dpdn', 'value')
)

def select_exp(type):
    df_e = df_melt.copy()
    df_e  = df_melt[df_melt.exp_type == type]
    
    map = px.scatter_mapbox(df_e, lat='Lat', 
                        lon='Long', 
                        color = 'value',
                        center=dict(lat=50.3, lon=-5), 
                        zoom=1, 
                        hover_name = 'Site_name',
                        hover_data = ('Site_name', 'value'),
                        mapbox_style="stamen-terrain",
                        color_continuous_scale="viridis"
                       )
    map.update_traces(marker={'size': 15}, opacity = 0.75)
    #map.update_layout({'legend_orientation':'h'})
    map.update_layout(
        legend_orientation='h', 
        uirevision="Don't change",
        margin_r= 0, margin_l = 0, margin_t = 0, margin_b = 0
        )   
    #return the mapbox map with values as necessary
    return map

@app.callback(
    Output(component_id='hist-graph', component_property='figure'),
    Input(component_id='dropdown', component_property='value')
)

def update_graph(selected_region):
    df_f= df.copy()
    df_f['Ecoregion'] = np.where(df['ECOREGION']==selected_region, 'selected <br>region', 'all')
    hist_fig = px.histogram(df_f,
                       x='Exposure (log)', 
                       nbins = 15,
                       color='Ecoregion',
                       labels = {'Exposure (log)': 'Exposure (log)', 'count':'frequency'},
                       color_discrete_sequence=("darkblue", 'orange'),
                       template="simple_white",
                       #title=f'Exposure distribution in {selected_region}'
                       )
    hist_fig.update_layout(bargap = 0.03, legend = dict(
        x = 0.85,
        y = 1,
        traceorder = 'normal',
    ))
    
    return hist_fig


if __name__ == "__main__":
    app.run_server(debug = False)