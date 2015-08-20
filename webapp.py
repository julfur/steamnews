#!/usr/bin/python
from flask import Flask, render_template
import json
import os
app = Flask(__name__)

@app.route('/')
def main():
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    with open(CURRENT_DIR + '/data.json') as data_file:
        data = json.load(data_file)
    return render_template('display.html', data=data)

if __name__ == '__main__':
    app.run()
