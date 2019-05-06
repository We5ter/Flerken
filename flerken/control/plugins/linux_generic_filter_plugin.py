#!/usr/bin/python
# -*-coding:utf-8-*-
# Path:plugins/linux_generic_filter_plugin.py

""" 
This module filters linux generic obfuscation commands

"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

import re
import json
import os

class linux_generic_filter_plugin(object):
        
    def __init__(self,cmd, type):
        self.cmd = cmd
        self.type = type
        self.whitelists = self._load_generic_whitelists()
        self.result = self._check()

    def _load_generic_whitelists(self):
        try:
            with open(os.path.join(os.getcwd(),'flerken/config/whitelists/linux_whitelist.json')) as f:
                whitelists = json.loads(f.read())['generic'][self.type]
                return whitelists
        except Exception:
            with open(os.path.join(os.getcwd(),'../flerken/config/whitelists/linux_whitelist.json')) as f:
                whitelists = json.loads(f.read())['generic'][self.type]
                return whitelists

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

    def _check(self):
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
    
if __name__ == '__main__':

    #test
    sample = '$(echo 3)'
    print('input cmd: '+sample)
    print(linux_generic_filter_plugin(sample,"echo_type").result)