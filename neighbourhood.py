#! /usr/bin/env python
# vim: set fenc=utf8 ts=4 sw=4 et :
import socket, ping, time, os

SIZE = 16
TIMEOUT = 0.1

if os.name != "nt":
    import fcntl, struct
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
                )[20:24])

def get_lan_ip():
    ip = None
    if os.name != "nt":
        interfaces = ["eth0","eth1","eth2","wlan0","wlan1","wifi0","ath0","ath1","ppp0"]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                if not ip.startswith("127."):
                    break
            except IOError:
                pass
    return ip

def get_ip_address():
    try:
        return [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][0]
    except:
        return get_lan_ip()

def get_neighbourhood(ipv4, size=SIZE):
    # Should do this right, but no cross-platform solutions are to be
    # found out there for locating the netmask using python, so this
    # is the "best thing"
    ips = []
    parts = ipv4.split('.')
    num = int(parts[3])
    # positive direction
    offset = 1
    for n in range(0, size/2):
        ipnum = (num + n + offset) % 255
        while ipnum == 0 or ipnum == 1 or ipnum == 255:
            offset += 1
            ipnum = (num + n + offset) % 255
        ips.append("%s.%s.%s.%s" % (parts[0], parts[1], parts[2], ipnum))
    # negative direction
    offset = 1
    for n in range(0, size/2):
        ipnum = (num - n - offset) % 255
        while ipnum == 0 or ipnum == 1 or ipnum == 255 or ipnum == num:
            offset += 1
            ipnum = (num - n - offset) % 255
        ips.append("%s.%s.%s.%s" % (parts[0], parts[1], parts[2], ipnum))
    return ips

def get_active_neighbourhood(ipv4, size=SIZE, timeout=TIMEOUT):
    t1 = time.clock()
    t11 = time.time()
    ips = []
    for ip in get_neighbourhood(ipv4, size):
        # pinging doesn't work on the boxee box, so we just return
        # ALL as being alive... *sigh*
        print "pinging %s" % ip
        try:
            #if ping.ping(ip, timeout):
            if ping.do_one(ip, timeout) != None:
                print " alive"
                ips.append(ip)
            else:
                print " dead"
        except Exception, e:
            if e.message.contains("protocol not found"):
                ips.append(ip) # Boxee Box gives me hell here
    t2 = time.clock()
    t21 = time.time()
    print "Found %s devices in %s seconds (%s clocks)" % (len(ips), t21-t11, t2-t1)
    return ips

if __name__ == '__main__':
    ip = get_ip_address()
    print "IP: %s" % ip
    for ipn in (get_neighbourhood(ip), get_neighbourhood('10.0.0.3')):
        print ipn
        print len(ipn)
    ipn = get_neighbourhood('10.0.0.253', 256)
    assert len(ipn) == 256
    assert not ipn.count('10.0.0.253')
    assert not ipn.count('10.0.0.0')
    assert not ipn.count('10.0.0.1')
    assert not ipn.count('10.0.0.255')
    print get_active_neighbourhood(ip, 16)
