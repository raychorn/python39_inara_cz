#!/usr/bin/env python
# -*- coding: utf8 -*-

# parse command line to get the database and wether we want to
# create the database.
from optparse import OptionParser

parser = OptionParser("usage: %prog -d DATABASE [-s]")
parser.add_option('-d', '--database', dest='database', help="DATABASE file name", metavar="DATABASE")
parser.add_option('-s', '--syncdb', dest='syncdb', action="store_true", help="should the database be created?")
parser.add_option('-r', '--repl', dest='repl', action="store_true", help="start a REPL with access to your models")

options, args = parser.parse_args()

if not options.database:
    parser.error("You must specify the database name")

# fetch the settings and cache them for later use
from standalone.conf import settings
settings = settings(
    DATABASE_ENGINE='sqlite3',
    DATABASE_NAME=options.database,
)

# build the models we want to have in the database
from standalone import models

class MyModel(models.StandaloneModel):

    col1 = models.CharField(max_length=1000)
    col2 = models.IntegerField()
    col3 = models.BooleanField()

    def __unicode__(self):
        return self.col1

from django.core.management import call_command

if options.syncdb:
    # run a simple command - here syncdb - from the management suite
    call_command('syncdb')
elif options.repl:
    # start the shell, access to your models through import standalone.models
    call_command('shell')
else:
    l = MyModel.objects.filter(col1='foo')
    if len(l):
        print "found", l[0]
    else:
        o = MyModel(col1='foo', col2=5, col3=3)
        o.save()
        print "new", o

