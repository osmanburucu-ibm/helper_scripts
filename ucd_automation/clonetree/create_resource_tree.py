# TODO: A LOT OF DUPLICATION at the moment, next iteration put all reusable methods/functions and so on into a module/class/package?? whatever it is in python

import json
import requests
import urllib3
import yaml
from datetime import datetime
import logging

logging.basicConfig(format='%(asctime)s | %(levelname)s | %(funcName)s: %(message)s', level=logging.INFO)

# suppress warnings of not checking certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parameters = {}

from requests.auth import HTTPBasicAuth

def read_configuration(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def create_resource(res, parent):
    # TODO: a good idea would be to check if this resource exists before creation is executed....
    logging.info ("parent:"+parent)

    parameters=read_configuration("parameters.yml")
    headers = {'Content-Type': 'application/json',}
    ucd_url="https://"+ parameters["target"]["hostname"] + ":"  + str(parameters["target"]["https_port"]) + "/cli/resource/create"
    logging.info(ucd_url)

    # set working variables
    payload = {}
    fieldnames=["name","description"]
    defaultValues={"description":"", "tags":[]}

    for name in fieldnames:
        payload[str(name)] = res.get(str(name), defaultValues.get(str(name),""))

    if (parent and not parent.isspace()):
        payload["parent"]=parent

    if (res.get("type") == "agent"):
        payload["agent"] = res.get(str("name"))
    if (res.get("type") == "agentPool"):
        payload["agentPool"] = res.get(str("name"))

    if (res.get("type") == "COMPONENT"):
        payload["component"] = res.get(str("name"))
    if (res.get("type") == "ComponentTag"):
        payload["componentTag"] = res.get(str("name"))
    
    
    logging.info(payload)

    auth_user=parameters["target"]["user"]
    auth_pwd=parameters["target"]["token"]

    r = requests.put(ucd_url, data=json.dumps(payload), auth=HTTPBasicAuth(auth_user, auth_pwd),headers=headers, verify=False)
    logging.info(r.text)

    # now iterate over children
    for child in res["children"]:
        create_resource(child, res["path"])
#    logging.info(json.dumps(r.json(), indent=2))

def main():

    with open ("ResourceTree.json") as inputfile:
        input_tree = json.load(inputfile)

        for tlr in input_tree["resources"]:
            create_resource(tlr, "")

if __name__ == '__main__':
    main()