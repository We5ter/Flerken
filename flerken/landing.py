#!/usr/bin/python
# -*-coding:utf-8-*-

""" 
Flerken landing page control center
"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

from flask import render_template, request, redirect, url_for, make_response, send_from_directory
from flerken import app
import os

@app.route('/', methods = ['GET'])
@app.route('/landing', methods = ['GET'])
def landing():
    return render_template("landing.html")

@app.route('/doc/<filename>', methods = ['GET'])
def doc(filename):
    file_path = os.getcwd()+'/doc'
    response = make_response(send_from_directory(file_path,filename.encode('utf-8').decode('utf-8')))
    response.headers["Content-Type"] = "application/pdf"
    return response