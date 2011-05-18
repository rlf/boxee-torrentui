#!/usr/bin/env python
if __name__ == '__main__':
    import urlparse
    url = 'http://192.168.40.101/transmission/rpc'
    scheme, loc, path, query, arg = urlparse.urlsplit(url)
    print "URL     : %s" % url
    print "Scheme  : %s" % scheme
    print "Location: %s" % loc
    print "Path    : %s" % path
    print "Query   : %s" % query
    print "Arg     : %s" % arg
