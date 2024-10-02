import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

df = pd.read_csv('data.csv')
# print(df.head())

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1(
        "Automobile Sales Statistics Dashboard", 
        style={'textAlign' : 'center', 'color' : '#503D36', 'font-size' : 24}
    ),
    html.Div([
        html.H2("Select Statistics :"),
        dcc.Dropdown(
            id='dropdown-statistics', 
            options=[
                        {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                        {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
                    ],
            placeholder='Select a report type', value='select-statistics',
            style={'width' : '80%', 'padding' : '5px', 'font-size' : '20px'}
        ),
        html.Br(),
        html.H2('Select year :'),
        dcc.Dropdown(
            id='select-year', 
            options=[{'label': i, 'value': i} for i in range(1980, 2014)],
            placeholder='Select-year', value='Select-year',
            style={'width' : '80%', 'padding' : '5px', 'font-size' : '20px'}
        )
    ]),
    html.Div(html.Div(id='output-container', className='chart-grid'))
])

'''
callback 1:
The purpose of this function is to enable or disable the year selection dropdown based on 
the user's choice of report type from another dropdown
The function checks the value of selected statistics. If the selected statistics is Yearly Statistics 
the function returns False. This means the disabled property of the select-year dropdown will be set to 
False, enabling the dropdown so the user can select a year.
If selected statistics is not Yearly Statistics (i.e., it is Recession Period Statistics), the function 
returns True. This means the disabled property of the select-year dropdown will be set to True, disabling 
the dropdown as selecting a year is not relevant in this context.

callback 2:
When Recession Period Statistics is selected, the data is filtered to include only recession periods where 
Recession equals 1. Conversely, when Yearly Statistics is chosen, the data is filtered based on the 
selected year.
'''

@app.callback(  Output(component_id='select-year', component_property='disabled'),
                Input(component_id='dropdown-statistics',component_property='value'))

def update_input_container(stat_type):
    if stat_type == 'Yearly Statistics': 
        return False
    else: 
        return True
    
@app.callback(  Output(component_id='output-container', component_property='children'),
                [Input(component_id='dropdown-statistics', component_property='value'), 
                 Input(component_id='select-year', component_property='value')])

def update_output_container(stat_type, year):
    if stat_type == 'Recession Period Statistics' :
        recession_data = df[df['Recession'] == 1]

        #Plot 1: Automobile sales fluctuate over Recession Period (year wise) using line chart
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, x='Year', y='Automobile_Sales', 
                           title="How Automobile sales fluctuate over Recession Period (year wise)"))
        
        #Plot 2: Calculate the average number of vehicles sold by vehicle type and represent as a Bar chart
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()                 
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales',
                          title="Sales Trend Vehicle-wise during Recession"))
        
        # Plot 3: Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].mean().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type',
                          title="Share of Each Vehicle Type in Total Expenditure during Recessions"))
        
        # Plot 4: Develop a Bar chart for the effect of unemployment rate on vehicle type and sales
        unemp_data= recession_data.groupby(['Vehicle_Type', 'unemployment_rate'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type',
            labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
            title='Effect of Unemployment Rate on Vehicle Type and Sales'))
        
        return [
            html.Div(className='chart-item', children=[html.Div(R_chart1), html.Div(R_chart2)], style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(R_chart3), html.Div(R_chart4)], style={'display': 'flex'})
        ]
    
    elif stat_type == 'Yearly Statistics' :
        year_data = df[df['Year'] == year]
        
        # Plot 1: Yearly Automobile sales using line chart for the whole period.
        yas = df.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas, x='Year', y='Automobile_Sales', 
                           title="How Automobile sales fluctuate over 1980 - 2013"))

        # Plot 2: Total Monthly Automobile sales using line chart.
        mas = df.groupby('Month')['Automobile_Sales'].mean().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(mas, x='Month', y='Automobile_Sales',
                           title='Total Monthly Automobile Sales'))
        
        # Plot 3: bar chart for average number of vehicles sold during the given year
        avr_vdata = year_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph( 
            figure=px.bar(avr_vdata, x='Vehicle_Type',y='Automobile_Sales', title='Average Vehicles Sold by Vehicle Type in the year {}'.format(year)))

        # Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
        exp_data = year_data.groupby('Vehicle_Type')['Advertising_Expenditure'].mean().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data, values='Advertising_Expenditure', names='Vehicle_Type',
                          title="Total Advertisment Expenditure for Each Vehicle"))
        
        return [
                html.Div(className='chart-item', children=[html.Div(Y_chart1), html.Div(Y_chart2)], style={'display':'flex'}),
                html.Div(className='chart-item', children=[html.Div(Y_chart3), html.Div(Y_chart4)], style={'display': 'flex'})
        ]
    
    else :
        return None

if __name__ == "__main__" :
    app.run()