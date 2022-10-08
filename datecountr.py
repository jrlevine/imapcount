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
        months=12, dates=None, doupdate=False, debug=False, dotz=False):

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
        if dates:
            self.dates = dates
        else:
            self.months = months
            now = datetime.datetime.today()
            tbase = now  - datetime.timedelta(days=int(self.months*30.25))
            self.dates = [ (tbase, now) ]

        self.folders = None

        if doupdate:
            self.db = pymysql.connect(user='datecount',passwd='x',db='datecount', charset='utf8', use_unicode=True)
        else:
            self.db = None
        self.results = dict()           # time zones
        self.dotz = dotz
        
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
        
        hours = 24 * [0]
        days = 7 * [0]
        utc = datetime.timezone.utc

        for x in self.dates:
            (tbase, tend) = x
            ym = self.i.search(['SINCE', tbase, 'BEFORE', tend]) # get the date range

            if self.debug:
                print(f"date list {tbase}->{tend}", ym[:20])

            if self.dotz:
                msgs = self.i.fetch(ym,[b'ENVELOPE',b'RFC822.HEADER'])
            else:
                msgs = self.i.fetch(ym,[b'ENVELOPE'])
            for mn, j in msgs.items():
                e = j[b'ENVELOPE']
                d = e.date
                # turn into UTC
                ud = d.astimezone(utc)
                hours[ud.hour] += 1
                days[ud.weekday()] += 1

                if self.dotz:
                    h = j[b'RFC822.HEADER']
                    h2 = h.replace(b'\r\n ', b'  ') # combine continued lines
                    hl = h2.split(b'\r\n')
                    hd = [ x.decode(errors='replace') for x in hl if x.lower().startswith(b'date:') ]
                    htz = hd[0].split()[-1]
                    if htz in self.results:
                        self.results[htz] += 1
                    else:
                        self.results[htz] = 1

        print(fname)
        print(hours, sum(hours), '/', days, sum(days))
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

    def tzresults(self):
        """ get results in order
        """

        def intx(s):
            " int() with error default "
            try:
                return int(s)
            except:
                return 9999
                
        k = list(self.results.keys())
        k.sort(key=intx)
        return [ (i, self.results[i]) for i in k ]

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='make date histogram')
    parser.add_argument("-d", action='store_true', help='debug stuff')
    parser.add_argument("-m", type=int, help='number of months', default=12)
    parser.add_argument("-r", action='append', nargs=2, help='date ranges in form yyyy-mm-dd yyyy-mm-dd')
    parser.add_argument("-u", action='store_true', help='update database')
    parser.add_argument("-z", action='store_true', help='count time zones')
    parser.add_argument("list", type=str, help='list to count or "all"')
    args = parser.parse_args()

    dates = None
    if args.r:
        dates = []
        for ds,de in args.r:
            try:
                dds = datetime.date.fromisoformat(ds)
                ddst = datetime.datetime(dds.year, dds.month, dds.day, 0, 0, 0, tzinfo=datetime.timezone.utc)
                dde = datetime.date.fromisoformat(de)
                ddet = datetime.datetime(dde.year, dde.month, dde.day, 23, 59, 59, tzinfo=datetime.timezone.utc)
            except ValueError as err:
                print(err)
                exit(1)

            if args.d:
                print(f"from {ddst} to {ddet}", ddst, ddet)
            dates.append((ddst, ddet))

    di = Datecount(months=args.m, dates=dates, debug=args.d, doupdate=args.u, dotz=args.z)
    if args.list == "all":
        di.allfolders()
    else:
        di.dofolder(args.list)
    if args.z:
        r = di.tzresults()
        m = max((x[1] for x in r))
        
        for k, i in r:
            print("{0} {1:3d} {2}".format(k, i, int(50 * i / m) * '*'))

