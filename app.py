import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import data_scrapping
import plotly.express as px
import plotly.graph_objects as go


#----------------- Global variables --------------------------------------
imdb_id = "ur67399547"

empty_template = {"layout": {"xaxis": {"visible": False},
    						 "yaxis": {"visible": False},
                             "annotations": [
                {"text": "No valid user id",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 28}}
                ]
    }
}

img_style = {"width":"8%","margin":"1%"}

#-------------------Loading css and Lauching app -------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

#---------------- App Layout ------------------------------------

app.layout = html.Div(children=
	[
		# Hidden div inside the app that stores the intermediate value
		dbc.Row(dbc.Col(html.Div(id='intermediate-value', style={'display': 'none'}))),
		dbc.Row(dbc.Col(html.H1("IMDd Dashboard", style={"textAlign":"center"}))),
		dbc.Row(dbc.Col(dcc.Input(id = 'imdb_id', value='ur67399547' , type='text', style={"width":"20%"}))),
		dbc.Row(
			[
				dbc.Col(dcc.Graph(id='director_1')),
				dbc.Col(dcc.Slider(id='director_slider', min = 1, max = 25, marks={str(i): str(i) for i in range(25)}, value= 5, vertical=True), width = 1),
				dbc.Col(dcc.Graph(id='director_2')),
			]
		),
		dbc.Row(
			[
				dbc.Col(dcc.Graph(id='actor_1')),
				dbc.Col(dcc.Slider(id='actor_slider', min = 1, max = 25, marks={str(i): str(i) for i in range(25)}, value= 5, vertical=True), width = 1),
				dbc.Col(dcc.Graph(id='actor_2')),
			]
		),
		dbc.Row(dbc.Col(dcc.Graph(id='year_hist'))),
		dbc.Row(
			[
				dbc.Col(dcc.Graph(id='note_pie')),
				dbc.Col(dcc.Graph(id='type_pie')),
				dbc.Col(dcc.Graph(id='genre_pie')),
			]
		),
		dbc.Row(
			[ 
				dbc.Col(html.H2("Movies explorer")),
			]
		),
		dbc.Row(
			[
				dbc.Col(dcc.Checklist(id="type_checklist",
									  options=[{'label': 'Movie', 'value': 'Movie'},
            									{'label': 'Serie', 'value': 'Serie'}],
            						  value=['Movie','Serie'])),
				dbc.Col(dcc.Dropdown(id="director_dropdown",value=[],multi=True))
			]
		),
		dbc.Row(id="poster_row"),
	]
)

#---------------- Callbacks --------------------------------------
@app.callback(
	Output('intermediate-value','children'),
	Output('year_hist','figure'),
	Output('note_pie','figure'),
	Output('type_pie','figure'),
	Output('genre_pie','figure'),
	Output('director_dropdown','options'),
	Input('imdb_id','value')
	)
def create_df(input_value):
	df = data_scrapping.build_df(input_value.strip())

	if df.shape[0] == 0 :
		year_hist = empty_template
		note_pie = empty_template
		type_pie = empty_template
		genre_pie = empty_template
	else :

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

		director_options =  [{"label":i,"value":i} for i in df.Director.unique()]


	return df.to_json(), year_hist, note_pie, type_pie, genre_pie, director_options

@app.callback(
	Output('director_1', 'figure'),
	Output('director_2', 'figure'),
	Input('intermediate-value','children'),
	Input('director_slider', 'value'))
def update_director(df_json,input_value):
	
	df = pd.read_json(df_json)

	if df.shape[0] ==0 :
		fig_1 = empty_template
		fig_2 = empty_template

	else :
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
	Input('intermediate-value','children'),
	Input('actor_slider', 'value'))
def update_actor(df_json,input_value):

	df = pd.read_json(df_json)

	if df.shape[0] == 0 :
		fig_1 = empty_template
		fig_2 = empty_template

	else:
		df_2 = pd.melt(df, id_vars = ['Name','User_note'], value_vars = ['Actor_1','Actor_2','Actor_3','Actor_4']).rename({"value":"Actor"},axis=1)

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

@app.callback(
	Output('poster_row','children'),
	Input('intermediate-value','children'),
	Input('type_checklist','value'),
	Input('director_dropdown','value'))
def update_images(df_json,type_list,director_list):
	df = pd.read_json(df_json)
	df = df[df['Type'].isin(type_list)]
	if len(director_list) != 0 :
		df = df[df['Director'].isin(director_list)]

	urls = df.sort_values(['User_note','IMDB_note'],ascending=False)["Poster_url"].values
	to_return = [html.Img(id="img_".format(i),src=urls[i],style=img_style) for i in range(len(urls))]
	return to_return

if __name__ == '__main__':
	app.run_server(debug=True)