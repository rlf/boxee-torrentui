import mc

from transmission_client import TransmissionClient
from rtorrent_client import RTorrentXMLRPCClient
from utorrent_client import uTorrent
from torrent_ui import rTorrentUI, uTorrentUI, TransmissionUI, TorrentUI

APP = mc.GetApp()
CONFIG = mc.GetApp().GetLocalConfig()
WINDOW = mc.GetWindow(14002)
TORRENT_CLIENTS={
    "Transmission": TransmissionClient,
    'RTorrent': RTorrentXMLRPCClient,
    'uTorrent': uTorrent,
}
TORRENT_LIST=WINDOW.GetList(100)

UI = {
    TransmissionClient: TransmissionUI,
    uTorrent: uTorrentUI,
    RTorrentXMLRPCClient: rTorrentUI
}


def create_connection(client, url=None, username=None, password=None):
    if url is None:
        conn = client()
    else:
        conn = client(url)
        
    ui = UI[client](conn)
    #TORRENT_LIST = ui.get_torrents()
    ui.run()
    return ui
