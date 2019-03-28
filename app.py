from flask import Flask, render_template, request, redirect, flash, url_for
from ticker_request import TickerInputs
import os
import sys
import requests
import json

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter
from bokeh.palettes import Spectral11

import pandas
import zipfile
import io

app = Flask(__name__, template_folder='templates')

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
quandl_api_key = "yKysFzygF2ZwjthmiHe7"

def requestGetData(responseFormat, ticker):
  baseurl = "https://www.quandl.com/api/v3/datatables/WIKI/PRICES."
  requestURL = baseurl + responseFormat + "?" + \
      "ticker=" + ticker + "&api_key=" + quandl_api_key
  return requests.get(requestURL)

def requestGetMetadata(responseFormat):
  baseurl = "https://www.quandl.com/api/v3/datatables/WIKI/PRICES/metadata"
  if responseFormat != "":
    requestURL = baseurl + "." + responseFormat + "?" + "api_key=" + quandl_api_key
  else:
    requestURL = baseurl + responseFormat + "?" + "api_key=" + quandl_api_key
  return requests.get(requestURL)


def getTickers():
  response = requests.get("https://www.quandl.com/api/v3/databases/WIKI/metadata?api_key=yKysFzygF2ZwjthmiHe7")
  root = zipfile.ZipFile(io.BytesIO(response.content))
  for name in root.namelist():
    df = pandas.read_csv(root.open(name))

  return df['code'].values


@app.route('/', methods=['POST','GET'])
def index():
  form = TickerInputs(request.form)

  if request.method == 'POST':
    if form.validate() == False:
      flash('All fields are required.')
      return render_template('index.html', form=form)
    elif form.ticker.data not in getTickers():
      if form.ticker.data.upper() in getTickers():
        flash('Ticker must be all uppercase, i.e. \'GOOG\'')
      else:
        flash('Ticker not in DB')
      return render_template('index.html', form=form)
    else:
      return redirect(url_for('graph', **request.form))

  elif request.method == 'GET':
    return render_template('index.html', form=form)

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/graph')
def graph():

    plot_params = {'opening':'open', 
                   'high':'high',
                   'low': 'low',
                   'closing':'close', 
                   'volume':'volume', 
                   'adj_opening':'adj_open', 
                   'adj_high':'adj_high', 
                   'adj_low':'adj_low', 
                   'adj_closing':'adj_close', 
                   'adj_volume':'adj_volume'}

    ticker = request.args.get('ticker')

    response = requestGetData('json', ticker)
    response2 = requestGetMetadata('json')

    WIKIP = json.loads(response.text)
    metadata = json.loads(response2.text)

    columns = [dct['name'] for dct in metadata['datatable']['columns']]
    wikipdf = pandas.DataFrame(WIKIP['datatable']['data'], columns=columns)

    ### convert generic date objects to datetime objects and set datetime as index
    wikipdf['date'] = pandas.to_datetime(wikipdf['date'])
    wikipdf.set_index('date', inplace=True)

    ### plotting requested parameters
    p = figure()
    numlines = len(request.args)-3
    mypalette = Spectral11[0:numlines]
    linenum = 0
    for key, value in request.args.items():
      if key in plot_params:
        data = wikipdf[plot_params[key]]

        x = data.index
        y = data.values

        legend_str = key.capitalize() + " Price"
        p.line(x, y, legend=legend_str, line_color=mypalette[linenum])
        linenum += 1


    p.xaxis[0].formatter = DatetimeTickFormatter()
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.legend.location = "top_right"
    p.legend.click_policy = "hide"

    script, div = components(p)

    return render_template('graph.html', script=script, div=div)

if __name__ == '__main__':
  app.run(port=33507, debug=True)
