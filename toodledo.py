import json
import md5
import pickle
from ConfigParser import SafeConfigParser
from pprint import pprint

import requests

config = SafeConfigParser()
config.read(["dailyform.cfg"])

appid = config.get('toodledo', 'id')
apptoken = config.get('toodledo', 'token')
userpw = config.get('toodledo', 'password')
email = config.get('toodledo', 'username')

session = {"appid": appid}


def make_sig(keyvalue):
    return md5.md5(keyvalue + apptoken).hexdigest()


def auth_request(url, *otherfields, **kwfields):
    params = dict(session)
    params.update(kwfields)
    params.update(dict(otherfields))
    params['sig'] = make_sig(params['userid']) if 'userid' in params else make_sig(params['email'])
    return requests.get(url, params=params)


session.update(
    json.loads(auth_request("http://api.toodledo.com/2/account/lookup.php", ("email", email), ("pass", userpw)).text))
session.update(json.loads(auth_request("http://api.toodledo.com/2/account/token.php", **session).text))
print session

pickle.dump(session, open("session.pkl", "w"))

key = md5.md5(md5.md5(userpw).hexdigest() + apptoken + session['token']).hexdigest()
session = {'key': key}


def request(url, *fields, **kwfields):
    params = dict(session)
    params.update(kwfields)
    params.update(dict(fields))
    return requests.get(url, params=params)


def get_todos():
    response = json.loads(request("http://api.toodledo.com/2/tasks/get.php").text)
    return response


pprint(json.loads(request("http://api.toodledo.com/2/tasks/get.php").text))
