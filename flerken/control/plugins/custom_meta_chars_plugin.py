#!/usr/bin/python
# -*-coding:utf-8-*-
# Path:plugins/custom_meta_chars_plugin.py

""" 
This module filters unexpected chars in command
"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

import re
import json
import os

class custom_meta_chars_plugin(object):

  def __init__(self, cmd):
    self.cmd = cmd
    self.rules = self._load_rules()
    self.result = self._check()

  def _load_rules(self):
    try:
      with open(os.path.join(os.getcwd(),'flerken/config/rules/meta_chars.json')) as f:
        rules = json.loads(f.read())
        return rules
    except Exception:
      with open(os.path.join(os.getcwd(),'../flerken/config/rules/meta_chars.json')) as f:
        rules = json.loads(f.read())
        return rules

  def _check(self):
    pattern_valid = re.compile(self.rules['meta_chars'])
    cmd = pattern_valid.sub("",self.cmd)
    return cmd

if __name__ == '__main__':

    #test
    sample1 = 'ddd121323213*&^&%$$")({}[]'
    print('input cmd: '+sample1)
    a = custom_meta_chars_plugin(sample1).result
    print('out: '+str(a))
    sample2 = 'vcvddd12132fgfdgfdgfd3213*&^&%$$")3(e3wqre{rrewr}[]'
    print('input cmd: '+sample2)
    b = custom_meta_chars_plugin(sample2).result
    print('out: '+str(b))