import mc
from transmission_client import TransmissionClient
from rtorrent_client import RTorrentXMLRPCClient
from utorrent_client import uTorrent
from torrent_ui import rTorrentUI, uTorrentUI, TransmissionUI, TorrentUI
from torrent_ui import TransmissionUI, TorrentUI

APP = mc.GetApp()
CONFIG = mc.GetApp().GetLocalConfig()
WINDOW = mc.GetWindow(14002)
TORRENT_CLIENTS={
    'Transmission': TransmissionClient,
    'RTorrent': RTorrentXMLRPCClient,
    'uTorrent': uTorrent,
}
TORRENT_LIST={}

UI = {
    TransmissionClient: TransmissionUI,
    uTorrent: uTorrentUI,
    RTorrentXMLRPCClient: rTorrentUI
}
params = {}

def create_connection(client, url=None, username=None, password=None):
    conn = get_connection(client, url, username, password)
    if conn:
        return get_ui(client, conn)
    return conn

def get_connection(client, url=None, username=None, password=None):
    if url is None:
        conn = client()
    elif username is None:
        conn = client(url)
    else:
        conn = client(url, username, password)

    return conn

def get_ui(client, conn):
    ui = UI[client](conn)
    ui.run()
    return ui
