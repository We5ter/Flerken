#!/usr/bin/python
# -*-coding:utf-8-*-
# Path:plugins/linux_graphic_detect_plugin.py

""" 
This module detects linux graphic obfuscation commands

"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

import re
import json
import os

class linux_graphic_detect_plugin(object):

    def __init__(self, cmd):
        self.cmd = cmd
        self.result = self._detect_obfuscation()
    
    def _load_graphic_rules(self):
        try:
            with open(os.path.join(os.getcwd(),'flerken/config/rules/linux_rule.json')) as f:
                self.rules = json.loads(f.read())['graphic']
                return self.rules
        except Exception:
            with open(os.path.join(os.getcwd(),'../flerken/config/rules/linux_rule.json')) as f:
                self.rules = json.loads(f.read())['graphic']
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
        self._load_graphic_rules()
        rules_compiled = self._prepare_pattern(self.rules['regex'])
        if rules_compiled.search(self.cmd) == False:
            return False
        else:
            return True

    def _underline_rate(self):
        underline_cnt = (self.cmd).count("_")
        total_cnt = len(self.cmd)
        if total_cnt == 0:
            total_cnt = 1
        rate = underline_cnt/total_cnt
        if rate > 0.6:
            return True
        else:
            return False

    def _detect_obfuscation(self):
        check = self._check()
        rate = self._underline_rate()
        if check == True and rate == True:
            return {"obfuscated": True, "reason": "linux.obfus.graphic"}
        else:
            return {"obfuscated": False, "reason": ""}