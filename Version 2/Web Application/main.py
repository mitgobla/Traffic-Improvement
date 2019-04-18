import os
from flask import Flask, request, render_template, redirect, Response
from flask_classful import FlaskView, route

CWD = os.path.dirname(os.path.realpath(__file__))

debug = True
app = Flask(__name__)
app.config.from_object(__name__)

class HomeView(FlaskView):
    route_base='/home'

    def index(self):
        return render_template('home.html')

