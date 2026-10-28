import base64
from io import BytesIO
from flask import Flask, render_template, request, session, jsonify

# CRITICAL FOR PYTHONANYWHERE: Use the non-interactive Agg backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import pandas as pd

import wordle_counts as wc
#--------------------------------------------------------------------
# Initial set up
#--------------------------------------------------------------------

answers = wc.get_all_answers()
letter_counts = wc.get_letter_counts(answers)
years = wc.get_years()

position_name = None
letter_name = None

index_names = [f"<button type='button' onclick=\"show_letter_graph('{letter_name}')\">{letter_name}</button>" for letter_name in wc.letters]
column_names = [f"<button type='button' onclick=\"show_position_graph('{position_name}')\">{position_name}</button>" for position_name in wc.positions]


app = Flask(__name__)
app.secret_key = 'LG-Wordle-Counts-101'

#--------------------------------------------------------------------
# Functions
#--------------------------------------------------------------------

def plot_graph(x_values, y_values, plot_title):
    plt.plot(x_values,y_values)

    #Use plt.gca() to target the y-axis and set the major locator
    multiplicator_val = (max(y_values) - min(y_values)) // 10
    if multiplicator_val < 1:
        multiplicator_val = 1
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(multiplicator_val))

    #annotate
    for x, y in zip(x_values, y_values):
        plt.annotate(f'({x},{y})', xy=(x,y), xytext=(x,y))
    plt.title(plot_title, color="darkblue")

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close() # Clear the current figure memory
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return plot_base64

def show_all_counts():

    df = pd.DataFrame(letter_counts, index=index_names, columns=column_names)
    table_html = df.to_html(escape=False, classes='data')
    return table_html

#--------------------------------------------------------------------
# Routes
#--------------------------------------------------------------------
@app.route('/')
def index():
    table_html = show_all_counts()
    return render_template('index.html',  years=years, months=wc.month_names, letters=wc.letters, last_date=wc.last_date_str, table_var=table_html)

@app.route('/api/show_selected', methods=['POST'])
def show_selected():
    global position_name
    position_name = None
    global letter_name
    letter_name = None

    global answers
    global letter_counts

    data = request.get_json()
    year = data['year']
    month = data['month']

    if month == "":
        answers = wc.get_answers_for_year(int(year))
        letter_counts = wc.get_letter_counts(answers)
    else:
        letter_counts = wc.get_counts_by_month_for_year(int(year), month)

    df = pd.DataFrame(letter_counts, index=index_names, columns=column_names)
    table_html = df.to_html(escape=False, classes='data')

    return jsonify({'table': table_html})

@app.route('/api/get_position', methods=['POST'])
def get_position():
    data = request.get_json()
    global position_name
    position_name = data['position_name']
    global letter_name
    letter_name = None
    return jsonify({'result':'success', 'position': session['position_name']})

@app.route('/api/get_letter', methods=['POST'])
def get_letter():
    data = request.get_json()
    global letter_name
    letter_name = data['letter_name']
    global position_name
    position_name = None
    return jsonify({'result': 'success', 'letter': session['letter_name']})

@app.route('/graph_counts', methods=['GET'])
def graph_counts():

    if(position_name == "" or position_name == None) and (letter_name == "" or letter_name == None):
        #x_values = letters
        #y_values = sum of counts of all positions for each letter
        x_values = wc.letters
        y_values = [sum(item) for item in letter_counts]
        plot_title = f"Total Number of times a letter appeared in answers since June 2019"
    elif(position_name != "" and position_name!= None):
        #x_values = letters
        #y_values = letter counts for [position_name index] for each letter
        position = wc.positions.index(position_name)
        x_values = wc.letters
        y_values = [item[position] for item in letter_counts]
        plot_title = f"Number of times a letter appeared in the {position_name} place"
    elif(letter_name != None):
        #x_values = position names
        #y_values = letter counts for the letter for each position
        letter_index = wc.letters.index(letter_name)
        x_values = wc.positions
        y_values = letter_counts[letter_index]
        plot_title = f"Number of times letter {letter_name} appeared in each of the 5 places"
    else:
        #error
        pass
    plot_base64 = plot_graph(x_values, y_values, plot_title)
    #return plot_base64

    return render_template('graph_display.html', plot_var=plot_base64)

if __name__ == '__main__':
    app.run(debug=True)
