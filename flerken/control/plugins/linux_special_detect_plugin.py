#!/usr/bin/python
# -*-coding:utf-8-*-
# Path:plugins/linux_special_detect_plugin.py

""" 
This module detects linux special obfuscation commands

"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

import re
import json
import os
import warnings

class linux_special_detect_plugin(object):

    def __init__(self, cmd):
        self.cmd = cmd
        self.result = self._detect_obfuscation()
    
    def _load_special_rules(self):
        try:
            with open(os.path.join(os.getcwd(),'flerken/config/rules/linux_rule.json')) as f:
                self.rules = json.loads(f.read())['special']
                return self.rules
        except Exception:
            with open(os.path.join(os.getcwd(),'../flerken/config/rules/linux_rule.json')) as f:
                self.rules = json.loads(f.read())['special']
                return self.rules

    def _prepare_pattern(self, regex):
        """
        Strip out key:value pairs from the pattern and compile the regular
        expression.
        """
        try:
            return re.compile(regex, re.I)
        except re.error as e:
            warnings.warn(
                "Caught '{error}' compiling regex: {regex}"
                .format(error=e, regex=regex)
            )
            return re.compile(r'(?!x)x')

    def _check(self):
        self._load_special_rules()
        rules_compiled = self._prepare_pattern(self.rules['regex'])
        list = rules_compiled.findall(self.cmd)
        if len(list) > 2:
            return True
        else:
            return False

    def _detect_obfuscation(self):
        check = self._check()
        if check == True:
            return {"obfuscated": True, "reason": "linux.obfus.special"}
        else:
            return {"obfuscated": False, "reason": ""}