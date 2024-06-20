# Import necessary libraries
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from dash import ALL, MATCH
from dash.exceptions import PreventUpdate

import logging
import dataiku
import io
import base64
import numpy as np
import pandas as pd

from collections import OrderedDict


logger = logging.getLogger(__name__)

############################################[ FRONTEND ]#######################################

app.config.external_stylesheets = [dbc.themes.PULSE, dbc.icons.FONT_AWESOME]
colors = {'background': '#111111','text': '#7FDBFF'}
all_options = {k: v for k, v in zip(list("ABCD"), np.random.randint(1, 4, 4))}
options1 = list(all_options.keys())
index_layout = html.Div([html.H2("Index"),
		 html.Img(src="https://picsum.photos/200/300", alt="Image to display")])

data_with_none = [
    {'Firm': 'Acme', '2017': '', '2018': 5, '2019': 10, '2020': 4},
    {'Firm': 'Olive', '2017': None, '2018': 3, '2019': 13, '2020': 3},
    {'Firm': 'Barnwood', '2017': np.NaN, '2018': 7, '2019': 3, '2020': 6},
    {'Firm': 'Henrietta', '2017': 14, '2018': 1, '2019': 13, '2020': 1},
]
df = pd.DataFrame(data_with_none)
df = df.fillna('N/A').replace('', 'N/A')


dict_page_anex = {"page1": "Anexo 18",
                "page2": "Anexo 19",
                "page3": "Anexo 20",
                "page4": "Anexo 21",
                "page5": "Anexo 22",
                "page6": "Cálculos EAD",
                "page7": "Cálculos LDG",
                "page8": "Cálculos RSC",
                "page9": "Cálculos NAFIN",
                "page10": "Cálculos Irrevocables No Dispuestos",
                "page11": "Cálculos de Reservas Totales"}

nav_layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("A18", href="page1")),
            dbc.NavItem(dbc.NavLink("A19", href="page2")),
            dbc.NavItem(dbc.NavLink("A20", href="page3")),
            dbc.NavItem(dbc.NavLink("A21", href="page4")),
            dbc.NavItem(dbc.NavLink("A22", href="page5")),
            dbc.NavItem(dbc.NavLink("EAD", href="page6")),
            dbc.NavItem(dbc.NavLink("LDG", href="page7")),
            dbc.NavItem(dbc.NavLink("RSC", href="page8")),
            dbc.NavItem(dbc.NavLink("NAFIN", href="page9")),
            dbc.NavItem(dbc.NavLink("IND", href="page10")),
            dbc.NavItem(dbc.NavLink("RT", href="page11"))
        ],
        brand=[
            dbc.NavItem(
                dbc.NavLink("Cognitve Services COE - Ingestion WebApp", 
                            href = "home"))
        ],
        fluid = True,
        color = "#104B84",
        dark = True,
    )
])


def page_div(page_name: str):
    section = dict_page_anex.get(f'{page_name}')
    page_layout = html.Div(
        [
            dbc.Row(
                [
                    html.H2(
                        children=f"{section}",
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                        }
                    ),  
            dbc.Row(
                dbc.Col(html.Hr(
                    style={'borderWidth': "0.3vh",
                           "width": "100%", 
                           "backgroundColor": "#B4E1FF",
                           "opacity":"1"}),
                   width={'size':12, 'offset':0.5}
            )),
            dbc.Col(
                dbc.Row([
                    dcc.Store(id='sequential_call'),
                    dbc.Row([html.H2("Seleccione un Managed Folder"), ]),
                    dbc.Row([dcc.Dropdown(id='select_managed',
                                        options=[], 
                                        placeholder="Seleccione...", 
                                        className="dbc")]),
					html.Br(),
                    dbc.Row([html.H2("Subir un archivo al Managed Folder")]),
                    dbc.Row(
                        dcc.Upload(
                            id='upload_data',
                            children=html.Div(id='output-data-upload', children=
                            ["Arrastre y suelte o haga clic para seleccionar un archivo para cargar."]
                                            ),
                            style={
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                            },
                            multiple=True,
                            disabled=True
                            )
                        ),
					 html.Br(),
					 dbc.Row([ 
					 	dbc.Col(
							dbc.Button("Data Quality Checks",
									   color = "dark", 
									   id = "verify-button")),
						dbc.Col(
							dbc.Button("Run Scenario",
									   color = "success",
									   outline = True,
									   disabled = True,
									   id = "run-button" ))					 
					 ])
                    ],
                    justify="center",
                ),
               
                 style = {"border-right": "2px solid"}
            ),
            dbc.Col(
                dbc.Row(
                    [dbc.Row([html.H3("Listado de archivos del Managed Folder"), ]),
                     dbc.Row([html.Ul(id='file_list')])]
                ), width={"size": 5, "order": "last", "offset": 1})
            ],
            justify="rigth",
        ),
         dbc.Row(
                dbc.Col(html.Hr(
                    style={'borderWidth': "0.3vh",
                           "width": "100%", 
                           "backgroundColor": "#B4E1FF",
                           "opacity":"1"}),
                   width={'size': 10, 'offset': 1})
            ),
			html.Br(),
			
			dbc.Row([dcc.Dropdown(id = 'select_dataset',
								options = [], 
								placeholder = "Seleccione un DataSet", 
								className = "dbc")]),
			html.Br(),
			dash_table.DataTable(
				id = "table_data",
    			data = df.to_dict('records'),
    			columns = [{'id': c, 'name': c} for c in df.columns],
					style_cell_conditional=[
						{
							'if': {'column_id': c},
							'textAlign': 'left'
						} for c in ['Date', 'Region']
					],
					style_data={
						'color': 'black',
						'backgroundColor': 'white'
					},
					style_data_conditional =[
						{
							'if': {'row_index': 'odd'},
							'backgroundColor': 'rgb(220, 220, 220)',
						}
					] + [
						{
							'if': {
								'filter_query': '{{{col}}} = "N/A"'.format(col=col),
								'column_id': col
							},
							'backgroundColor': 'tomato',
							'color': 'white'
						} for col in df.columns
					],
					style_header={
						'backgroundColor': 'rgb(210, 210, 210)',
						'color': 'black',
						'fontWeight': 'bold'
					}		
			)    
    
	],
   
    style={"font-family": "Arial", "font-size": "0.9em", "text-align": "center"}
    )
    return page_layout


def make_download_button(filename, index):
    """
    Create a button associated with a dcc.Download component
    Args:
        filename: filename associated with the download component
        index: index of the button.

    Returns:
        a button associated with a dcc.Download component
    """
    download_area = dcc.Download(id={'index': index, 'type': 'dld'}, data={'base64': True})
    button = html.Button(filename, id={'index': index, 'type': 'btn', 'filename': filename})
    layout = html.Li(html.Div(children=[button, download_area]))
    return layout


home_layout = html.Div([
    dcc.Store(id='root-url', storage_type = 'memory', clear_data=True),
    dcc.Store(id='loaded', storage_type = 'memory', clear_data=True, data=False),
    dcc.Location(id='url', refresh=False),
    nav_layout,
    html.H1(
        children="Wholesale & PyMES - Preproccesing",
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.Div(id='page-content'),
    html.Footer("Copyright 2024, Cognitive Services.")
])

app.layout = home_layout

############################################[ BACKEND ]#######################################

# The following callback is used to dynamically instantiate the root-url
@app.callback([Output('root-url', 'data'), Output('loaded', 'data')], 
              Input('url', 'pathname'), 
              State('loaded', 'data'))
def update_root_url(url, loaded):
    if not loaded:
        return url, True
    else:
        raise PreventUpdate

#  When the URL changes, update the content
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')],
              [State('root-url', 'data'),State('loaded', 'data')])
def display_page(pathname, root_url, is_loaded):
    logger.info(f"Root URL: {pathname}")
    if is_loaded:
        if pathname == root_url + 'page1':
            logger.info("## Page1")
            return page_div("page1")
        
        elif pathname == root_url + 'page2':
            logger.info("## Page 2")
            return page_div("page2")
        
        elif pathname == root_url + 'page3':
            logger.info("## Page 3")
            return page_div("page3")
        
        elif pathname == root_url + 'page4':
            logger.info("## Page 4")
            return page_div("page4")
        
        elif pathname == root_url + 'page5':
            logger.info("## Page 5")
            return page_div("page5")
        
        elif pathname == root_url + 'page6':
            logger.info("## Page 6")
            return page_div("page6")
        
        elif pathname == root_url + 'page7':
            logger.info("## Page 7")
            return page_div("page7")
        
        elif pathname == root_url + 'page8':
            logger.info("## Page 8")
            return page_div("page8")
        
        elif pathname == root_url + 'page9':
            logger.info("## Page 9")
            return page_div("page9")
        
        elif pathname == root_url + 'page10':
            logger.info("## Page 10")
            return page_div("page10")
        
        elif pathname == root_url + 'page11':
            logger.info("## Page 11")
            return page_div("page11")
        
        elif pathname == root_url + 'home':
            logger.info("## home")
            return index_layout
        
        else:
            return index_layout
    else:
        return index_layout

# This part is the upper logic
	
def get_managed_folder_list():
    """
    Get the list of managed folders in the current project

    :return: A list of (id, name)
    """
    project = dataiku.api_client().get_default_project()
    managed_folders = project.list_managed_folders()
    ids_and_names = [(mf.get('id', ''), mf.get('name', ''))
                     for mf in managed_folders]
    return ids_and_names


@app.callback(Output('select_managed', 'options'),
              Input('select_managed', 'id'))
def load_select_folder(_):
    """
    Populate the dropdown with the list of the managed folders

    Returns:
        list of the managed folders with their id
    """
    ids_and_names = get_managed_folder_list()
    print(ids_and_names)
    return [{'value': ian[0], 'label': ian[1]} for ian in ids_and_names]



# List files in selected managed folder
@app.callback([Output('upload_data', 'disabled', allow_duplicate = True),
               Output('sequential_call', 'data', allow_duplicate = True),
               Output('file_list', 'children', allow_duplicate = True)],
              Input('select_managed', 'value'),
              State('sequential_call', 'data'),
              prevent_initial_call = True)
def clear_list(_, data):
    """
    Clear the list of Button and Download components
    Args:
        _: not used (only for calling the callback)
        data: for callback synchronization

    Returns:
        False (to enable the Upload component),
        value (for calling the next callback (update list))
        [] (to remove existing component)
    """
    value = data or {'update_list': 0}
    value['update_list'] = value['update_list'] + 1
    return [False, value, []]

def get_files_in_folder(folder_id):
    """
    Get the list of files in a managed folder

    :param id: Id of the managed folder

    :return: A list of files in the managed folder
    """
    mf = dataiku.Folder(folder_id)
    files = mf.list_paths_in_partition()
    return files

# Update list of file
@app.callback([Output('file_list', 'children', allow_duplicate = True),
               Output('upload_data', 'disabled', allow_duplicate = True)],
              Input('sequential_call', 'data'),
              State('select_managed', 'value'),
              prevent_initial_call = True)
def update_list(_, folder_id):
    """
    Update the file list
    Args:
        _: not use, callback synchronization
        folder_id: the id of the managed folder

    Returns:
        the file list
    """
    if folder_id:
        files = get_files_in_folder(folder_id)
        if len(files) == 0:
            return [[html.Li("No file in the selected folder")], False]
        else:
            return [[make_download_button(filename, x)\
					 for x, filename in enumerate(files)],\
                            False]
    else:
        return dash.no_update, True


# Upload file in managed folder
@app.callback(Output('select_managed', 'value', allow_duplicate = True),
              [Input('upload_data', 'filename'), Input('upload_data', 'contents')],
              State('select_managed', 'value'),
              prevent_initial_call = True)
def update_output(uploaded_filenames, uploaded_file_contents, folder_id):
    """
    Save uploaded files and regenerate the file list.
    Args:
        uploaded_filenames: filenames
        uploaded_file_contents: file contents
        folder_id: where to upload the files.

    Returns:
        folder_id for file list refresh
    """
    if folder_id is not None:
        mf = dataiku.Folder(folder_id)
        if uploaded_filenames is not None and uploaded_file_contents is not None:
            for name, data in zip(uploaded_filenames, uploaded_file_contents):
                content_type, content_string = data.split(',')
                stream_d = base64.b64decode(content_string)
                stream = io.BytesIO(stream_d)
                mf.upload_stream(name, stream)

        return folder_id
    else:
        return dash.no_update

# Download file from Managed Folder
@app.callback(Output({'type': 'dld', 'index': MATCH}, 'data'),
              Input({'type': 'btn', 'index': MATCH, 'filename': ALL}, 'n_clicks'),
              State({'type': 'btn', 'index': MATCH, 'filename': ALL}, 'id'),
              State('select_managed', 'value'),
              prevent_initial_call = True)
def download_file(_, id, managed):
    """
    Callback for downloading a file
    Args:
        _: not used (only for triggering the callback)
        id: id of the associated button
        managed: value of the selected managed folder
    Returns:
        nothing, just the ability of downloading a file.
    """
    if id:
        mf = dataiku.Folder(managed)

        def write_file(bytes_io):
            stream = mf.get_download_stream(id[0].get('filename', ''))
            bytes_io.write(stream.read())

        return dcc.send_bytes(write_file, (id[0].get('filename', '_file'))[1:])
    else:
        return dash.no_update


@app.callback(
    Output("select_dataset", "options"),
    Input('sequential_call', 'data'),
    State('select_managed', 'value'),
    prevent_initial_call = True)
def load_select_dataset(_, folder_id):
	if folder_id:
		files = get_files_in_folder(folder_id)
		if len(files) == 0:
			return [[html.Li("No file in the selected folder")], False]
		else:
			return [{'value': f"{file}", 'label': f"{file}"} for file in files]
	else:
		return dash.no_update, True
	
#@app.callback(
#    dash.dependencies.Output('example-graph','figure'),
#    [dash.dependencies.Input('graph-update', 'n_intervals')]
#)
#def updateTable(n):
#    dataset = dataiku.Dataset("sample_data_prepared")
#    df = dataset.get_dataframe()
#    return df
