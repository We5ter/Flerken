#!/usr/bin/python
# -*-coding:utf-8-*-
# Path:plugins/win_generic_detect_plugin.py

""" 
This module detects obfuscation commands with the following four features: 
- Readability
- Ratio of special chars
- Long strings with numbers
- Ratio of Spaces
"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"


import os
import re
import json
import warnings
from .win_generic_filter_plugin import win_generic_filter_plugin

class win_generic_detect_plugin(object):

    def __init__(self, cmd):
        self.cmd = cmd
        self.result = self._detect_obfuscation()

    def _load_generic_rules(self, type):
        try:
            with open(os.path.join(os.getcwd(),'flerken/config/rules/win_rule.json')) as f:
                rules = json.loads(f.read())['generic'][type]
                return rules
        except Exception:
            with open(os.path.join(os.getcwd(),'../flerken/config/rules/win_rule.json')) as f:
                rules = json.loads(f.read())['generic'][type]
                return rules

    def _check(self):

        # Calculate the ratio of special chars and spaces
        ratio_special = 0
        ratio_space = 0
        
        cmd_list = list(filter(lambda x: x.isalnum(),str(self.cmd)))
        cmd_new = "".join(cmd_list)
        cmd_nospace = str(self.cmd).replace(" ","") # squeeze out all the spaces
        # We ignore space if there are more than 10 spaces included. Also alert when there are too many spaces.
        if len(self.cmd) - len(cmd_nospace) > 10: # Here consider a compensation of 10 spaces
            cmd_new = cmd_new + "          "
            cmd_nospace = cmd_nospace + "          "
            ratio_space = (len(self.cmd)-len(cmd_nospace)+10)/float(len(self.cmd)) # Calculate the ratio of spaces
            if len(self.cmd) != 0:
                ratio_special = (len(cmd_nospace) - len(cmd_new)) / float(len(cmd_nospace))
        else:     
            # When there are not too many spaces. We do not ignore spaces.
            cmd_list = filter(lambda x: x.isalnum(), str(self.cmd).replace(" ","a"))
            cmd_new = "".join(cmd_list)
            if len(self.cmd) != 0:
                ratio_special = (len(self.cmd) - len(cmd_new)) / float(len(self.cmd))
        
        # Calculate the ratio of unreadable chars
        ratio_unchar = 0
        cmd_list = filter(lambda x: x.isalnum(),str(self.cmd))
        cmd_new = "".join(cmd_list)
        cmd_nospace = str(self.cmd).replace(" ","") # squeeze out all the spaces
        cmd_unchar_list = filter(lambda x: x.isalnum(), str(self.cmd).replace("`","a").replace("~","a").replace("!","a").replace("@","a").replace("#","a").replace("$","a").replace("%","a").replace("^","a").replace("&","a").replace("*","a").replace("+","a").replace(",","a").replace(";","a").replace("\"","a").replace("'","a").replace("{","a").replace("}","a"))
        cmd_unchar = "".join(cmd_unchar_list)
        if len(self.cmd) - len(cmd_nospace) > 10: # Here consider a compensation of 10 spaces
            cmd_nospace = cmd_nospace + "          "
            if (len(cmd_nospace)-len(cmd_new)) != 0:
                ratio_unchar = (len(cmd_unchar) - len(cmd_new)) / float(len(cmd_nospace)-len(cmd_new))
        else:     
            if (len(self.cmd)-len(cmd_new)) != 0:
                ratio_unchar = (len(cmd_unchar)-len(cmd_new)) / float(len(self.cmd)-len(cmd_new))
      
        # Calculate the number of words that are composed of alphabets
        pattern = re.compile(r'[a-zA-Z]+')
        result = pattern.findall(self.cmd)
        ctr_total = len(result)
        if ctr_total == 0:
            ctr_total = 1 # Avoid ctr divide by 0 in the following code
        
        ctr = 0
        # Define a limited whitelist that are considered as readable words
        whitelist = [] # add this list on demand
        for word in result:
            if len(word) > 10: # (1) Long word case
                ctr += 1
            else:
                pattern_vowels = re.compile(r'[a|A|e|E|i|I|o|O|u|U]')
                result_vowels = pattern_vowels.findall(word)
                #print result_vowels
                ratio = len(result_vowels)/float(len(word))
                #print ratio
                if ratio > 0.8 or ratio < 0.4: # (2) Define a suitable vowel letter ratio interval
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
                        if case_ratio >= 0.6 and case_ratio != 1:
                            ctr += 1
                            #print word
                            #print case_ratio
                        elif case_ratio > 0 and re.match(pattern_first,word):
                            ctr += 1
        ratio_unread = ctr / float(ctr_total); #Calc the ratio of unreadable words.

        long_cmd_rules = self._load_generic_rules('long_cmd')
        shorter_cmd_rules = self._load_generic_rules('shorter_cmd')
        shortest_cmd_rules = self._load_generic_rules('shortest_cmd')

        if len(self.cmd) > long_cmd_rules['length']: # long cmd case
            if ratio_space > long_cmd_rules['condition']["0"]["ratio_space"]:
                return True
            elif ratio_special > long_cmd_rules['condition']["1"]["ratio_special"] and ratio_unread > long_cmd_rules['condition']["1"]["ratio_unread"]:
                return True
            elif ratio_unchar > long_cmd_rules['condition']["2"]["ratio_unchar"] and ratio_unread > long_cmd_rules['condition']["2"]["ratio_unread"]:
                return True
            elif ratio_unchar > long_cmd_rules['condition']["3"]["ratio_unchar"] and ratio_unread > long_cmd_rules['condition']["3"]["ratio_unread"]:
                return True
            elif ratio_special > long_cmd_rules['condition']["4"]["ratio_special"] and ratio_unread > long_cmd_rules['condition']["4"]["ratio_unread"]:
                return True
            elif len(self.cmd) > long_cmd_rules['condition']["5"]["length"]:
                return True
            else:
                ws = long_cmd_rules['ws'] # The weight of special chars
                wc = long_cmd_rules['wc'] # The weight of unreadable chars
                wu = long_cmd_rules['wu']  # The weight of unreadable words
                score = ratio_special * ws + ratio_unchar * wc + ratio_unread * wu #+ ratio_str * wl #Calc the final score.
                if score > 0.2:
                    return True   
                else:
                    return False
        elif len(self.cmd) >= shorter_cmd_rules['length']: # shorter cmd case
            if ratio_special > shorter_cmd_rules['condition']["0"]["ratio_special"] and ratio_unread > shorter_cmd_rules['condition']["0"]["ratio_unread"]:
                return True
            elif ratio_unchar > shorter_cmd_rules['condition']["1"]["ratio_unchar"] and ratio_unread > shorter_cmd_rules['condition']["1"]["ratio_unread"]:
                return True
            elif ratio_unchar > shorter_cmd_rules['condition']["2"]["ratio_unchar"] and ratio_unread > shorter_cmd_rules['condition']["2"]["ratio_unread"]:
                return True
            elif ratio_special > shorter_cmd_rules['condition']["3"]["ratio_special"] and ratio_unread > shorter_cmd_rules['condition']["3"]["ratio_unread"]:
                return True
            else:
                w_s = shorter_cmd_rules['ws']  # The weight of special chars
                w_c = shorter_cmd_rules['wc']  # The weight of unreadable chars
                w_u = shorter_cmd_rules['wu']   # The weight of unreadable words
                score = ratio_special * w_s + ratio_unchar * w_c + ratio_unread * w_u #+ ratio_str * w_l #Calc the final score.
                if score > 0.2:
                    return True
    
                else:
                    return False
        elif len(self.cmd) > shortest_cmd_rules['length']: # shortest cmd case
            if ratio_special > shortest_cmd_rules["condition"]["0"]["ratio_special"] and ratio_unread > shortest_cmd_rules["condition"]["0"]["ratio_unread"]:
                return True

            elif ratio_unchar > shortest_cmd_rules["condition"]["1"]["ratio_unchar"] and ratio_unread > shortest_cmd_rules["condition"]["1"]["ratio_unread"]:
                return True

            elif ratio_unchar > shortest_cmd_rules["condition"]["2"]["ratio_unchar"] and ratio_unread > shortest_cmd_rules["condition"]["2"]["ratio_unread"]:
                return True

            elif ratio_special > shortest_cmd_rules["condition"]["3"]["ratio_special"] and ratio_unread > shortest_cmd_rules["condition"]["3"]["ratio_unread"]:
                return True

            else:
                w_ss = shortest_cmd_rules["ws"] # The weight of special chars
                w_cc = shortest_cmd_rules['wc'] # The weight of unreadable chars
                w_uu = shortest_cmd_rules['wu']  # The weight of unreadable words
                score = ratio_special * w_ss + ratio_unchar * w_cc + ratio_unread * w_uu #Calc the final score.
                if score > 0.2:
                    return True
    
                else:
                    return False
        else:
            return False
    
    def _detect_obfuscation(self):
        if win_generic_filter_plugin(self.cmd).result == False:
            check = self._check() 
            if check == True:
                return {"obfuscated": True, "reason": "windows.obfus.generic"}
            else:
                return {"obfuscated": False, "reason": ""}
        else:
            return {"obfuscated": False, "reason": ""}

if __name__ == '__main__':
    
    sample = ''
    print('sample command:\n'+sample+'\n')
    a = win_generic_detect_plugin(cmd)
    a._detect_obfuscation()