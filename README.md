# check_solr_search
Simple icinga/nagios check for testing solr search
Simple check to check solr answer times and collections.
Critical if no matches
warning or critical if timelimit exceeded

"url" is the url used

json output is expected "wt=json" needed in url

example url: /solr/collection/select?start=0&rows=1&wt=json&q.alt=*:*

example usage
-H 'solrhost001.tld.com' -u '/solr/collection/select?start=0&rows=1&wt=json&q.alt=*:*' -w 500 -c 1000 Simple check to check solr 
