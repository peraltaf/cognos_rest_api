const https = require('https');
require('dotenv').config();


const httpsAgent = new https.Agent({
  rejectUnauthorized: false,
});

class CognosAPI {
  #headers = {
    'Accept': '*/*',
    'Content-Type': 'application/json'
  }

  constructor(base_url, ssl_verify=false) {
    this.base_url = base_url;
    this.ssl_verify = ssl_verify;
  }

  async #send(method, endpoint, data=null) {
    let api_url = this.base_url + endpoint;
    let payload = {
      'method': method,
      'headers': this.#headers,
      'credentials': 'same-origin'
    }
    if (!this.ssl_verify) {
      payload.agent = httpsAgent;
      process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
    }
    if (data) payload.body = JSON.stringify(data);
    try {
      return await fetch(api_url, payload)
      .then(resp => {        
        if ([200,201].includes(resp.status)) {
          return resp.json();
        } else {
          throw resp.status;
        }
      })
      .then(data => data.hasOwnProperty('content') ? data.content : [data])
      .catch(e => this.#throwError(e));
    } catch (e) {
      this.#throwError(e);
    }
  }

  #throwError(e) {
    throw e;
  }

  async #get(endpoint, data=null) {
    return await this.#send('GET', endpoint, data);
  }

  async #put(endpoint, data=none) {
    return await this.#send('PUT', endpoint, data);
  }

  async login(user=null, password=null, namespace=null) {
    let payload = {
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

    try {
      let response = await this.#put('/session', payload);
      this.#headers['IBM-BA-Authorization'] = await response[0].session_key;
    } catch (e) {
      throw `Could not log in into CA as ${user} in namespace ${namespace}.`;
      // this.#throwError(e);
    }
  }


  async #traverseDir(store_id, curr_path='', out=[])  {
    let contents = await this.#get(`/content/${store_id}/items`);
  
    for (let content of contents) {
      if (content.type === 'folder') {
        out = await this.#traverseDir(content.id, `${curr_path}/${content.defaultName}`, out);
      } else if (['report', 'exploration', 'jupyterNotebook', 'reportView', 'dashboard'].includes(content.type)) {
        out = [...out, {
          name: content.defaultName,
          id: content.id,
          path: `${curr_path}/${content.defaultName}`,
        }];
      } else {
        console.log('Unaccounted content type', content);
      }
    }
  
    return out;
  }

  async get_reports(content_id) {
    let init_folder = await this.#get(`/content/${content_id}`);
    let data = await this.#traverseDir(content_id, `?pathRef=.public_folders/${init_folder[0].defaultName}/`);
    return data;
  }

  async #getGroups() {
    /*** i0E3B406D53D147BF8C5E724097BAE234 is the SFPUC group ID. All Cognos users and groups are under this group. ***/
    let groups = await this.#get(`/groups?parent_id=i0E3B406D53D147BF8C5E724097BAE234`);
    return groups[0].groups;
  }

  async #getRoles(object_id) {
    let obj_perms = await this.#get(`/roles/${object_id}`);
    return obj_perms;
  }
      
  async #getGroupMembers() {
    let group_data = await this.#getGroups();
    let groups = {};

    for (let group of group_data) {
      let members = await this.#get(`/roles/${group.id}/members`);
      groups[group.searchPath] = {
        'group_id': group.id,
        'group_name': group.defaultName,
        'members': members[0].users
      }
    }
        
    return groups;
  }
      

  async get_permissions(object_id) {
    let groups = await this.#getGroupMembers();
    let perms = await this.#getRoles(object_id);
    let permissions = await perms[0].policies.reduce((a,c) => {
      if (c.securityObject.searchPath === 'CAMID("::System Administrators")') return a;
      return [...a, groups[c.securityObject.searchPath]]
    }, []);
  
    return permissions;
  }
}

module.exports = { CognosAPI }
