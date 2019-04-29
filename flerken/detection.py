#!/usr/bin/python
# -*-coding:utf-8-*-

""" 
Flerken detection page control center
"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

from flask import render_template, request, redirect, url_for
from flerken import app
import html
import json
from .control.smart_detect import smart_detect
from .lib.mysql_conn import *
from datetime import datetime

@app.route('/detection', methods = ['GET'])
def detection_index():
    return render_template("detection.html")

@app.route('/v1/detect/result.json', methods = ['POST'])
def detect_api():
    cmd = request.form['cmd'] if ('cmd' in request.form.keys()) else ''
    platform = request.form['platform'] if ('platform' in request.form.keys()) else 'not_sure'
    
    #delete spaces and fix unicode
    cmd = html.unescape(cmd).lstrip().rstrip()
    cmd = cmd.replace(u'\xa0', u' ')
    
    #print(cmd)
    #cmd is null or space
    if len(cmd) == 0:
        result = {'res': -1, 'message': 'Length of your input command is zero, please check it and try again!'}
        return json.dumps(result)
    else:
        if platform == 'linux':
            res = smart_detect(cmd).linux_identify()
            db_info = {}
            db_info['rid'] = 0
            db_info['cmd'] = res['cmd']
            db_info['hash'] = res['hash']
            db_info['obfuscated'] = str(res['obfuscated'])
            db_info['likely_platform'] = res['platform']
            db_info['selected_platform'] = 'linux'
            db_info['reason'] = res['reason']
            db_info['measure_time'] = res['measure_time']
            try:
                db_info['submit_ip'] = request.headers['X-Real-IP']
            except Exception:
                db_info['submit_ip'] = request.remote_addr
            db_info['submit_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Results = M('results')
            Results.add(db_info)
            return json.dumps(res)
        elif platform == 'windows':
            res = smart_detect(cmd).win_identify()
            db_info = {}
            db_info['rid'] = 0
            db_info['cmd'] = res['cmd']
            db_info['hash'] = res['hash']
            db_info['obfuscated'] = str(res['obfuscated'])
            db_info['likely_platform'] = res['platform']
            db_info['selected_platform'] = 'windows'
            db_info['reason'] = res['reason']
            db_info['measure_time'] = res['measure_time']
            try:
                db_info['submit_ip'] = request.headers['X-Real-IP']
            except Exception:
                db_info['submit_ip'] = request.remote_addr
            db_info['submit_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Results = M('results')
            Results.add(db_info)
            return json.dumps(res)
        elif platform == 'not_sure':
            res = smart_detect(cmd).not_sure_identify()
            db_info = {}
            db_info['rid'] = 0
            db_info['cmd'] = res['cmd']
            db_info['hash'] = res['hash']
            db_info['obfuscated'] = str(res['obfuscated'])
            db_info['likely_platform'] = res['likely_platform']
            db_info['selected_platform'] = 'not_sure'
            db_info['reason'] = res['reason']
            db_info['measure_time'] = res['measure_time']
            try:
                db_info['submit_ip'] = request.headers['X-Real-IP']
            except Exception:
                db_info['submit_ip'] = request.remote_addr
            db_info['submit_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            Results = M('results')
            Results.add(db_info)
            return json.dumps(res)
        else:
            result = {'res': -1, 'message': 'PLatform should be choosed in following list ["linux", "windowd", "not_sure"]'}
            return json.dumps(result)
