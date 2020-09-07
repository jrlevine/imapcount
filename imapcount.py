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
        
        # one week or month
        self.month = month
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

    def dofolder(self, mlist, count=False, fto=None, derole=None, prev=None):
        """
        read new messages from a folder
        report number and size, by count if count otherwise size
        derole domain to say "Role Aaccount"
        fto address to put into a To: header
        """

        fname = self.list2folder(mlist)
        if not fname:
            print("no folder",mlist)
            return

        # this better work
        f = self.i.select_folder(fname, readonly=True)
        
        if self.month:
            ndays = 30                  # fake months
        else:
            ndays = 7

        now = datetime.datetime.today()
        if prev:
            tend = now  - datetime.timedelta(days=ndays*prev)
            tbase = tend - datetime.timedelta(days=ndays)
            if self.debug:
                print("from",self.tbase,"to",self.newtbase)
            ym = self.i.search(['BEFORE', tend, 'SINCE', tbase]) # get that week's stuff
        else:
            tend = now
            tbase = now  - datetime.timedelta(days=ndays)
            if self.debug:
                print("from",tbase,"to", now)
            ym = self.i.search(['SINCE', tbase]) # get the last week's or month's

        if self.debug:
            print("date list",ym)

        msgs = self.i.fetch(ym,[b'RFC822.SIZE', b'ENVELOPE'])

        mname = {}
        mcount = {}
        msize = {}

        for mn, j in msgs.items():
            e = j[b'ENVELOPE']
            s = j[b'RFC822.SIZE']
            ef = e.from_[0]
            addr = f"{ef.mailbox.decode()}@{ef.host.decode()}".lower()
            if not addr in mname:
                if ef.name:
                    if derole and ef.host.decode() == derole:
                        mname[addr] = 'Role account'
                    else:
                        mname[addr] = ef.name.decode()
                else:
                    mname[addr] = ""
                mcount[addr] = 0
                msize[addr] = 0
            mcount[addr] += 1
            msize[addr] += s

        ftime = tend.strftime("%c")
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
            addrs.sort(key=lambda a: (mcount[a], msize[a]), reverse=True) # sort by count, size
        else:
            addrs.sort(key=lambda a: (msize[a], mcount[a]), reverse=True) # sort by size, count

        for a in addrs:
            aname = mname[a]
            if '=?' in aname:
                try:
                    dhl = decode_header(aname)
                    aname = ""
                    for dhs, dht in dhl:
                        if type(dhs) is str:
                            aname += dhs
                        elif dht is None:
                            aname += dhs.decode()
                        else:
                            aname += dhs.decode(dht)
                except Exception as err: # in case something we can't decode
                    aname = f"{mname[a]} ({err})"

            print("{0:3d} |{1:7d} | {2} <{3}>".format(mcount[a], msize[a], aname, a))

        self.i.close_folder()


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='count messages')
    parser.add_argument("-d", action='store_true', help='debug stuff')
    parser.add_argument("-m", action='store_true', help='month rather than week')
    parser.add_argument("-c", action='store_true', help='sort by count')
    parser.add_argument("-p", type=int, help='previous N weeks or months')
    parser.add_argument("--to", type=str, help='To address')
    parser.add_argument("-r", type=str, help='Role account domain')
    parser.add_argument("list", type=str, help='list to count')
    args = parser.parse_args()

    ii = Imapcount(month=args.m, debug=args.d)
    ii.dofolder(args.list, count=args.c, fto=args.to, derole=args.r, prev=args.p)
