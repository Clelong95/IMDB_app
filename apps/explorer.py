import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app import app

img_style = {"width":"8%","margin":"1%"}

layout = html.Div(children=
	[
		dbc.Row(
			[ 
				dbc.Col(html.H1("Movies explorer", style={"textAlign":"center"})),
			]
		),
		dbc.Row(
			[
				dbc.Col(dcc.Checklist(id="type_checklist",
									  options=[{'label': 'Movie', 'value': 'Movie'},
            									{'label': 'Serie', 'value': 'Serie'}],
            						  value=['Movie','Serie'])),
				dbc.Col(dcc.Dropdown(id="director_dropdown",value=[],multi=True)),
				dbc.Col(dcc.Dropdown(id="actor_dropdown", value=[], multi= True))
			]
		),
		dbc.Row(id="poster_row"),
	]
)

@app.callback(
	Output('director_dropdown','options'),
	Output('actor_dropdown','options'),
	Input('intermediate-value','children'))
def update_dropdowns(df_json):
	df = pd.read_json(df_json)
	director_options =  [{"label":i,"value":i} for i in df.Director.unique()]

	df_2 = pd.melt(df, id_vars = ['Name','User_note'], value_vars = ['Actor_1','Actor_2','Actor_3','Actor_4']).rename({"value":"Actor"},axis=1)
	actor_options = [{"label":i,"value":i} for i in df_2['Actor'].unique()]

	return director_options, actor_options


@app.callback(
	Output('poster_row','children'),
	Input('intermediate-value','children'),
	Input('type_checklist','value'),
	Input('director_dropdown','value'),
	Input('actor_dropdown','value'))
def update_images(df_json,type_list,director_list,actor_list):
	df = pd.read_json(df_json)
	df = df[df['Type'].isin(type_list)]
	if len(director_list) != 0 :
		df = df[df['Director'].isin(director_list)]

	if len(actor_list) !=0 :
		actor_cols = [i for i in df.columns if 'Actor' in i]
		df = df[(df[actor_cols].isin(actor_list)).any(axis="columns")]

	urls = df.sort_values(['User_note','IMDB_note'],ascending=False)["Poster_url"].values
	to_return = [html.Img(id="img_".format(i),src=urls[i],style=img_style) for i in range(len(urls))]
	return to_return