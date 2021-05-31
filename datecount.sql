-- counts of message times

CREATE TABLE hours (
    mlist VARCHAR(255) NOT NULL,
    hour TINYINT(2) UNSIGNED NOT NULL,
    nhours INT UNSIGNED NOT NULL,
    PRIMARY KEY(mlist,hour)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE days (
    mlist VARCHAR(255) NOT NULL,
    wday TINYINT(1) UNSIGNED NOT NULL,
    ndays INT UNSIGNED NOT NULL,
    PRIMARY KEY(mlist,wday)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE daynames (
    wday TINYINT(1) UNSIGNED PRIMARY KEY,
    dayname varchar(10)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO daynames VALUES (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday');
