import mc

from connect import APP, CONFIG, WINDOW, TORRENT_CLIENTS, TORRENT_LIST, get_connection, get_ui
CONFIG_WINDOW = mc.GetWindow(14003)
STATUS = WINDOW.GetLabel(105)
connection = None
client_ui = None
forced_config = False

def load_ui():
    global connection, client_ui
    STATUS.SetLabel("Checking for saved connections...")

    params = mc.Parameters()
    params['client_name'] = CONFIG.GetValue('client_name')
    params['client_address'] = CONFIG.GetValue('client_address')
    params['client_user'] = CONFIG.GetValue('client_user')
    params['client_pass'] = CONFIG.GetValue('client_pass')

    client = params['client_name']
    print "OnLoad connection to %s with url %s" % (params['client_name'], params['client_address']) 
    if client:
        STATUS.SetLabel("Connecting to %s" % client)
        client = TORRENT_CLIENTS[params['client_name']]
        try:
            connection = get_connection(client, url=params['client_address'], 
                                            username=params['client_user'], 
                                            password=params['client_pass'])
        except Exception, e:
            print "ERR: %s" % e
            connection = None # Revert to config screen

        if not connection:
            STATUS.SetLabel("Connection failed, launching configuration.")
            show_config(True)
        else:
            print "Got connection"
            STATUS.SetVisible(False)
            try:
                client_ui = get_ui(client, connection)
            except Exception, e:
                print "ERR: %s" % e
                client_ui = None
            if not client_ui:
                show_config(True)

    else:
        STATUS.SetLabel("No client found, launching configuration.")
        WINDOW.PushState()
        APP.ActivateWindow(14003, params)    

def init():
    """ Initializes the TORRENT_LIST and WINDOW variables
    """
    global WINDOW, TORRENT_LIST, client_ui, connection
    if not WINDOW:
        WINDOW = mc.GetWindow(14002)
    if not TORRENT_LIST:
        TORRENT_LIST = WINDOW.GetList(100)

def show_options():
    init()
    listitem = TORRENT_LIST.GetItem(TORRENT_LIST.GetFocusedItem())
    WINDOW.PushState()
    option = None
    if listitem.GetProperty("transfer_status") == 'Paused':
        option = 4001
    elif listitem.GetProperty("transfer_status") in ['Downloading', 'Seeding']:
        option = 4002
    if option:
        WINDOW.GetControl(option).SetVisible(True)
        WINDOW.GetControl(option).SetFocus()
    WINDOW.GetLabel(4007).SetLabel(listitem.GetLabel())
    WINDOW.GetControl(4000).SetVisible(True)

def do_start():
    init()
    pk = TORRENT_LIST.GetFocusedItem()
    WINDOW.PopState()
    TORRENT_LIST.SetFocusedItem(pk)
    listitem = TORRENT_LIST.GetItem(pk)
    client_ui.start_torrent(listitem.GetProperty('id'))
    
def do_delete():
    init()
    pk = TORRENT_LIST.GetFocusedItem()
    WINDOW.PopState()
    TORRENT_LIST.SetFocusedItem(pk)
    listitem = TORRENT_LIST.GetItem(pk)
    client_ui.delete_torrent(listitem.GetProperty('id'))

def do_stop():
    init()
    pk = TORRENT_LIST.GetFocusedItem()
    WINDOW.PopState()
    TORRENT_LIST.SetFocusedItem(pk)
    listitem = TORRENT_LIST.GetItem(pk)
    client_ui.stop_torrent(listitem.GetProperty('id'))

def show_config(forced=False):
    global forced_config
    init()
    forced_config = forced
    WINDOW.PushState()
    WINDOW.GetControl(3000).SetVisible(True)
    params = mc.Parameters()
    params['client_name'] = CONFIG.GetValue('client_name')
    params['client_address'] = CONFIG.GetValue('client_address')
    params['client_user'] = CONFIG.GetValue('client_user')
    params['client_pass'] = CONFIG.GetValue('client_pass')
    APP.ActivateWindow(14003, params)
    WINDOW.GetControl(3000).SetVisible(False)

def busy(func):
    WINDOW.GetControl(100).SetVisible(False)
    WINDOW.GetControl(3000).SetVisible(True)
    try:
        func()
    finally:
        WINDOW.GetControl(3000).SetVisible(False)
        WINDOW.GetControl(100).SetVisible(True)
