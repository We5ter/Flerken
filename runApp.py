#!/usr/bin/python
# -*-coding:utf-8-*-

""" 
The Entry of Flerken App
"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

from flerken import app
from flerken.config.global_config import APP_CONFIG

app.run(host=APP_CONFIG['HOST'],port=APP_CONFIG['PORT'])
