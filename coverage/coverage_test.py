#!/usr/bin/python
# -*-coding:utf-8-*-

__author__ = 'Yao Zhang & Zhiyang Zeng'
__copyright__   = "Copyright 2019, Apache License 2.0"

import sys
import os
sys.path.append('../flerken/control')
from smart_detect import smart_detect

LINUX_SAMPLE_PATH = 'samples/linux.txt'
WIN_SAMPLE_PATH = 'samples/win.txt'
OUTPUT_PATH = 'output'

def win_sample_test():
    total = 0
    obfus = 0
    with open(os.path.join(OUTPUT_PATH,'win_res.txt'),'w') as fo:
            #read sample file
            with open(WIN_SAMPLE_PATH) as fs:
                for cmd in fs.readlines():
                    total = total + 1
                    smart = smart_detect(cmd)
                    res = smart.not_sure_identify()
                    if res['obfuscated'] == True and res['likely_platform'] == 'windows':
                        obfus = obfus + 1
                        fo.write('[windows obfuscated]: '+cmd+'\n')
                    elif res['obfuscated'] == True and res['likely_platform'] == 'linux':
                        fo.write('[wrong platform detected]: '+cmd+'\n')
                    else:
                        fo.write('[not obfuscated detected]: '+cmd+'\n')
    print("windows coverage rate is "+str(round((obfus/total),5)*100)+'%')
                    
def linux_sample_test():
    total = 0
    obfus = 0
    with open(os.path.join(OUTPUT_PATH,'linux_res.txt'),'w') as fo:
            #read sample file
            with open(LINUX_SAMPLE_PATH) as fs:
                for cmd in fs.readlines():
                    total = total + 1
                    smart = smart_detect(cmd)
                    res = smart.not_sure_identify()
                    if res['obfuscated'] == True and res['likely_platform'] == 'linux':
                        obfus = obfus + 1
                        fo.write('[linux obfuscated]: '+cmd+'\n')
                    elif res['obfuscated'] == True and res['likely_platform'] == 'windows':
                        fo.write('[wrong platform detected]: '+cmd+'\n')
                    else:
                        fo.write('[not obfuscated detected]: '+cmd+'\n')
    print("linux coverage rate is "+str(round((obfus/total),5)*100)+'%')

if '__main__' == __name__:
    print('''
            ________________              ______                
            ___  ____/___  /_____ ___________  /_______ _______ 
            __  /_    __  / _  _ \__  ___/__  //_/_  _ \__  __ \\
            _  __/    _  /  /  __/_  /    _  ,<   /  __/_  / / /
            /_/       /_/   \___/ /_/     /_/|_|  \___/ /_/ /_/ 
                                                      
    Flerken Coverage Test Tool, All Your Obfuscations Are Belong To Us!
          ''')
    
    print("[+]Checking windows samples, please waiting...")
    win_sample_test()
    print("[+]Checking linux samples, please waiting...")
    linux_sample_test()