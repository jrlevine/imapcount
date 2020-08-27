#!/usr/bin/env python3
#
# count null bodies from imap server
# detects problem where \n rather than \r\n line terminator puts the
# whole message intop the header

import imapclient
import datetime
from email.header import decode_header

class Imapnull:
    def __init__(self, host='imap.ietf.org', iuser='anonymous', ipass='guest',debug=False):

        self.i = imapclient.IMAPClient(host,ssl=True)
        self.i.login(iuser, ipass)
        self.debug = debug
        
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

    def dofolder(self, mlist, chunk=100, month=False, count=None):
        """
        read message bodies
        """

        fname = self.list2folder(mlist)
        if not fname:
            print("no folder",mlist)
            return

        # this better work
        f = self.i.select_folder(fname, readonly=True)
        
        if month:
                    self.newtbase = datetime.datetime.today()
        self.month = month
        if month:
            self.newtbase = datetime.datetime.today()
            self.tbase = self.newtbase - datetime.timedelta(days=30)
            if self.debug:
                print("from",self.tbase,"to",self.newtbase)
            ym = self.i.search([u'SINCE', self.tbase]) # get the last month's
        else:
            ym = self.i.search(['ALL'])
            if count and count < len(ym):
                ym = ym[-count:]
        if self.debug:
            print("nmsgs", len(ym))
        ymo = []
        while ym:
            ymc = ym[:chunk]
            if self.debug:
                print("chunk",ymc[0], ymc[-1])
            msgs = self.i.fetch(ymc,[b'RFC822.TEXT'])

            for mn, j in msgs.items():
                s = j[b'RFC822.TEXT']
                if len(s) == 0:
                    print(mn)
                    ymo.append(mn)
            del ym[:chunk]
        return ymo
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='count null messages')
    parser.add_argument("-d", action='store_true', help='debug stuff')
    parser.add_argument("-c", type=int, help='chunk size', default=100)
    parser.add_argument("-n", type=int, help='look at last N messages')
    parser.add_argument("-m", action='store_true', help='month rather than all')
    parser.add_argument("list", type=str, help='list to count')
    args = parser.parse_args()

    ii = Imapnull(debug=args.d)
    print("nulls",ii.dofolder(args.list, chunk=args.c, month=args.m, count=args.n))
