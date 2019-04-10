#!/usr/bin/env python2
  
from __future__ import print_function
import os
import time
import argparse
import sys
import requests
from urllib import urlencode
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Exit codes
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3


helpstring = '''
Simple check to check solr answer times and collections.
Critical if no matches
warning or critical if timelimit exceeded

"url" is the url used

json output is expected "wt=json" needed in url

example url: /solr/collection/select?start=0&rows=1&wt=json&q.alt=*:*

example usage
-H 'solrhost001.tld.com' -u '/solr/collection/select?start=0&rows=1&wt=json&q.alt=*:*' -w 500 -c 1000 
'''

def help():
    print(helpstring)

def parse_args():
    parser = argparse.ArgumentParser(description='Checks and warns too slow solr answers / critical if none')
    parser.add_argument('-w' '--warn', dest='warn', help='warn threshold milliseconds', required=True, type=int)
    parser.add_argument('-c' '--crit', dest='crit', help='crit threshold milliseconds', required=True, type=int)
    parser.add_argument('-H' '--host', dest='host', help='host', required=True)
    parser.add_argument('-p' '--port', dest='port', help='port', default="80", type=str)
    parser.add_argument('-u' '--url', dest='url', help='url where to search', required=True)
    args = parser.parse_args()
    return args


def exit_ok(message=None):
    if message:
        print(message)
    else:
        print('Ok!')
    sys.exit(STATE_OK)

def exit_warning(message):
    print(message)
    sys.exit(STATE_WARNING)

def exit_critical(message):
    print(message)
    sys.exit(STATE_CRITICAL)

def check(args):
    starttime = int(round(time.time() * 1000))
    url = 'http://%s:%s%s' % (args.host, args.port, args.url)
    try:
        r = requests.get(url, verify=False)
    except Exception, e:
        exit_critical('Failed to get data from solr: %s' % e)
    endtime = int(round(time.time() * 1000))
    # Test status code
    if r.status_code > 299 or r.status_code < 200:
        exit_critical('Failed to get data from solr: %s:%s' % (r.status_code, r._content))

    data = r.json()

    # no response = critical
    if not 'response' in data:
        exit_critical("Search failed! Error in response:%s" % response)
    
    # no searches matched = critical
    if data['response']['numFound'] < 1:
        exit_critical("Search failed! Zero matches:%s" % response)
    
    # Test time thresholds
    timediff = endtime - starttime

    # Critical
    if timediff > args.crit:
        exit_critical('Search took too long:%s > %s; Response: %s| searchtime=%1.2f;%1.2f;%1.2f;0;' % (timediff, data['response'], args.warn, timediff, args.warn, args.crit))

    # Warning
    if timediff > args.warn:
        exit_warning('Search took too long:%s > %s; Response: %s| searchtime=%1.2f;%1.2f;%1.2f;0;' % (timediff, data['response'], args.crit, timediff, args.warn, args.crit))
    
    # Ok
    print('Search ok; Response:%s | searchtime=%1.2f;%1.2f;%1.2f;0;' % (data['response'], timediff, args.warn, args.crit))

def main():
    args = parse_args()
    check(args)

if __name__ == '__main__':
    main()
