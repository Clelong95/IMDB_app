import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import data_scrapping
import plotly.express as px
import plotly.graph_objects as go


#----------------- Loading Data --------------------------------------
imdb_id = "ur67399547"
df = data_scrapping.build_df(imdb_id)

df_2 = pd.melt(df, id_vars = ['Name','User_note'], value_vars = ['Actor_1','Actor_2','Actor_3','Actor_4']).rename({"value":"Actor"},axis=1)

#-------------------Loading css and Lauching app -------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#---------------- Simple plots (no callbacks) ------------------------------------
year_hist = px.histogram(df,x="Year",nbins=100, title="Years histogram")
note_pie = px.pie(df, names='User_note',title='Note repartition')
#---------------- App Layout ------------------------------------

app.layout = html.Div(
    [
        dbc.Row(dbc.Col(dcc.Graph(id='year_hist',figure=year_hist))),
        dbc.Row(
            [
                dbc.Col(dcc.Slider(id='director_slider', min = 1, max = min(25,df['Director'].nunique()), marks={str(i): str(i) for i in range(min(25,df['Director'].nunique()))}, value= 5, vertical=True), width = 1),
                dbc.Col(dcc.Graph(id='director_1')),
                dbc.Col(dcc.Graph(id='director_2')),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Slider(id='actor_slider', min = 1, max = min(25,df_2['Actor'].nunique()), marks={str(i): str(i) for i in range(min(25,df_2['Actor'].nunique()))}, value= 5, vertical=True), width = 1),
                dbc.Col(dcc.Graph(id='actor_1')),
                dbc.Col(dcc.Graph(id='actor_2')),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='note_pie', figure=note_pie)),
                dbc.Col(dcc.Graph()),
                dbc.Col(dcc.Graph()),
            ]
        )

    ]
)

#---------------- Callbacks --------------------------------------
@app.callback(
    Output('director_1', 'figure'),
    Output('director_2', 'figure'),
    Input('director_slider', 'value'))
def update_director(input_value):

    df_directors = pd.DataFrame(df['Director'].value_counts()[:input_value].drop('None')).sort_values('Director',ascending=True).rename({'Director':'Number of movies'},axis=1)
    df_directors.index.name = "Director"
    fig_1 = px.bar(df_directors, x="Number of movies", orientation="h", title = "Most watched Directors")
    fig_1.update_layout(transition_duration=500)

    df_directors_note = pd.DataFrame(df[df['Director'].isin(df_directors.index)].groupby('Director').mean()['User_note']).sort_values('User_note',ascending=False)
    fig_2 = go.Figure(data=[go.Table(
    header=dict(values=['Director', 'Average Note'],
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df_directors_note.index, round(df_directors_note.User_note,2)],
               fill_color='lavender',
               align='left'))
        ])
    fig_2.update_layout(title = "Top rated Directors" , transition_duration=500)

    return fig_1,fig_2

@app.callback(
    Output('actor_1', 'figure'),
    Output('actor_2','figure'),
    Input('actor_slider', 'value'))
def update_actor(input_value):

    df_actors = pd.DataFrame(df_2['Actor'].value_counts()[:input_value]).sort_values('Actor',ascending=True).rename({'Actor':'Number of movies'},axis=1)
    df_actors.index.name = "Actor"
    fig_1 = px.bar(df_actors, x="Number of movies", orientation="h", title  ="Most watched Actors")
    fig_1.update_layout(transition_duration=500)

    df_actors_note = pd.DataFrame(df_2[df_2['Actor'].isin(df_actors.index)].groupby('Actor').mean()['User_note']).sort_values('User_note',ascending=False)

    fig_2 = go.Figure(data=[go.Table(
    header=dict(values=['Actor', 'Average Note'],
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df_actors_note.index, round(df_actors_note.User_note,2)],
               fill_color='lavender',
               align='left'))
        ])
    fig_2.update_layout(title = "Top rated Actors" , transition_duration=500)

    return fig_1,fig_2


if __name__ == '__main__':
    app.run_server(port=8080)
