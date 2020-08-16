#!/usr/bin/env python3
#
# count messages from imap server

import imapclient
import datetime
from email.header import decode_header

class Imapcount:
    def __init__(self, host='imap.ietf.org', iuser='anonymous', ipass='guest',
        month=False, debug=False):

        self.i = imapclient.IMAPClient(host,ssl=True)
        self.i.login(iuser, ipass)
        self.debug = debug
        
        # one week
        self.newtbase = datetime.datetime.today()
        self.month = month
        if month:
            b = self.newtbase
            if b.month == 1:
                self.tbase = datetime.datetime(b.year-1, 12, b.day, b.hour, b.minute, b.second)
            else:
                self.tbase = datetime.datetime(b.year, b.month-1, b.day, b.hour, b.minute, b.second)
        else:
            self.tbase = self.newtbase - datetime.timedelta(days=7)
        if debug:
            print("from",self.tbase,"to",self.newtbase)
            
        self.folders = None

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

    def dofolder(self, mlist, count=False, fto=None):
        """
        read new messages from a folder
        count number and volume by sender
        """

        fname = self.list2folder(mlist)
        if not fname:
            print("no folder",mlist)
            return

        # this better work
        f = self.i.select_folder(fname, readonly=True)
        
        ym = self.i.search([u'SINCE', self.tbase]) # get the last week's or month's
        if self.debug:
            print("date list",ym)

        msgs = self.i.fetch(ym,[b'RFC822.SIZE', b'ENVELOPE'])

        mname = {}
        mcount = {}
        msize = {}

        for mn in iter(msgs):
            j = msgs[mn]
            e = j[b'ENVELOPE']
            s = j[b'RFC822.SIZE']
            ef = e.from_[0]
            addr = f"{ef.mailbox.decode()}@{ef.host.decode()}"
            if not addr in mname:
                if ef.name:
                    mname[addr] = ef.name.decode()
                else:
                    mname[addr] = ""
                mcount[addr] = 0
                msize[addr] = 0
            mcount[addr] += 1
            msize[addr] += s

        ftime = self.newtbase.strftime("%c")
        if fto:
            print(f"To: {fto}")
        print(f'Subject: Messages from the {mlist} list for the {"month" if self.month else "week"} ending {ftime}')
        # for decoded names
        print("Content-Type: text/plain; charset=utf-8")
        print("Mime-Version: 1.0")
        print("Content-Transfer-Encoding: 8bit")
        print()

        addrs = list(mname)
        if count:
            addrs.sort(key=lambda a: msize[a], reverse=True) # sort by size
            addrs.sort(key=lambda a: mcount[a], reverse=True) # sort by count
        else:
            addrs.sort(key=lambda a: mcount[a], reverse=True) # sort by count
            addrs.sort(key=lambda a: msize[a], reverse=True) # sort by size
        for a in addrs:
            aname = mname[a]
            if aname.startswith('=?'):
                dh = decode_header(aname)[0]
                aname = dh[0].decode(dh[1])

            print("{0:3d} |{1:7d} | {2} <{3}>".format(mcount[a], msize[a], aname, a))

        self.i.close_folder()


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='count messages')
    parser.add_argument("-d", action='store_true', help='debug stuff')
    parser.add_argument("-m", action='store_true', help='month rather than week')
    parser.add_argument("-c", action='store_true', help='sort by count')
    parser.add_argument("--to", type=str, help='To address')
    parser.add_argument("list", type=str, help='list to count')
    args = parser.parse_args()

    ii = Imapcount(month=args.m, debug=args.d)
    ii.dofolder(args.list, count=args.c, fto=args.to)
