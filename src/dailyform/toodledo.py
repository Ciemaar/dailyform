import hashlib
import json
import pickle
from configparser import ConfigParser
from pprint import pprint

import requests

config = ConfigParser()
config.read(["dailyform.cfg"])

appid = config.get("toodledo", "id")
apptoken = config.get("toodledo", "token")
userpw = config.get("toodledo", "password")
email = config.get("toodledo", "username")

session = {"appid": appid}


def make_sig(keyvalue):
    # MD5 is required by Toodledo API v2 for authentication signatures
    return hashlib.md5((keyvalue + apptoken).encode("utf-8"), usedforsecurity=False).hexdigest()


def auth_request(url, *otherfields, **kwfields):
    params = dict(session)
    params.update(kwfields)
    params.update(dict(otherfields))
    params["sig"] = make_sig(params["userid"]) if "userid" in params else make_sig(params["email"])
    return requests.get(url, params=params)


session.update(
    json.loads(auth_request("http://api.toodledo.com/2/account/lookup.php", ("email", email), ("pass", userpw)).text)
)
session.update(json.loads(auth_request("http://api.toodledo.com/2/account/token.php", **session).text))
print(session)

pickle.dump(session, open("session.pkl", "wb"))

# MD5 is required by Toodledo API v2 for authentication key generation
key = hashlib.md5(
    (hashlib.md5(userpw.encode("utf-8"), usedforsecurity=False).hexdigest() + apptoken + session["token"]).encode(
        "utf-8"
    ),
    usedforsecurity=False,
).hexdigest()
session = {"key": key}


def request(url, *fields, **kwfields):
    params = dict(session)
    params.update(kwfields)
    params.update(dict(fields))
    return requests.get(url, params=params)


def get_todos():
    response = json.loads(request("http://api.toodledo.com/2/tasks/get.php").text)
    return response


pprint(json.loads(request("http://api.toodledo.com/2/tasks/get.php").text))
