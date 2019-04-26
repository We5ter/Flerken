#!/usr/bin/python
# -*-coding:utf-8-*-
# Path:plugins/win_special_detect_plugin.py

""" 
This module detects windows special obfuscation commands
"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

import sys, os
import json
import socket
import traceback
from math import log
import time
import re
import string
from .win_special_filter_plugin import win_special_filter_plugin

class win_special_detect_plugin():

    def __init__(self, cmd):
        self.cmd = cmd
        self.result = self._detect_obfuscation()

    def _load_special_rules(self):
        try:
            with open(os.path.join(os.getcwd(),'flerken/config/rules/win_rule.json')) as f:
                rules = json.loads(f.read())['special']
                return rules
        except Exception:
            with open(os.path.join(os.getcwd(),'../flerken/config/rules/win_rule.json')) as f:
                rules = json.loads(f.read())['special']
                return rules

    def _check(self):

        # Calculate the long strings with numbers
        pattern_str = re.compile(r'[a-zA-Z0-9]+[a-zA-Z0-9|\+|\/]*[\=]*')
        result_str = pattern_str.findall(self.cmd)
        
        cmd1="This is a good apple"

        for string in result_str:
            if len(string) >= len(cmd1):
                cmd1 = string
        self.cmd = cmd1
        
        # Calculate the number of words that are composed of alphabets
        pattern = re.compile(r'[a-zA-Z]+')
        result = pattern.findall(self.cmd)
        ctr_total = len(result)
        if ctr_total == 0:
            ctr_total = 1 # Avoid ctr divide by 0 in the following code
        
        ctr = 0
        # Define a limited whitelist that are considered as readable words
        whitelist = []
        for word in result:
            if len(word) > 2019: # (1) Long word case
                ctr += 1
            else:
                pattern_vowels = re.compile(r'[a|A|e|E|i|I|o|O|u|U]')
                result_vowels = pattern_vowels.findall(word)
                #print result_vowels
                ratio = len(result_vowels)/float(len(word))
                #print ratio
                if ratio > 0.87 or ratio < 0.42: # (2) Vowel case
                    if word.lower() not in whitelist:
                        ctr += 1
                else:
                    pattern_repeat = re.compile(r'(.)\1{4}')
                    # (3) Repetition case. Find out the repeat of an alphabet for more than n times
                    result_repeat = pattern_repeat.findall(word)
                    if len(result_repeat) >= 1:
                        ctr += 1
                    else:
                        #(4) Uncommon capital case.
                        pattern_case = re.compile(r'[A-Z]')
                        pattern_first = re.compile(r'[a-z]')
                        result_case = pattern_case.findall(word)
                        case_ratio = len(result_case)/float(len(word))
                        if case_ratio >= 0.66 and case_ratio != 1:
                            ctr += 1
                        elif case_ratio > 0 and re.match(pattern_first,word):
                            ctr += 1
        ratio_unread = ctr / float(ctr_total); #Calc the ratio of unreadable words.
        
        special_rules = self._load_special_rules()
        if len(self.cmd) > special_rules['length']: 
            if ratio_unread > special_rules['condition']["0"]["ratio_unread"]:
                return True
            else:
                return False
        else:
            return  False

    def _detect_obfuscation(self):
        if win_special_filter_plugin(self.cmd).result == False:
            check = self._check()
            if check == True:
                return {"obfuscated": True, "reason": "windows.obfus.special"}
            else:
                return {"obfuscated": False, "reason": ""}
        else:
            return {"obfuscated": False, "reason": ""}

if __name__ == '__main__':
    
    #test
    sample = 'CMD.exe HU5IGBNJM4GUGSHLHSDDS6DESQ87WE4QKLJSQIUHKNJ98HKLHJKS=='
    print('sample command:\n'+sample+'\n')
    a = win_special_detect_plugin(sample)._detect_obfuscation()
    print(a)
      

