<p align="center">
  <img src="doc/logo.png" width="150">
</p>

<h1 align="center">Flerken</h1>

<p align="center">
  
  <img src="https://img.shields.io/badge/python-3.x-orange.svg" alt="python 3.x">
  <img src="http://img.shields.io/badge/license-APL2-brightgreen.svg?style=flat" alt="license">
  
</p>

## Web Demo Quick Install

- <b>Installation</b>
  
  #### Step 1: Ensure you have installed python 3.x on your server, you can use the following command to check it.
  
  `[root@server:~$] python -V`
  
  #### Step 2: Install the required components, all the prerequisite components have been declared in requirement.txt.
  
  `[root@server:~$] pip install -r requirement.txt`
  
  #### Step 3: Login in your MySQL console, and import database
  
  `source /your path/Flerken/flerken/lib/flerken.sql`
  
  #### Step4: Custom your Flerken APP config as you want.
  `Path: flerken/config/global_config.py`
  
  #### Step5: Now you can run it!
   `[root@server:~$] python runApp.py`
   
  #### Step 6(Optional): You can build your own whitelists for reducing false positive rate.
  `Path: flerken/config/whitelists/`

 
- <b>How to use</b> 

  #### It's very easy to use as shown in the following picture, and we will also release API interfaces as soon.

<p align="center">
  <img src="doc/intro-animation.gif" width="95%">
</p>

## Getting Help

If you have any question or feedbacks on Flerken. Please create an issue and choose a suitable label for it. We will solve it as soon as possible.

<p align="center">
  <img src="doc/labels.png" width="95%">
</p>

## CHANGELOG

Please see our <a href="./CHANGELOG.md">CHANGELOG.md</a>

## Build-in 3rd parties

- <b>[Flask](http://flask.pocoo.org)</b>
- <b>[Flask-WTF](https://flask-wtf.readthedocs.io/en/stable)</b>
- <b>[Flask-Limiter](https://flask-limiter.readthedocs.io)</b>
- <b>[frankie-huang/pythonMySQL](https://github.com/frankie-huang/pythonMySQL)</b>
- <b>[jQuery](https://jquery.org)</b>
- <b>[Swiper](https://idangero.us/swiper)</b>

## License

Flerken is released under the Apache 2.0 license.
