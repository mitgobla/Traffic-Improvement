import os
from flask import Flask, request, render_template, redirect, Response
from flask_classful import FlaskView, route

CWD = os.path.dirname(os.path.realpath(__file__))

debug = True
app = Flask(__name__)
app.config.from_object(__name__)

class HomeView(FlaskView):
    route_base='/'

    def index(self):
        return render_template('home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=debug)