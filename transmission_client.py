#!/usr/bin/env python
try:
    import simplejson as json
except ImportError:
    import json
import sys

import socket
socket.setdefaulttimeout(30)
import urllib2
import base64
from urlparse import urlsplit, urlunsplit
from common import AuthenticationFailure

class TransmissionClientFailure(Exception): pass

class TransmissionClient(object):
    rpcUrl = None
    headers = {}

    def __init__( self, rpcUrl='http://localhost:9091', username=None, password=None):
        """ try to do a stupid call to transmission via rpc """

        self.username = username
        self.password = password
        if username:
            usrpw = "%s:%s" % (username, password)
            b64encoded = base64.b64encode(usrpw)
            self.headers['Authorization'] = 'Basic ' + b64encoded
        try:
            self.rpcUrl = rpcUrl
            if not self.rpcUrl.endswith("/transmission/rpc"):
                self.rpcUrl = '%s/transmission/rpc' % rpcUrl 
            if not self.rpcUrl.startswith('http:'):
                self.rpcUrl = 'http://%s' % self.rpcUrl
            scheme, nwloc, path, query, fragment = urlsplit(self.rpcUrl)
            if nwloc.find(':') == -1:
                nwloc += ':9091'
                self.rpcUrl = urlunsplit((scheme, nwloc, path, query, fragment))
            print "Trying: %s" % self.rpcUrl
            req = urllib2.Request( self.rpcUrl , {}, self.headers)
            response = urllib2.urlopen(req)
            response = response.read()
            if not response.find("no method name"):
                raise TransmissionClientFailure, "Make sure your transmission-daemon is running %s" % e             
                
        except urllib2.HTTPError, e:
            if e.code == 409:
                self.headers['X-Transmission-Session-Id'] = e.info()['X-Transmission-Session-Id']
                req = urllib2.Request( self.rpcUrl , {}, self.headers)
                response = urllib2.urlopen(req)
                response = response.read()
            elif e.code == 401:
                raise AuthenticationFailure, "The transmission-daemon is running, but requires authentication!"
            else:
                raise Exception('HTTPError: %s' % e.code )
        except Exception, e:
            raise TransmissionClientFailure, "Make sure your transmission-daemon is running %s" % e


    def get_url(self):
        return self.rpcUrl

    def _rpc( self, method, params={} ):
        """ generic rpc call to transmission """
        
        try:
            params['ids'] = int(params['ids'])
        except:
            pass

        data = { 'method': method, 'arguments': params}
        postdata = json.dumps(data)
        try:
            req = urllib2.Request( self.rpcUrl , postdata, self.headers)
            response = urllib2.urlopen(req)
            return json.loads(response.read())
        except urllib2.HTTPError, e:
            if e.code == 409:
                self.headers['X-Transmission-Session-Id'] = e.info()['X-Transmission-Session-Id']
                return self._rpc(method, params)
            elif e.code == 401:
                raise AuthenticationFailure, "The transmission-daemon is running, but requires authentication!"
            else:
                raise Exception('HTTPError: %s' % e.code )
            
            
    def sessionStats( self ):
        return self._rpc( 'session-stats' )
    

    def torrentGet( self, torrentIds=[], fields=[ 'id', 'name', 'totalSize', 'percentDone', 'rateDownload', 'rateUpload', 'files', 'status', 'peersConnected', 'peersSendingToUs', 'peersGettingFromUs', 'eta', 'uploadedEver', 'uploadRatio']):
        if len(torrentIds) > 0:
            return self._rpc( 'torrent-get', { 'ids': torrentIds, 'fields': fields } ) 
        return self._rpc( 'torrent-get', { 'fields': fields } )


    def torrentAdd( self, torrentFile, downloadDir='.' ):
        return self._rpc( 'torrent-add', { 'filename': torrentFile, 'download-dir': downloadDir } )


    def torrentRemove( self, torrents=None, files=False ):
        if files:
            if torrents:
                return self._rpc( 'torrent-remove', { 'ids': torrents, 'delete-local-data': 'true' } )
            else:
                return self._rpc( 'torrent-remove', { 'delete-local-data': 'true' } )
        if torrents:
            return self._rpc( 'torrent-remove', { 'ids': torrents } )
        else:
            return self._rpc( 'torrent-remove', { } ) 
    
    
    def torrentStart( self, torrents=None ):
        if torrents:
            return self._rpc( 'torrent-start', { 'ids': torrents } )
        else:
            return self._rpc( 'torrent-start', {} )
        
        
    def torrentStop( self, torrents=None ):
        if torrents:
            return self._rpc( 'torrent-stop', { 'ids': torrents } )
        else:
            return self._rpc( 'torrent-stop', {} )
