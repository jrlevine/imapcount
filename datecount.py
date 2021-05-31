#!/usr/bin/env python3
#
# count message dates

import pymysql
import imapclient
import datetime
from email.header import decode_header
import sys

badlists = { "dmarc-report" }

class Datecount:
    def __init__(self, host='imap.ietf.org', iuser='anonymous', ipass='guest',
        months=12, doupdate=False, debug=False):

        if debug:
            print("connect to",host)
        self.i = imapclient.IMAPClient(host, port=143, ssl=False)
        if debug:
            print("starttls")
        self.i.starttls()
        if debug:
            print("log in as",iuser)
        self.i.login(iuser, ipass)
        if debug:
            print("logged in")
        self.debug = debug
        
        # how long
        self.months = months
        self.folders = None

        if doupdate:
            self.db = pymysql.connect(user='datecount',passwd='x',db='datecount', charset='utf8', use_unicode=True)
        else:
            self.db = None

    def closeimap(self):
        self.i.logout()

    def getfolders(self):
        """
        get a list of live folders
        """
        l = self.i.list_folders()
        self.folders = tuple( f[2] for f in l if not br'\Noselect' in f[0] )
        return self.folders

    def list2folder(self, lname):
        """
        lname is name of list
        flist is list of folders from getfolders
        """
        if not self.folders:
            self.getfolders()

        flist = self.folders

        for x in flist:
            if x.endswith("/"+ lname):
                return x
        return None

    def dofolder(self, mlist=None, fname=None):
        """
        read new messages from a folder
        report number and size, by count if count otherwise size
        derole domain to say "Role Aaccount"
        fto address to put into a To: header
        """

        if mlist:
            fname = self.list2folder(mlist)

        if not fname:
            print("no folder",mlist, file=sys.stderr)
            return False
        if not mlist:
            mlist = fname.rsplit('/')[-1]

        # this better work
        f = self.i.select_folder(fname, readonly=True)
        
        now = datetime.datetime.today()
        nyears = self.months // 12
        nmonths = self.months % 12
        tbase = now  - datetime.timedelta(days=int(self.months*30.25))

        if self.debug:
            print("from",tbase,"to", now)
        ym = self.i.search(['SINCE', tbase]) # get the last week's or month's

        if self.debug:
            print("date list",ym)

        msgs = self.i.fetch(ym,[b'ENVELOPE'])

        utc = datetime.timezone.utc

        hours = 24 * [0]
        days = 7 * [0]
        bogus = 0

        for mn, j in msgs.items():
            e = j[b'ENVELOPE']
            d = e.date
            # turn into UTC
            ud = d.astimezone(utc)
            if ud.hour or ud.minute:
                hours[ud.hour] += 1
            else:
                bogus += 1
            days[ud.weekday()] += 1
        print(fname)
        print(hours, sum(hours), bogus, '/', days, sum(days))
        if self.db:
            hargs = [ (mlist, i, hours[i]) for i in range(24) if hours[i] > 0 ]
            dargs = [ (mlist, i, days[i]) for i in range(7) if days[i] > 0 ]
            if self.debug:
                print(hargs)
                print(dargs)
            if hargs:
                with self.db.cursor() as cur:
                    cur.executemany("""REPLACE INTO hours(mlist,hour,nhours) VALUES(%s,%s,%s)""", hargs)
                    cur.executemany("""REPLACE INTO days(mlist,wday,ndays) VALUES(%s,%s,%s)""", dargs)
                self.db.commit()

    def allfolders(self):
        """
        iterate over all the folders
        """
        if not self.folders:
            self.getfolders()

        flist = self.folders
        for f in flist:
            mlist = f.split('/')[-1]
            if mlist not in badlists:   # mail not from humans
                self.dofolder(fname=f)

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='make date histogram')
    parser.add_argument("-d", action='store_true', help='debug stuff')
    parser.add_argument("-m", type=int, help='number of months', default=12)
    parser.add_argument("-u", action='store_true', help='update database')
    parser.add_argument("list", type=str, help='list to count or "all"')
    args = parser.parse_args()

    di = Datecount(months=args.m, debug=args.d, doupdate=args.u)
    if args.list == "all":
        di.allfolders()
    else:
        di.dofolder(args.list)
