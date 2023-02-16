#!/usr/bin/env python

import json
try:
    f = open("/tmp/wall.json","r")
    wall = json.load(f)
except:
    wall = []

login_form="""
<html><form>
What is your name? <input type=text name=user><br/>
<input type=submit name=login value=login>
</form></html>
"""

def index(req, user='', text=''):
    if user == '': return login_form
    if text != "": 
        wall.append((user, text))
        f = open("/tmp/wall.json","w")
        json.dump(wall, f)
    
    html = "<html><h2>wall</h2>"
    for post in wall:
        html += post[0]+" - "+post[1]+"<br/>"
        html += "<form>"
        html += '<p><input type=text name=text><input type=submit value=comment>'
        html += "<input type=hidden name=user value="+user+">"
        html += "<p><a href='wall.py'>Exit</a></p>"
        html += '</html>'
        return html

