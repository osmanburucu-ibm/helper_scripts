import json
import time

import requests
import urllib3
# suppress warnings of not checking certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from requests.auth import HTTPBasicAuth

def upgrade_agents():
    headers = {'Content-Type': 'application/json',}
    ucd_url='https://192.168.62.197:8443/cli/agentCLI'
    auth_user='PasswordIsAuthToken'
    auth_pwd='aa1f17e1-404d-4dc7-b452-fda8503e382b'
    r = requests.get(ucd_url, auth=HTTPBasicAuth(auth_user, auth_pwd), verify=False)
    # now work with json
    print (json.dumps(r.json(), indent=2))

    for x in r.json():
        agentname = x["name"]
        if 'tags' in x:
            for t in x["tags"]:
                if t["name"] == 'upgrade':
                    print("upgrading {}".format(agentname))
                    u = requests.put(ucd_url + '/upgrade', params={'agent': agentname},
                                     auth=HTTPBasicAuth(auth_user, auth_pwd),
                                     verify=False)
                    print("Status Code of upgrade request: {}".format(u.status_code))
                    time.sleep(30)
                    params = (('agent',agentname),('tag','upgrade'),)
                    d = requests.delete(ucd_url + "/tag/", params=params,
                                         auth=HTTPBasicAuth(auth_user, auth_pwd), headers=headers,
                                        verify=False)
                    print("Status Code of remove tag request: {}".format(d.status_code))

if __name__ == '__main__':
    while upgrade_agents():
        print()