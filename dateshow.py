#!/usr/local/bin/python3
#
# show message counts

from bottle import request, route, get, post, run, hook, app, template, view, \
    static_file, redirect, HTTPResponse, BaseRequest
import pymysql
import re, sys

debug = False

# allow large zones
BaseRequest.MEMFILE_MAX = 1024*1024

db = None

if __name__=="__main__":
    if len(sys.argv) >= 2 and sys.argv[1].startswith("debug"):
        debug = True
        print("Debugging on")

myapp = app()

# print something in red
def inred(msg):
    if msg:
        return '<font color="red">{0}</font>'.format(msg)
    return msg    

def boilerplate():
    """
    boilerplate toolbar at the top of each page
    """
    here = request.path
    def bp(page, desc):
        if here == page:
            return "<li><a href=\"{}\" class=active>{}</a></li>\n".format(page,desc)
        else:
            return "<li><a href=\"{}\">{}</a></li>\n".format(page,desc)

    bo = "<ul id=tabnav>\n"
    bo += bp("/hours","Hours")
    bo += bp("/days","Days")
#    bo += bp("/lists","Lists")
    bo += "</ul>\n<p align=right>Mailing list date summaries"
    bo += "</p>"
    return bo

### database
def getdb():
    global db

    if not db:
        db = pymysql.connect(user='datecount',passwd='x',db='datecount', charset='utf8', use_unicode=True)
    return db

    
@get('/')
def starthere():
    return statuspage("Click on Hours or on Days")

@get('/hours')
@view('hours')
def hours():
    """
    make chart by hours
    """
    sql = """select hour,sum(nhours) from hours group by hour order by hour"""

    hourdata = 24 * ["0"]
    hournames = ", ".join(map(str, range(24)))
    getdb()
    with db.cursor() as cur:
        cur.execute(sql)
        for h,s in cur.fetchall():
            hourdata[h] = str(s)
    shourdata = ", ".join(hourdata)
    return dict(boilerplate=boilerplate(), hournames=hournames, hourdata=shourdata)

@get('/days')
@view('days')
def days():
    """
    make chart by day
    """
    sql = """select days.wday, dayname, sum(ndays) from days join daynames using (wday) group by wday;"""
    
    daydata = 7 * ["0"]
    daynames = []
    getdb()
    with db.cursor() as cur:
        cur.execute(sql)
        for d,n,s in cur.fetchall():
            daydata[d] = str(s)
            daynames.append(f'"{n}"')
            
    sdaynames = ", ".join(daynames)
    sdaydata = ", ".join(daydata)
    return dict(boilerplate=boilerplate(), daynames=sdaynames, daydata=sdaydata)


@view('failpage')
def failpage(why):
    """ return a failure page
    """
    return dict(boilerplate=boilerplate(),
        kvetch=why)

@view('statuspage')
def statuspage(why):
    """ return a status page
    """
    return dict(boilerplate=boilerplate(),
        kvetch=why)

################################################################
# for CSS and images
@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./static')

@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./static')

@route('/robots.txt')
def robots():
    return static_file('robots.txt', root='./static')

################# main stub for debugging
if __name__=="__main__":
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "debug":
        run(app=myapp, host='localhost', port=8803, debug=True, reloader=True)
    else:
        run(app=myapp, server="cgi", debug=True)
