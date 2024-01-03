import requests
from json import loads, JSONDecodeError
from typing import List, Dict


class APIResponse:    
    def __init__(self, status_code: int, message: str='', data: List[Dict]=None):
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else []


class CognosAPI:
    def __init__(self, base_url, ssl_verify: bool=True, **kwargs):
        self.env = 'dev'
        self._headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'credentials': 'same-origin/include'
        }
        self.base_url = base_url
        self._session = requests.Session()
        self._ssl_verify = ssl_verify

        if not ssl_verify:
            requests.urllib3.disable_warnings()

    def _send(self, method:str, endpoint:str, params:Dict=None, data:Dict=None) -> APIResponse:
        api_url = self.base_url + endpoint

        try:
            response = self._session.request(method=method,
                                             url=api_url,
                                             params=params,
                                             json=data,
                                             headers=self._headers,
                                             verify=self._ssl_verify
                                             )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception('An error occurred: ', e)

        data_out = {}
        if response.content:
            try:
                data_out = loads(response.content)
            except (ValueError, JSONDecodeError):
                data_out = {'data': response.content}
 
        return APIResponse(response.status_code,
                            message=response.reason,
                            data=data_out)

    def get(self, endpoint: str, params: Dict=None) -> APIResponse:
        return self._send(method='GET', endpoint=endpoint, params=params)

    def post(self, endpoint: str, params: Dict=None, data: Dict=None) -> APIResponse:
        return self._send(method='POST', endpoint=endpoint, params=params, data=data)

    def put(self, endpoint: str, params: Dict=None, data: Dict=None) -> APIResponse:
        return self._send(method='PUT', endpoint=endpoint, params=params, data=data)

    def delete(self, endpoint: str, params: Dict=None, data: Dict=None) -> APIResponse:
        return self._send(method='DELETE', endpoint=endpoint, params=params, data=data)

    def login(self, user=None, password=None, namespace=None):
        payload = {
            'parameters': [
                {
                    'name': 'CAMNamespace',
                    'value': namespace
                }, {
                    'name': 'CAMUsername',
                    'value': user
                }, {
                    'name': 'CAMPassword',
                    'value': password
                }
            ]
        }

        response = self.put(endpoint='/session', params=None, data=payload)
        if response.status_code in (200, 201):
            print(response.data)
            self._headers['IBM-BA-Authorization'] = response.data['session_key']
        else:
            self._logger.error('Could not log in into CA as %s %s:%s', (namespace, user, response.message))

    def _traverse_dir(self, content_id: str='', path: str='', out: List[Dict]=[]) -> List[Dict]:
        contents = self.get(endpoint=f'/content/{content_id}/items')
        for content in contents.data['content']:
            if content['type'] == 'folder':
                out = self._traverse_dir(content['id'], f'{path}/{content["defaultName"]}', out)
            elif content['type'] in ['report', 'exploration', 'jupyterNotebook', 'reportView', 'dashboard']:
                out.append({
                    'name': content['defaultName'],
                    'id': content['id'],
                    'path': f"{path}/{content['defaultName']}"
                })
            else:
                pass
        return out

    def get_reports(self, content_id: str='') -> List[Dict]:
        init_folder = self.get(endpoint=f'/content/{content_id}')
        data = self._traverse_dir(content_id, f'?pathRef=.public_folders/{init_folder.data["defaultName"]}/')
        return data

    def _get_groups(self) -> APIResponse:
        ### i0E3B406D53D147BF8C5E724097BAE234 is the SFPUC group ID. All Cognos users and groups are under this group. ###
        groups = self.get(endpoint=f'/groups?parent_id=i0E3B406D53D147BF8C5E724097BAE234')
        return groups.data['groups']

    def _get_roles(self, object_id: str='') -> APIResponse:
        obj_perms = self.get(f'/roles/{object_id}')
        return obj_perms

    def _get_group_members(self) -> Dict:
        group_data = self._get_groups()
        groups = {}

        for group in group_data:
            print('.'*80)
            members = self.get(endpoint=f'/roles/{group["id"]}/members')
            groups[group['searchPath']] = {
                'group_id': group['id'],
                'group_name': group['defaultName'],
                'members': members.data['users']
            }
        return groups

    def get_folder_permissions(self, folder_id: str='') -> List[Dict]:
        print(f'Getting user list, please wait..................................................')
        groups = self._get_group_members()
        perms = self._get_roles(folder_id)
        permissions = [groups[c['securityObject']['searchPath']] for c in perms.data['policies'] if c['securityObject']['searchPath'] != 'CAMID("::System Administrators")']
        return permissions

