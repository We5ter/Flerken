#!/usr/bin/python
# -*-coding:utf-8-*-

""" 
config
"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

APP_CONFIG = {
    "HOST": "127.0.0.1",
    "PORT": 8080,
    "DEBUG": True, #debug mode
    "SECRET_KEY": "awesomeflerken*",
    "QPS_LIMIT": True,
    "LIMIT_SETTING": ["200 per minute", "5 per second"]，
    "LOG_FILE": "flerken.log"
}

DB_CONFIG = {
     0: {
        "host": "127.0.0.1",
        "port": "3306",
        "user": "root",
        "password": "root",
        "database": "flerken",
        'charset': 'utf8',  
        'DB_DEBUG': True,  # Please set this field to 'False' when your website going online
        'autocommit': True  
     }
}
