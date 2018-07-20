import requests
import json
import urllib3
import sys
from time import sleep

urllib3.disable_warnings()

if len(sys.argv) == 1:
    bigiqUsername = "admin"
    bigiqPassword = "admin"
    bigiqIp = "192.168.142.50"
    bigipIp = "192.168.142.19"
    bigipMac = "00:0c:29:57:4e:21"
    poolName = "pool_BT_1G"
elif len(sys.argv) !=7:
    print ("Requiered arguments: bigiqUsername bigiqPassword bigiqIp bigipIp bigipMac poolName or Nothing")
    #python.exe revoke_license.py admin admin 192.168.142.50 192.168.142.19 00:0c:29:57:4e:21 pool_BT_1G
    sys.exit()
else:
    bigiqUsername = sys.argv[1]
    bigiqPassword = sys.argv[2]
    bigiqIp = sys.argv[3]
    bigipIp = sys.argv[4]
    bigipMac = sys.argv[5]
    poolName = sys.argv[6]

def getBigiqToken (username, password, ip ):

    url = "https://"+ip+"/mgmt/shared/authn/login"

    payload = "{\n    \"username\":\""+username+"\",\n    \"password\":\""+password+"\",\n    \"loginProvidername\":\"tmos\"\n}"
    headers = {
        'Cache-Control': "no-cache"
        }
    response = requests.request("POST", url, data=payload, headers=headers, verify=False)    #print(payload)
    #print(response.status_code)
    if response.status_code == 200:
        bigiqtoken= response.json()['token']['token']
        #print(bigiqToken)
        return bigiqtoken
    else:
        print("GET TOKEN:", response.status_code)
        return("")

def revokeLicense (bigiqip, bigipip, mac, poolname, token ):

    url = "https://"+bigiqip+"/mgmt/cm/device/tasks/licensing/pool/member-management"

    payload = "{\r\n  \"licensePoolName\": \""+poolname+"\",\r\n  \"command\": \"revoke\",\r\n  \"address\": \""+bigipip+"\",\r\n  \"assignmentType\": \"UNREACHABLE\",\r\n  \"macAddress\": \""+mac+"\"\r\n}"
    headers = {
        'x-f5-auth-token': token
        }

    response = requests.request("POST", url, data=payload, headers=headers, verify=False)
    if response.status_code == 202:
        revokeid = response.json()['id']
        return(revokeid)
    else:
        print("REVOKE LICENSE:", response.status_code)
        return("")

def getrevokeStatus(ip,id,token):
    url = "https://"+ip+"/mgmt/cm/device/tasks/licensing/pool/member-management/"+id

    headers = {
        'x-f5-auth-token': token
        }

    response = requests.request("GET", url, headers=headers, verify=False)
    #print(url)
    #print("STATUS CODE" , response.status_code)
    if response.json()['status'] == "FINISHED":
        return("FINISHED")
    elif response.json()['status'] == "FAILED":
        return("FAILED: "+response.json()['errorMessage'])
    else: return("IN_PROGRESS")

bigiqToken = getBigiqToken(bigiqUsername, bigiqPassword, bigiqIp)

revoketaskId = revokeLicense(bigiqIp, bigipIp, bigipMac, poolName, bigiqToken)

revokeStatus = "IN_PROGRESS"
while revokeStatus=="IN_PROGRESS":
 revokeStatus=getrevokeStatus(bigiqIp, revoketaskId, bigiqToken )
 print(revokeStatus)
 sleep(1)
