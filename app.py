import pandas as pd
import datetime
from datetime import datetime, timedelta

# Reading Dataframes of interest:
## Earnings DataFrame
url_earningdf = "http://stockdatadash.s3-website.eu-central-1.amazonaws.com/_displayearnings_cleanset.csv"
url_pri = "http://stockdatadash.s3-website.eu-central-1.amazonaws.com/pri.csv"

earningsdf = pd.read_csv(url_earningdf)
earningsdf = earningsdf.drop(columns="Unnamed: 0")



# FORMATTING "EPS"
def format_eps(x):
    return f"{x:.2f} $"

earningsdf['epsActual'] = earningsdf['epsActual'].apply(format_eps)
earningsdf['epsEstimate'] = earningsdf['epsEstimate'].apply(format_eps)

# FORMATTING:
def format_as_billion(x):
    return f"{x / 1e9:.4f} Mrd"

earningsdf['revenueActual'] = earningsdf['revenueActual'].apply(format_as_billion)
earningsdf['revenueEstimate'] = earningsdf['revenueEstimate'].apply(format_as_billion)



#earningsdf = pd.read_csv("./data/earnings/_displayearnings_cleanset.csv")






#earningsdf["date"] = pd.to_datetime(earningsdf["date"])
## Program Run Info 

pridf = pd.read_csv(url_pri)

#pridf = pd.read_csv("./data/pri.csv")
pridf = pridf.drop(columns="Unnamed: 0")

# Imports for the Dashboard

import dash
from dash import dcc, html, dash_table, Input, Output, callback
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

import pandas as pd

# -------------------------------
# Variables to display at the Page:
# -------------------------------

version_str = "1.1x_WIP"

# stockrun_date = When was the last time, the stock update app was run
stockrun_date = pridf["stockrun_date"].values[0]

# earningsrun_date = When was the last time, the earnings update app was run

earningsrun_date = datetime.strptime(pridf["earningsrun_date"].values[0], "%Y-%m-%d")
earningsrun_date = datetime.date(earningsrun_date)

# Todays Date
tmstp = datetime.now()
dtd = datetime.date(tmstp)
dtd_str = str(tmstp)[:10]
# Yesterdays Date
pastdate = datetime.date(tmstp - timedelta(2))
filterpastdate = tmstp - timedelta(1)
pstd_str = str(pastdate)[:10]


# -------------------------------
# Bedienfilter:
# -------------------------------
## Sortiert nach:

## Gefiltert nach:

df_t = pd.DataFrame()


# Mit "eventID":
#earningsdf["eventID"] = earningsdf["symbol"] +"-"+ earningsdf["date"]
#ioi = ["date", "name", "hour", "marketCapitalization", "revenueEstimate", "revenueActual", "epsEstimate", "epsActual", "symbol", "eventID"]


# Ohne "eventID":
ioi = ["date", "name", "hour", "marketCapitalization", "revenueEstimate", "revenueActual", "epsEstimate", "epsActual", "symbol"]

for i in ioi:
    df_t[i] = earningsdf[i] 

# earningsdf = df_t

# -------------------------------
# app 
# -------------------------------

## Definition

app = dash.Dash(external_stylesheets=[dbc.themes.LUX],
                meta_tags = [{"name" : "viewport",
                             "content" : "width=device=width, initial-scale=1.0"}])
server = app.server

## Elements


#datetime.strptime(date_string, "%d %B, %Y")

anzeigedf = df_t
anzeigedf = anzeigedf.sort_values(by=["date", "epsEstimate"], ascending=[True, False])
#anzeigedf = anzeigedf.sort_values(by=["epsEstimate"], ascending=False)
#anzeigedf = anzeigedf.sort_values(by=["date"], ascending=True)

anzeigedf["marketCapitalization"] = anzeigedf["marketCapitalization"].round(4)
anzeigedf["epsEstimate"] = anzeigedf["epsEstimate"].round(4)


f_date = anzeigedf["date"] > pstd_str
anzeigedf = anzeigedf.loc[f_date]

cfilterlist = []
for i in anzeigedf["name"].unique():
    cfilterlist.append(i)


earningstable = dash_table.DataTable(anzeigedf.to_dict('records'), id="earningstable",
                                    page_size=23,
                                    style_data={'color': 'white','backgroundColor': 'black'},
                                    style_header={
                                    'backgroundColor': 'rgb(110, 110, 110)',
                                    'color': 'white','fontWeight': 'bold'})

earnings_fdpdn = dcc.Dropdown(cfilterlist, value=cfilterlist, multi=True, id='earnings_fdpdn')#, id='earnings_fdpdn', multi=True),






## Layout section: Bootstrap:

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H3(f"Today: {dtd_str}", className="text-end"))
            ]),
    dbc.Row([
        dbc.Col(html.H1("📈 Stock Earnings Data", className="text-start")),
        dbc.Col(html.H1(f"Data last refreshed: {earningsrun_date}", className="text-end"))
            ], justify="around"),
    dbc.Row([
        dbc.Col(html.Div(earningstable)),
                html.Div(earnings_fdpdn)
            ]), 
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="my-dpdnx", multi=False, value="AMZN", options=[{"label" : x, "value" : x} for x in sorted(earningsdf["date"].unique())]
                        ),
                ]),
        dbc.Col([
            dcc.Dropdown(
                id="my-dpdn2", multi=False, value="AMZN", options=[{"label" : x, "value" : x} for x in sorted(earningsdf["date"].unique())]
                        )
                ])
            ]),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="my-dpdn11", multi=False, value="AMZN", options=[{"label" : x, "value" : x} for x in sorted(earningsdf["date"].unique())]
                        ),
            dcc.Graph(id="line-fig", figure={})
                ], width={"size":6, "offset":0}),
        dbc.Col([
            dcc.Dropdown(
                id="my-dpdn221", multi=True, value=["AMZN", "TSLA"], options=[{"label" : x, "value" : x} for x in sorted(earningsdf["date"].unique())]
                        ),
            dcc.Graph(id="line-fig2", figure={})
                ], width={"size":6, "offset":0})
            ], justify="around"),
    dbc.Row([]),

    dbc.Row([
        dbc.Col(html.H3(f"©JLX JLX SFTWR 2024, StockDataDash {version_str}", className="text-start"))
                ]),
    
                            ], fluid=True)

@callback(
    Output(earningstable, component_property="data"),
    Input(earnings_fdpdn, component_property="value")
        )


def update_output(nameofstock):
    mask = anzeigedf["name"].isin(nameofstock)
    filtered_table = anzeigedf[mask].to_dict('records')
    return filtered_table

# -------------------------------
# Run the App
# -------------------------------

if __name__ == "__main__":
    app.run_server(mode="inline", host="localhost")