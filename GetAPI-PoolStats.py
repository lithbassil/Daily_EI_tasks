import requests
from requests.auth import HTTPBasicAuth
from netmiko import Netmiko
import json
import time
from datetime import datetime

TeamsUrl = 'TEAMS WEBHOOK URL'

pre_date = datetime.now()
dt_now = pre_date.strftime("%d/%m/%Y %H:%M:%S")


def TeamsMSG(val):
    msg = {
        'title': 'CUC Job',
        'text': val
    }
    val = 'ACTION OUTPUT'
    # print(json.dumps(msg, indent=2))
    msg_body = requests.post(url=TeamsUrl, data=json.dumps(msg))


def ConnectSSH(ip, cmd):
    net_connect = Netmiko(ip, username="admin", password="password", device_type="cisco_ios")
    output = net_connect.send_command(cmd)
    return output

qui11 = '100.100.100.1'
qui12 = '100.100.100.2'
cmdQ11UP = 'utils network ping'
cmdQ11Restart = 'utils system restart'
cmdMakePri = 'utils cuc cluster makeprimary'
cmdQ12ResTomcat = 'utils service restart Cisco Tomcat'

username = 'admin'
password = 'password'
headers = {'Content-Type': 'application/json'}
url = 'https://100.100.100.3/mgmt/tm/ltm/pool/~Common~VM_TEST/members/~Common~qui11:443/stats'
try:

    req = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password), verify=False)
    req = req.json()
    monitorStatus = \
        req['entries']['https://localhost/mgmt/tm/ltm/pool/~Common~VM_TEST/members/~Common~qui11:443/stats'][
            'nestedStats'][
            'entries']['monitorStatus']['description']
    status_code = req.status_code

    if monitorStatus == 'up':
        print('UP')
    else:
        print('Make QUI12 primary & Restart QUI11 ')
        output = ConnectSSH(qui12, cmdMakePri)
        print(output)
        time.sleep(10)
        output = ConnectSSH(qui11, cmdQ11Restart)
        print(output)
        TeamsMSG(output)
        time.sleep(300)
        try:
            output = ConnectSSH(quiver11, cmdQ11UP)
            if output == 'PING':
                ConnectSSH(qui11, cmdMakePri)
                ConnectSSH(qui11, cmdQ12ResTomcat)
                TeamsMSG(output)
        finally:
            pass
except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)
except requests.exceptions.ConnectionError as errc:
    print("Error Connecting:", errc)
except requests.exceptions.Timeout as errt:
    print("Timeout Error:", errt)
except requests.exceptions.RequestException as err:
    print("OOps: Something Else", err)