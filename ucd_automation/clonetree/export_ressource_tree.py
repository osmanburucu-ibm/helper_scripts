import json
import requests
import urllib3
import yaml
from datetime import datetime
import logging

logging.basicConfig(format='%(asctime)s | %(levelname)s | %(funcName)s: %(message)s', level=logging.WARNING)

# suppress warnings of not checking certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parameters = {}

from requests.auth import HTTPBasicAuth

def read_configuration(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def get_ressource_type(path):
    parameters=read_configuration("parameters.yml")
    specialType = "subresource"

    headers = {'Content-Type': 'application/json',}
    ucd_url="https://"+ parameters["source"]["hostname"] + ":"  + str(parameters["source"]["https_port"]) + "/cli/resource/info"

    if (path and not path.isspace()):
        ucd_url= ucd_url +"?resource="+path.replace("\/","/")

    auth_user=parameters["source"]["user"]
    auth_pwd=parameters["source"]["token"]

    r = requests.get(ucd_url, auth=HTTPBasicAuth(auth_user, auth_pwd), verify=False)
    logging.info (json.dumps(r.json(), indent=2))

    res=r.json()
    if "role" in res:
        role = res.get("role")
        specialType=role.get("specialType", "subresource")
    logging.info(specialType)
    return specialType


def get_ressource(parent):

    parameters=read_configuration("parameters.yml")

    headers = {'Content-Type': 'application/json',}
    ucd_url="https://"+ parameters["source"]["hostname"] + ":"  + str(parameters["source"]["https_port"]) + "/cli/resource"

    if (parent and not parent.isspace()):
        ucd_url= ucd_url +"?parent="+parent.replace("\/","/")

    auth_user=parameters["source"]["user"]
    auth_pwd=parameters["source"]["token"]

    r = requests.get(ucd_url, auth=HTTPBasicAuth(auth_user, auth_pwd), verify=False)
    logging.info(json.dumps(r.json(), indent=2))

    allResources=[]
    fieldnames=("name","path","type","tags")
    defaultValues={"type":"resource", "tags":[]}

    for res in r.json():
        childresources=[]
        if res["active"]:
            actResource={}
            for name in fieldnames:
                actResource[str(name)] = res.get(str(name), defaultValues.get(str(name),""))
            # check info when type = subresource and hasAgent = true
            if (res.get("hasAgent", "false") and res.get("type") == "subresource"):
                specialType=get_ressource_type(res.get("path"))
                actResource["type"]=specialType
            childresources=get_ressource(actResource["path"])
            actResource["children"]=childresources
            allResources.append(actResource)

    return allResources


def main():
    parameters=read_configuration("parameters.yml")
    myTree = {"source":str(parameters["source"]["hostname"]), "date":str(datetime.now())}

    tlrResources=get_ressource("")
    myTree["resources"]=tlrResources
    logging.info(json.dumps(myTree))
    with open ("ResourceTree.json","w") as outputfile:
        json.dump(myTree, outputfile, indent=2)

if __name__ == '__main__':
    main()