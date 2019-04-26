#!/usr/bin/python
# -*-coding:utf-8-*-
# Path:plugins/linux_generic_detect_plugin.py

""" 
This module detects linux generic obfuscation commands

"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

import warnings
import re
import os,sys
import json
from .linux_generic_filter_plugin import linux_generic_filter_plugin

class linux_generic_detect_plugin(object):

    def __init__(self, cmd):
        self.cmd = cmd
         #OBFUSCATED TYPE STORAGE
        self.__TYPE_LIST = []
        self.result = self._detect_obfuscation()

    def _load_generic_rules(self, type):
        try:
            with open(os.path.join(os.getcwd(),'flerken/config/rules/linux_rule.json')) as f:
                self.rules = json.loads(f.read())['generic'][type]
                return self.rules
        except Exception:
            with open(os.path.join(os.getcwd(),'../flerken/config/rules/linux_rule.json')) as f:
                self.rules = json.loads(f.read())['generic'][type]
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

    def _check(self, type):
        flag = -1
        for r in range(0,len(self.rules)):
            regex_compiled = self._prepare_pattern(self.rules[str(r)]['regex'])
            if 'length' in self.rules[str(r)].keys():
                if self.rules[str(r)]['condition'] == '<':
                    if regex_compiled.search(self.cmd) != None and len(self.cmd) < self.rules[str(r)]['length']:
                        flag = r
                        continue
                    else:
                        break
                if self.rules[str(r)]['condition'] == '>':
                    if regex_compiled.search(self.cmd) != None and len(self.cmd) > self.rules[str(r)]['length']:
                        flag = r
                        continue
                    else:
                        break
                if self.rules[str(r)]['condition'] == '<=':
                    if regex_compiled.search(self.cmd) != None and len(self.cmd) <= self.rules[str(r)]['length']:
                        flag = r
                        continue
                    else:
                        break    
                if self.rules[str(r)]['condition'] == '>=':
                    if regex_compiled.search(self.cmd) != None and len(self.cmd) >= self.rules[str(r)]['length']:
                        flag = r
                        continue
                    else:
                        break  
                if self.rules[str(r)]['condition'] == '=':
                    if regex_compiled.search(self.cmd) != None and len(self.cmd) == self.rules[str(r)]['length']:
                        flag = r
                        continue
                    else:
                        break          
            else:
                if regex_compiled.search(self.cmd) != None:
                    flag = r
                    continue
                else:
                    break
        if flag == len(self.rules) -1:
            self.__TYPE_LIST.append(type)

    def _varible_name_score(self):       
        score=0
        pattern = self._load_generic_rules('varible_name_score')["0"]['regex']
        try:
            pattern_str = re.compile(pattern)
            result_str = pattern_str.findall(self.cmd)
            result_str = list(set(result_str))
            
            for string_ele in result_str:
                if len(string_ele)>0:
                    pattern_repeat = re.compile(r'%s' %string_ele)
                    target_str = pattern_repeat.findall(self.cmd)
                    if len(target_str)>1:
                        score += 1
            if score > 1:
                score = 1
            else:
                score = 0
            return score
        except Exception as e:
            print(e)

    def _varible_name_check(self):
        vn_rules = self._load_generic_rules('varible_name')
        vn_rules_compiled = dict()

        for rule in vn_rules:
            vn_rules_compiled[int(rule)] = self._prepare_pattern(vn_rules[rule]['regex'])
    
        if vn_rules_compiled[0].search(self.cmd) != None:
            if self._varible_name_score() == 1:
                if vn_rules_compiled[1].search(self.cmd) != None:
                    if linux_generic_filter_plugin(self.cmd,'varible_name').result == False:
                        if len(self.cmd) < 300:
                            self.__TYPE_LIST.append('varible_name')

    def _detect_obfuscation(self):
        type_list = ["echo_type", "sub_syntax", "special_calc", "ifs", "offset_ctl", "escape_char", "reverse_char", "base64", "rot13_char", "octal_code", "hex_or_unicode", "wildcard"]
        for type in type_list:
            if linux_generic_filter_plugin(self.cmd,type).result == False:
                self._load_generic_rules(type)
                self._check(type)
        self._varible_name_check()
        if len(self.__TYPE_LIST) > 0:
            return {"obfuscated": True, "reason": "linux.obfus.generic"}
        else:
            return {"obfuscated": False, "reason": ""}

if __name__ == '__main__':

    #test
    sample = "echo $'\\143\\141\\164\\040\\057\\145\\164\\143\\057\\160\\141\\163\\163\\167\\144' | bash"
    print('input cmd: '+sample)
    linux_generic_detect_plugin(sample)._detect_obfuscation()
    
