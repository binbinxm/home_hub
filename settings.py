class ip_table(object):
    def __init__(self, desc, mac, ip = ''):
        self.ip = ip
        self.description = desc
        self.mac = mac

arduino = ip_table('arduino as iot hub', '60:01:94:0a:a1:fe', '192.168.0.104')
sp2_00 = ip_table('sp2 for unknown controller', '34:ea:34:b8:79:a0')

