# Module containing common classes for use accross torrent-clients

class AuthenticationFailure(Exception):
    """ Exception used to indicate a torrent-service was found, but it
        requires authentication.
    """
    pass
