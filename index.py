import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import data_scrapping


# Connect to app.py file 
from app import app
from app import server

# Connect to the app pages
from apps import statistics, explorer

link_style = {'font-size':'24px','font-color':'yellow','margin':'5px','border':'2px solid black'}
top_style = {'background':'black', 'width':'100%','height':'10%'}

app.layout = html.Div([
	# Hidden div inside the app that stores the intermediate value
	dbc.Row(dbc.Col(html.Div(id='intermediate-value', style={'display': 'none'}))),
	
	# Input for user id
	dbc.Row([
		dbc.Col(dcc.Input(id = 'imdb_id', value="ur67399547" , type='text', style={"width":"100%"})),
		
		dbc.Col(html.Div([
							dcc.Link('Statistics',href='/apps/statistics',style=link_style),
							dcc.Link('Movies explorer', href='/apps/explorer',style=link_style),
						]),
				style={'display': 'flex','justify-content': 'center'}),

		dbc.Col(dcc.Location(id='url', refresh = False, pathname='')),
		], id="top", style=top_style),
	
	html.Div(id='page_content', children=[])
])


@app.callback(
	Output('intermediate-value','children'),
	Input('imdb_id','value'))
def create_df(imdb_id):
	df = data_scrapping.build_df(imdb_id.strip())
	return df.to_json()


@app.callback(
	Output('page_content','children'),
	Input('url','pathname'))
def display_page(pathname):
	if pathname == '/apps/statistics':
		return statistics.layout
	if pathname == '/apps/explorer':
		return explorer.layout
	else :
		return statistics.layout

if __name__ == '__main__':
    app.run_server(debug=False)