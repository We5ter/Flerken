#!/usr/bin/python
# -*-coding:utf-8-*-
# Path:plugins/win_special_filter_plugin.py

""" 
This module filters windows special obfuscation commands
"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

import re
import json
import os

class win_special_filter_plugin(object):

    def __init__(self,cmd):
        self.cmd = cmd
        self.result = self._check()

    def _load_special_whitelists(self, type):
        try:
            with open(os.path.join(os.getcwd(),'flerken/config/whitelists/win_whitelist.json')) as f:
                whitelists = json.loads(f.read())['special'][type]
                return whitelists
        except Exception:
            with open(os.path.join(os.getcwd(),'../flerken/config/whitelists/win_whitelist.json')) as f:
                rules = json.loads(f.read())['special'][type]
                return rules

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
    
    def _unit_check(self,type):
        self.whitelists = self._load_special_whitelists(type)
        for wl in range(0,len(self.whitelists)):
            regex_compiled = self._prepare_pattern(self.whitelists[str(wl)]['regex'])
            if 'length' in self.whitelists[str(wl)].keys():
                if self.whitelists[str(wl)]['condition'] == '<':
                    if regex_compiled.search(self.cmd) != None and len(self.cmd) < self.whitelists[str(wl)]['length']:
                        return True
                        break
                    else:
                        continue
                if self.whitelists[str(wl)]['condition'] == '>':
                    if regex_compiled.search(self.cmd) != None and len(self.cmd) > self.whitelists[str(wl)]['length']:
                        return True
                        break
                    else:
                        continue
                if self.whitelists[str(wl)]['condition'] == '<=':
                    if regex_compiled.search(self.cmd) != None and len(self.cmd) <= self.whitelists[str(wl)]['length']:
                        return True
                        break
                    else:
                        continue    
                if self.whitelists[str(wl)]['condition'] == '>=':
                    if regex_compiled.search(self.cmd) != None and len(self.cmd) >= self.whitelists[str(wl)]['length']:
                        return True
                        break
                    else:
                        continue  
                if self.whitelists[str(wl)]['condition'] == '=':
                    if regex_compiled.search(self.cmd) != None and len(self.cmd) == self.whitelists[str(wl)]['length']:
                        return True
                        break
                    else:
                        continue          
            else:
                if regex_compiled.search(self.cmd) != None:
                    return True
                    break
                else:
                    continue      
        return False  

    def _comm_cmd_check(self):
        regex_dict = self._load_special_whitelists('comm_cmd')
        regex_compile = dict()

        for key in regex_dict:
            regex_compile[int(key)] = self._prepare_pattern(regex_dict[key]['regex'])

        #filter logic start
        if regex_compile[0].search(self.cmd) != None and regex_compile[-1].search(self.cmd) == None:
            return True
        elif regex_compile[1].search(self.cmd) != None and regex_compile[-1].search(self.cmd) == None:
            return True
        elif regex_compile[2].search(self.cmd) != None and regex_compile[-1].search(self.cmd) == None:
            return True

        return False

    def _check(self):
        flag = 0
        type_list=['normal_win_process', 'popular_software']
        for type in type_list:
            check = self._unit_check(type)    
            if check == True:
                flag = -1
                break
            else:
                continue  
        if flag == -1:
            return False
        else:
            comm_cmd_res = self._comm_cmd_check()
            if comm_cmd_res == False:
                return False
            else:
                return True



if __name__ == '__main__':

    #test
    sample = 'winAgentSC.exe >'
    print('input cmd: '+sample)
    a = win_special_filter_plugin(sample)
    out = a._check()
    print('out: '+str(out))