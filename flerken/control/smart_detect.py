#!/usr/bin/python
# -*-coding:utf-8-*-

""" 
Flerken smart detect logic
"""

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

import sys
import os
import hashlib
import time
import re
from flerken import app
try:
    from .plugins.linux_generic_detect_plugin import linux_generic_detect_plugin
except Exception: 
    from plugins.linux_generic_detect_plugin import linux_generic_detect_plugin
try:
    from .plugins.win_special_detect_plugin import win_special_detect_plugin
except Exception: 
    from plugins.win_special_detect_plugin import win_special_detect_plugin
try:
    from .plugins.win_generic_detect_plugin import win_generic_detect_plugin
except Exception:
    from plugins.win_generic_detect_plugin import win_generic_detect_plugin
try:
    from .plugins.custom_meta_chars_plugin import custom_meta_chars_plugin
except Exception:
    from plugins.custom_meta_chars_plugin import custom_meta_chars_plugin
try:
    from .plugins.linux_special_detect_plugin import linux_special_detect_plugin
except Exception:
    from plugins.linux_special_detect_plugin import linux_special_detect_plugin
try:
    from .plugins.linux_graphic_detect_plugin import linux_graphic_detect_plugin
except Exception:
    from plugins.linux_graphic_detect_plugin import linux_graphic_detect_plugin

class smart_detect(object):

    def __init__(self,cmd):
        app.logger.info('='*50)
        app.logger.info('[+]time: '+datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.original_cmd = cmd
        app.logger.info('[+]original cmd: '+self.original_cmd)
        self.cmd = custom_meta_chars_plugin(cmd).result
        app.logger.info('[+]meta cmd: '+self.cmd)
        self.start_time = time.time()

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

    def _hash_calc(self):
        sha256 = hashlib.sha256()
        sha256.update((self.cmd).encode('UTF8'))
        return sha256.hexdigest()

    def linux_identify(self):
        linux_identification_generic = linux_generic_detect_plugin(self.cmd).result
        linux_identification_graphic = linux_graphic_detect_plugin(self.cmd).result
        linux_identification_special = linux_special_detect_plugin(self.cmd).result
        app.logger.info('[+]linux_identification_generic: '+str(linux_identification_generic))
        app.logger.info('[+]linux_identification_graphic: '+str(linux_identification_graphic))
        app.logger.info('[+]linux_identification_special: '+str(linux_identification_special))
        if linux_identification_graphic['obfuscated'] == True:
            self.end_time = time.time()
            linux_identification_graphic['measure_time'] = str(round(self.end_time - self.start_time,5)) + 's'
            linux_identification_graphic['hash'] = 'sha256: ' + self._hash_calc()
            linux_identification_graphic['platform'] = 'linux'
            linux_identification_graphic['cmd'] = self.original_cmd
            linux_identification_graphic['res'] = 0
            return linux_identification_graphic
        elif linux_identification_graphic['obfuscated'] == False and linux_identification_special['obfuscated'] == True:
            self.end_time = time.time()
            linux_identification_special['measure_time'] = str(round(self.end_time - self.start_time,5)) + 's'
            linux_identification_special['hash'] = 'sha256: ' + self._hash_calc()
            linux_identification_special['platform'] = 'linux'
            linux_identification_special['cmd'] = self.original_cmd
            linux_identification_special['res'] = 0
            return linux_identification_special
        else:
            self.end_time = time.time()
            linux_identification_generic['measure_time'] = str(round(self.end_time - self.start_time,5)) + 's'
            linux_identification_generic['hash'] = 'sha256: ' + self._hash_calc()
            linux_identification_generic['platform'] = 'linux'
            linux_identification_generic['cmd'] = self.original_cmd
            linux_identification_generic['res'] = 0
            return linux_identification_generic
    
    def win_identify(self):
        if len(self.cmd) <= 20:
            app.logger.info('[+]win_identify cmd length < 20')
            win_identification = dict()
            win_identification['res'] = 0
            win_identification['obfuscated'] = False
            win_identification['reason'] =''
            self.end_time = time.time()
            win_identification['measure_time'] = str(round(self.end_time - self.start_time,5)) + 's'
            win_identification['hash'] = 'sha256: ' + self._hash_calc()
            win_identification['platform'] = 'windows'
            win_identification['cmd'] = self.original_cmd
            return win_identification

        special_res = win_special_detect_plugin(self.cmd).result
        generic_res = win_generic_detect_plugin(self.cmd).result
        app.logger.info('[+]win_special_res: '+str(special_res))
        app.logger.info('[+]win_generic_res: '+str(generic_res))
        if generic_res['obfuscated'] == True:
            win_identification = dict()
            win_identification['res'] = 0
            if len(self.cmd) >= 50:
                win_identification['obfuscated'] = generic_res['obfuscated']
                win_identification['reason'] = generic_res['reason']
            else:
                win_identification['obfuscated'] = 'suspicious'
                win_identification['reason'] = 'windows.suspicious.generic'
            self.end_time = time.time()
            win_identification['measure_time'] = str(round(self.end_time - self.start_time,5)) + 's'
            win_identification['hash'] = 'sha256: ' + self._hash_calc()
            win_identification['platform'] = 'windows'
            win_identification['cmd'] = self.original_cmd
            return win_identification

        elif generic_res['obfuscated'] == False and special_res['obfuscated'] == True:
            win_identification = dict()
            win_identification['res'] = 0
            win_identification['obfuscated'] = special_res['obfuscated']
            win_identification['reason'] = special_res['reason']
            self.end_time = time.time()
            win_identification['measure_time'] = str(round(self.end_time - self.start_time,5)) + 's'
            win_identification['hash'] = 'sha256: ' + self._hash_calc()
            win_identification['platform'] = 'windows'
            win_identification['cmd'] = self.original_cmd
            return win_identification
        else:
            win_identification = dict()
            win_identification['res'] = 0
            win_identification['obfuscated'] = False
            win_identification['reason'] = ''
            self.end_time = time.time()
            win_identification['measure_time'] = str(round(self.end_time - self.start_time,5)) + 's'
            win_identification['hash'] = 'sha256: ' + self._hash_calc()
            win_identification['platform'] = 'windows'
            win_identification['cmd'] = self.original_cmd
            return win_identification

    def not_sure_identify(self):
        linux_identify_res = self.linux_identify()
        if linux_identify_res['obfuscated'] == True:
            linux_identify_res['likely_platform'] = 'linux'
            linux_identify_res.pop('platform')
            return linux_identify_res
        else:
            win_identify_res = self.win_identify()
            if win_identify_res['obfuscated'] == True or win_identify_res['obfuscated'] == 'suspicious':
                win_identify_res['likely_platform'] = 'windows'
                win_identify_res.pop('platform')
                return win_identify_res
            else:
                not_sure_res = linux_identify_res
                not_sure_res['likely_platform'] = ''
                return not_sure_res

if __name__ == '__main__':

    #test
    sample = 'ki=w;das=ho;qq=ami;$ki$das$qq'
    print('input cmd: '+sample)
    a = smart_detect(sample)
    out = a.linux_identify()