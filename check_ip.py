from subprocess import check_output

def ip_lookup(mac_list):
    if type(mac_list) is not list:
        return None
    lines = check_output(['ip', 'n', 'show'])
    lines = lines.decode('utf-8')
    lines = lines.split('\n')
    ip = [None] * len(mac_list)
    for line in lines:
        for i in range(len(mac_list)):
            if mac_list[i] in line:
                tmp = line[0:line.find(' ')]
                if os.system('ping -c 1 ' + tmp) == 0:
                    ip[i] = tmp
    return ip

import settings
print(ip_lookup([settings.arduino.mac, settings.sp2_00.mac]))

