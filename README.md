# imapcount

Small python script to count recent messages in an imap folder and format
the result to mail out

Options are count for a week (default) or a month, and sort by count or size (default)

Requires the imapclient module

# datecount

Make histograms of messages by hour and day of the week

datecount.sql defines the MySQL database

datecount.py counts message times by list for some period, default a year

dateshow.py and views/ and static/ WSGI script to display the data

