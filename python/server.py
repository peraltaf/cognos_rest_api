from flask import Flask, request, jsonify
from configparser import ConfigParser
from json import dumps
import api


app = Flask(__name__)

env = 'dev'
config = ConfigParser(interpolation=None)
config.read('config.ini')
BASE_URL = config.get(env, 'url')
USER = config.get(env, 'user')
NAMESPACE = config.get(env, 'namespace')
PASSWORD = config.get(env, 'password')

ca = api.CognosAPI(BASE_URL, ssl_verify=False)
ca.login(USER, PASSWORD, NAMESPACE)
################### TODO ###################
## Logic to re-login when session expires ##
## Better error handling ###################
############################################

@app.route('/get_reports')
def get_reports():
    folder_id = request.args.get('folder_id')

    if folder_id is None or len(folder_id) == 0:
        return 'You must include a folder_id parameter'
    
    contents = ca.get_reports(folder_id)
    return jsonify(contents)

@app.route('/get_permissions')
def get_permissions():
    object_id = request.args.get('object_id')

    if object_id is None or len(object_id) == 0:
        return 'You must include a object_id parameter'
    
    permissions = ca.get_permissions(object_id)
    return jsonify(permissions)

if __name__ == '__main__':  
   app.run()
