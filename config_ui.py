import mc, neighbourhood as nb

from connect import *
from traceback import print_exc
from common import AuthenticationFailure
from main_ui import forced_config
CONFIG_WINDOW = mc.GetWindow(14003)
VERSION = "Loaded v0.9"

def addstatus(lbl):
    list = CONFIG_WINDOW.GetList(700)
    items = list.GetItems()
    items[-1].SetLabel(items[-1].GetLabel() + " " + lbl)
    list.SetItems(items)
    print "STATUS: %s" % items[-1].GetLabel()

def status(lbl):
    global CONFIG_WINDOW
    item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item.SetLabel(lbl)
    append_list(CONFIG_WINDOW.GetList(700), item, True)
    print "STATUS: %s" % lbl

def append_list(list, item, focusLast = False):
    items = list.GetItems()
    focus = list.GetFocusedItem()
    items.append(item)
    list.SetItems(items)
    if focus and not focusLast:
        list.SetFocusedItem(focus)
    else:
        list.SetFocusedItem(len(items)-1)

def refresh_list(list):
    items = list.GetItems()
    list.SetItems(items)

def load_ui():
    global params, APP, CONFIG_WINDOW
    # Initialize LOG
    items = mc.ListItems()
    item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item.SetLabel(VERSION)
    items.append(item)
    CONFIG_WINDOW.GetList(700).SetItems(items)
    params = APP.GetLaunchedWindowParameters()
    CONFIG_WINDOW.GetEdit(9001).SetText(params['client_address'])
    CONFIG_WINDOW.GetEdit(9002).SetText(params['client_user'])
    CONFIG_WINDOW.GetEdit(9003).SetText(params['client_pass'])
    CONFIG_WINDOW.GetControl(7000).SetVisible(True)
    CONFIG_WINDOW.GetControl(3000).SetVisible(False)

    items = mc.ListItems()
    if params['client_name']:
        auth = params['client_user'] != ''
        item = create_client_item(params['client_name'], params['client_address'], auth)
        item.SetProperty('username', params['client_user'])
        item.SetProperty('password', params['client_pass'])
        items.append(item)
    else:
        item = create_client_item('Unknown', 'localhost', False)
        items.append(item)
    CONFIG_WINDOW.GetList(200).SetItems(items)

def auto_scan():
    global CONFIG_WINDOW, TORRENT_CLIENTS, CONFIG, params
    CONFIG = mc.GetApp().GetLocalConfig()
    CONFIG_WINDOW.GetControl(9007).SetVisible(True)
    status("Scanning neighbourhood...")
    ip = nb.get_ip_address()
    addresses = nb.get_active_neighbourhood(ip, 10, 0.1)
    addstatus(' found %s devices' % len(addresses))
    addresses.append('localhost')
    clients = CONFIG_WINDOW.GetList(200)
    for address in addresses:
        status('Scanning %s' % address)
        for name, client in TORRENT_CLIENTS.items():
            print "Name: %s Client: %s" % (name, client)
            status(' - ' + name)
            connection = None
            try:
                connection = get_connection(client, address)
                append_list(clients, create_client_item(name, connection.get_url(), False))
            except AuthenticationFailure, e:
                addstatus("[AUTH]")
                append_list(clients, create_client_item(name, address, True))
            except Exception, e:
                print_exc()
    status("Done")

    CONFIG_WINDOW.GetControl(9007).SetVisible(False)

def do_connect():
    CONFIG_WINDOW.GetControl(9008).SetVisible(True)
    address = CONFIG_WINDOW.GetEdit(9001).GetText()
    usr = CONFIG_WINDOW.GetEdit(9002).GetText()
    pw = CONFIG_WINDOW.GetEdit(9003).GetText()
    for name, client in TORRENT_CLIENTS.items():
        status("Checking %s" % (name))
        connection = None
        try:
            connection = get_connection(client, url=address, username=usr, password=pw)
        except Exception, e:
            addstatus("ERROR: %s" % e)
            raise

        if connection:
            addstatus("SUCCESS")
            print "Created connection to %s successfully." % name
            CONFIG.SetValue('client_name', name)
            CONFIG.SetValue('client_address', address)
            CONFIG.SetValue('client_user', usr)
            CONFIG.SetValue('client_pass', pw)
            WINDOW.PopState()
            mc.CloseWindow()
            get_ui(client, connection)
            break
    CONFIG_WINDOW.GetControl(9008).SetVisible(False)
    #if not connection:
    #    mc.ShowDialogOk("Connection failed", "Could not connect to any torrent clients with the provided information.")

def close_ui():
    mc.CloseWindow()
    WINDOW.PopState()
    if forced_config:
        mc.CloseWindow()
        WINDOW.PopState()

def select_client():
    global CONFIG_WINDOW
    clients = CONFIG_WINDOW.GetList(200)
    item = clients.GetItem(clients.GetFocusedItem())
    if item:
        address = CONFIG_WINDOW.GetEdit(9001)
        usr = CONFIG_WINDOW.GetEdit(9002)
        pw = CONFIG_WINDOW.GetEdit(9003)
        address.SetText(item.GetLabel())
        usr.SetText(item.GetProperty('username'))
        pw.SetText(item.GetProperty('password'))

def create_client_item(name, url, auth=False):
    item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item.SetLabel(url)
    item.SetProperty('type', name)
    item.SetProperty('auth', '%s' % auth)
    return item
