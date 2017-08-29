#!/usr/bin/env python

####################################################
# Standard packages from a local Python installation

import httplib
import mimetools
import mimetypes
import os
import os.path
import pwd
import simplejson
import socket
import stat
import sys
import tempfile

import urllib
import urllib2

##############################################
# This non-standard package is available from:
#
#   http://atlee.ca/software/poster/index.html
#
# See more information on it from:
#
#   http://stackoverflow.com/questions/680305/using-multipartposthandler-to-post-form-data-with-python

from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers

######################################
# And here follows the grabber's logic

from utilities import guessBeamline
# ------------------------------------------------------------
# Unspecified values of the LogBook parameters must be set
# either via commad line parameters or inrteractivelly before
# posting the messages.
# ---------------------------------------
beamline=guessBeamline()
logbook_author      = pwd.getpwuid(os.geteuid())[0]  # this is fixed
logbook_instrument  = beamline.upper()                 # command line parameter
#logbook_instrument  = "SXR"                           # command line parameter

# The dictionary of available experiments. Experiment names serve as keys.
# This information is equested from the web service. If a specific experiment
# was requestd on via a command-line parametyer then there will be only
# one entry in the dictionary.
#
# NOTE: Once initialized the dictionary must have at least one entry.

logbook_experiments = None

# ------------------------------------------------------------------
# Default values of these parameters can be changed via command line
# option of the application.
# ------------------------------------------------------------------

ws_url            = "https://pswww/pcdsn/ws-auth";      ## 'https://www-lclsdev.slac.stanford.edu:81/ws-auth/'
user=beamline.lower()+'opr'
ws_login_user     = user ## 'logbook'
#ws_login_user     = 'sxropr' ## 'logbook'
ws_login_password = 'pcds'

blinepython=beamline.lower()+'python'
class pypsElog:

    def __init__(self,experiment=None):
      ws_configure_auth()
      if (experiment is None):
        experiment=ws_get_current_experiment()
      self.experiment=experiment
      self.logbook_experiments = ws_get_experiments (experiment)

    def submit(self,text="TEXT TO DELETE",tag=blinepython,tag2=None,tag3=None,file=None,file_descr="description not known",file2=None,file_descr2="description not known",file3=None,file_descr3="description not known",runnum=None):
    #def submit(self,text="TEXT TO DELETE",tag="sxrpython",file=None,file_descr="description not known",file2=None,file_descr2="description not known",file3=None,file_descr3="description not known"):
        exper_id = self.logbook_experiments[self.experiment]['id']
        url = ws_url+'/LogBook/NewFFEntry4grabberJSON.php'
        
        data = [
          ('author_account', logbook_author),
          ('id', exper_id),
          ('message_text', text),
          ('scope', 'experiment')]
        if tag2 is None:
          data.extend([
            ('num_tags', '1'),
            ('tag_name_0',tag),
            ('tag_value_0','')
          ])
        elif tag3 is None:
          data.extend([
            ('num_tags', '2'),
            ('tag_name_0',tag),
            ('tag_value_0',''),
            ('tag_name_1',tag2),
            ('tag_value_1','')
          ])
        else:
          data.extend([
            ('num_tags', '3'),
            ('tag_name_0',tag),
            ('tag_value_0',''),
            ('tag_name_1',tag2),
            ('tag_value_1',''),
            ('tag_name_2',tag3),
            ('tag_value_2',''),
          ])


        if (file is None):
          pass
        elif (file2 is None):
          data.extend([
            MultipartParam.from_file("file1", file ),
            ("file1", file_descr)])
        elif(file3 is None):
          data.extend([
            MultipartParam.from_file("file1", file ),
            ("file1", file_descr), 
            MultipartParam.from_file("file2", file2 ),
            ("file2", file_descr2) ])
        else:
          data.extend([
            MultipartParam.from_file("file1", file ),
            ("file1", file_descr), 
            MultipartParam.from_file("file2", file2 ),
            ("file2", file_descr2),
            MultipartParam.from_file("file3", file3 ),
            ("file3", file_descr3) ])

        datagen,headers = multipart_encode(data)

        try:
            req = urllib2.Request(url, datagen, headers)
            response = urllib2.urlopen(req)
            the_page = response.read()
            result = simplejson.loads(the_page)
            if result['status'] != 'success':
                tkMessageBox.showerror ( "Error", result['message'])
            new_message_id = int(result['message_id'])

        except urllib2.URLError, reason:
            tkMessageBox.showerror (
                "Submit New Message Error",
                reason )
        except urllib2.HTTPError, code:
            tkMessageBox.showerror (
                "Submit New Message Error",
                code )

    def submit_old(self,text="TEXT TO DELETE",tag=blinepython,file=None,file_descr="description not known",file2=None,file_descr2="description not known",file3=None,file_descr3="description not known",runnum=None):
    #def submit(self,text="TEXT TO DELETE",tag="sxrpython",file=None,file_descr="description not known",file2=None,file_descr2="description not known",file3=None,file_descr3="description not known"):
        exper_id = self.logbook_experiments[self.experiment]['id']
        url = ws_url+'/LogBook/iNewFFEntry4grabberJSON.php'
        if (file is None):
          data = (
            ('author_account', logbook_author),
            ('id', exper_id),
            ('message_text', text),
            ('scope', 'experiment'),
            ('num_tags', '1'),
            ('tag_name_0',blinepython),
            ('tag_value_0',tag))
        elif (file2 is None):
          data = (
            ('author_account', logbook_author),
            ('id', exper_id),
            ('message_text', text),
            ('scope', 'experiment'),
            ('num_tags', '1'),
            ('tag_name_0',blinepython),
            ('tag_value_0',tag),
            MultipartParam.from_file("file1", file ),
            ("file1", file_descr) )
        elif(file3 is None):
          data = (
            ('author_account', logbook_author),
            ('id', exper_id),
            ('message_text', text),
            ('scope', 'experiment'),
            ('num_tags', '1'),
            ('tag_name_0',blinepython),
            ('tag_value_0',tag),
            MultipartParam.from_file("file1", file ),
            ("file1", file_descr), 
            MultipartParam.from_file("file2", file2 ),
            ("file2", file_descr2) )
        else:
          data = (
            ('author_account', logbook_author),
            ('id', exper_id),
            ('message_text', text),
            ('scope', 'experiment'),
            ('num_tags', '1'),
            ('tag_name_0',blinepython),
            ('tag_value_0',tag),
            MultipartParam.from_file("file1", file ),
            ("file1", file_descr), 
            MultipartParam.from_file("file2", file2 ),
            ("file2", file_descr2),
            MultipartParam.from_file("file3", file3 ),
            ("file3", file_descr3) )

        datagen,headers = multipart_encode(data)

        try:
            req = urllib2.Request(url, datagen, headers)
            response = urllib2.urlopen(req)
            the_page = response.read()
            result = simplejson.loads(the_page)
            if result['status'] != 'success':
                tkMessageBox.showerror ( "Error", result['message'])
            new_message_id = int(result['message_id'])


        except urllib2.URLError, reason:
            tkMessageBox.showerror (
                "Submit New Message Error",
                reason )
        except urllib2.HTTPError, code:
            tkMessageBox.showerror (
                "Submit New Message Error",
                code )

# ------------------------------------------------------
# Configure an authentication context of the web service
# ------------------------------------------------------

def ws_configure_auth():

    try:

        # First, register openers required by multi-part poster
        #
        opener = register_openers()

        # Then configure and add a handler for Apache Basic Authentication
        #
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, ws_url, ws_login_user, ws_login_password)

        opener.add_handler(urllib2.HTTPBasicAuthHandler(password_mgr))

    except urllib2.URLError, reason:
        print "ERROR: failed to set up Web Service authentication context due to: ", reason
        sys.exit(1)
    except urllib2.HTTPError, code:
        print "ERROR: failed to set up Web Service authentication context due to: ", code
        sys.exit(1)

# ------------------------------------------------------

def ws_get_experiments (experiment=None):

    # Try both experiments (at instruments) and facilities (at locations)
    #
    urls = [ ws_url+'/LogBook/RequestExperiments.php?instr='+logbook_instrument,
             ws_url+'/LogBook/RequestExperiments.php?instr='+logbook_instrument+'&is_location' ]

    try:

        d = dict()

        for url in urls:

            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            the_page = response.read()
            result = simplejson.loads(the_page)
            if len(result) <= 0:
                print "ERROR: no experiments are registered for instrument: %s" % logbook_instrument

            # if the experiment was explicitly requested in the command line then try to find
            # the one. Otherwise return the whole list
            #
            if experiment is not None:
                for e in result['ResultSet']['Result']:
                    if experiment == e['name']:
                        d[experiment] = e
            else:
                for e in result['ResultSet']['Result']:
                    d[e['name']] = e

        return d

    except urllib2.URLError, reason:
        print "ERROR: failed to get a list of experiment from Web Service due to: ", reason
        sys.exit(1)
    except urllib2.HTTPError, code:
        print "ERROR: failed to get a list of experiment from Web Service due to: ", code
        sys.exit(1)

def ws_get_current_experiment ():

    url = ws_url+'/LogBook/RequestCurrentExperiment.php?instr='+logbook_instrument

    try:
        print 'using new module'
        req      = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()
        result   = simplejson.loads(the_page)
        if len(result) <= 0:
            print "ERROR: no experiments are registered for instrument: %s" % logbook_instrument

        e = result['ResultSet']['Result']
        if e is not None:
            return e['name']

        print "ERROR: no current experiment configured for this instrument"
        sys.exit(1)

    except urllib2.URLError, reason:
        print "ERROR: failed to get the current experiment info from Web Service due to: ", reason
        sys.exit(1)
    except urllib2.HTTPError, code:
        print "ERROR: failed to get the current experiment info from Web Service due to: ", code
        sys.exit(1)

