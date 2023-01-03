import requests
from requests.auth import HTTPBasicAuth
from netmiko import Netmiko
import json
import time
from datetime import datetime



pre_date = datetime.now()
dt_now = pre_date.strftime("%d/%m/%Y %H:%M:%S")

# Notification bu MS Teams webhook
TeamsUrl = 'TEAMS WEBHOOK URL'
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


publisher = '100.100.100.1'
subscriber = '100.100.100.2'
nodeStatus = 'utils network ping'
restartNode = 'utils system restart'
makePrimary = 'utils cuc cluster makeprimary'
restartTomcat = 'utils service restart Cisco Tomcat'

username = 'admin'
password = 'password'
headers = {'Content-Type': 'application/json'}

# The CUC virtual server in F5 load balance stats url
url = 'https://100.100.100.3/mgmt/tm/ltm/pool/~Common~VM_TEST/members/~Common~publisher:443/stats'

try:

    req = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password), verify=False)
    req = req.json()
    monitorStatus = \
        req['entries']['https://localhost/mgmt/tm/ltm/pool/~Common~VM_TEST/members/~Common~publisher:443/stats'][
            'nestedStats'][
            'entries']['monitorStatus']['description']
    status_code = req.status_code

    if monitorStatus == 'up':
        print('UP')
    else:
        print('Make subscriber primary & Restart publisher ')
        output = ConnectSSH(subscriber, makePrimary + subscriber)
        print(output)
        time.sleep(10)
        output = ConnectSSH(publisher, restartNode)
        print(output)
        TeamsMSG(output)
        time.sleep(300)
        try:
            output = ConnectSSH(publisher, nodeStatus)
            if output == 'PING':
                ConnectSSH(publisher, makePrimary + publisher)
                ConnectSSH(subscriber, restartTomcat)
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
