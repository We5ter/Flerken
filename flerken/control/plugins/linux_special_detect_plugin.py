#!/usr/bin/python
# -*-coding:utf-8-*-
# Path:plugins/linux_special_detect_plugin.py

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
    
    def _load_special_rules(self, type):
        try:
            with open(os.path.join(os.getcwd(),'flerken/config/rules/linux_rule.json')) as f:
                rule = json.loads(f.read())['special'][type]
                return rule
        except Exception:
            with open(os.path.join(os.getcwd(),'../flerken/config/rules/linux_rule.json')) as f:
                rule = json.loads(f.read())['special'][type]
                return rule

    def _prepare_pattern(self, regex):
        """
        Strip out key:value pairs from the pattern and compile the regular
        expression.
        """
        try:
            return re.compile(regex)
        except re.error as e:
            warnings.warn(
                "Caught '{error}' compiling regex: {regex}"
                .format(error=e, regex=regex)
            )
            return re.compile(r'(?!x)x')

    def _check_symbol_varible_name(self):
        svn_rule = self._load_special_rules('symbol_varible_name')
        svn_rule_compiled = self._prepare_pattern(svn_rule['regex'])
        list = svn_rule_compiled.findall(self.cmd)
        if len(list) >= 2:
            return True
        else:
            return False

    def _check_string_manipulation(self):
        sm_rule = self._load_special_rules('string_manipulation')
        sm_rule_compiled = self._prepare_pattern(sm_rule['regex'])
        res = sm_rule_compiled.search(self.cmd)
        if res != None:
            return True
        else:
            return False

    def _check_file_io(self):
        fi_rules = self._load_special_rules('file_io')
        fi_rules_compiled = dict()
        for rule in fi_rules:
            fi_rules_compiled[int(rule)] = self._prepare_pattern(fi_rules[rule]['regex'])
        #print(fi_rules_compiled[0])
        if fi_rules_compiled[0].search(self.cmd) == None:
            return False
        else:
            variable_name = fi_rules_compiled[0].search(self.cmd).group(5)
            if fi_rules_compiled[1].search(self.cmd) != None and fi_rules_compiled[2].search(self.cmd) != None:
                return True
            elif fi_rules_compiled[3].search(self.cmd) != None:
                return True
            else:
                return False

    def _detect_obfuscation(self):
        symbol_varible_name_check = self._check_symbol_varible_name()
        string_manipulation_check = self._check_string_manipulation()
        file_io_check = self._check_file_io()
        if symbol_varible_name_check == True or string_manipulation_check == True or file_io_check == True:
            return {"obfuscated": True, "reason": "linux.obfus.special"}
        else:
            return {"obfuscated": False, "reason": ""}