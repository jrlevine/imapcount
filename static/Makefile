# install static files appropriate place

# web server
WEB ?= /usr/local/www/eaitest

SWEB=${WEB}/static

STATIC=eaitest.css favicon.ico robots.txt

all: static
	@echo static files made

static:	${STATIC}

install:	static
	mkdir -p ${SWEB}
	cp -f ${STATIC} ${SWEB}
