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

server = app.server

#---------------- Simple plots (no callbacks) ------------------------------------
year_hist = px.histogram(df,x="Year",nbins=100, title="Years histogram")

note_pie = px.pie(df, names='User_note',title='Note repartition')
note_pie.update_traces(textposition='inside', textinfo='percent+label')

type_pie = px.pie(df, names='Type',title='Type repatition')
type_pie.update_traces(textposition='inside', textinfo='percent+label')

L_genre_temp = [i.split() for i in df['Genre'].values]
L_genre = [x for j in L_genre_temp for x in j]

df_genre = pd.DataFrame(L_genre).rename({0:'Genre'},axis=1)
genre_pie = px.pie(df_genre, names = "Genre", title="Genre repartition")
genre_pie.update_traces(textposition='inside', textinfo='percent+label', showlegend= False)

#---------------- App Layout ------------------------------------

app.layout = html.Div(children=
    [
    	dbc.Row(dbc.Col(html.H1("IMDd Dashboard", style={"textAlign":"center"}))),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='director_1')),
                dbc.Col(dcc.Slider(id='director_slider', min = 1, max = min(25,df['Director'].nunique()), marks={str(i): str(i) for i in range(min(25,df['Director'].nunique()))}, value= 5, vertical=True), width = 1),
                dbc.Col(dcc.Graph(id='director_2')),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='actor_1')),
                dbc.Col(dcc.Slider(id='actor_slider', min = 1, max = min(25,df_2['Actor'].nunique()), marks={str(i): str(i) for i in range(min(25,df_2['Actor'].nunique()))}, value= 5, vertical=True), width = 1),
                dbc.Col(dcc.Graph(id='actor_2')),
            ]
        ),
        dbc.Row(dbc.Col(dcc.Graph(id='year_hist',figure=year_hist))),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='note_pie', figure=note_pie)),
                dbc.Col(dcc.Graph(id='type_pie', figure=type_pie)),
                dbc.Col(dcc.Graph(id='genre_pie', figure=genre_pie)),
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
                fill_color='#1f77b4',
                font=dict(color='white'),
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
                fill_color='#1f77b4',
                font=dict(color='white'),
                align='left'),
    cells=dict(values=[df_actors_note.index, round(df_actors_note.User_note,2)],
               fill_color='lavender',
               align='left'))
        ])
    fig_2.update_layout(title = "Top rated Actors" , transition_duration=500)

    return fig_1,fig_2

#@app.callback(
#	Output('year_hist','figure'),
#	Output('note_pie','figure'),
#	Output('type_pie','figure'),
#	Output('genre_pie','figure'),
#	Input())


if __name__ == '__main__':
    app.run_server(debug=True)
