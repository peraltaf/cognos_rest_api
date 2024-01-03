# Cognos Analytics REST API using NodeJS

This is a simple Node script that utilizes the Cognos Analytics REST API to pull all of the reports in a specified folder and getting the permissions/users of a specified object.

## Installation

Use NPM to install the necessary packages specified in package.json.

```bash
npm install
```

## Usage
Create an .env file that contains entries for API_URL, API_USER, API_PASS, and NAMESPACE. The file should look similar to below.
```
API_URL=url_to_api
API_USER=my_username
API_PASS=my_password
NAMESPACE=my_namespace
```

### Running as a standalone script
Instantiate a new CognosAPI object 
```javascript
const { CognosAPI } = require('./api.js');

const test = async () => {
  let ca = new CognosAPI(process.env.API_URL);
  await ca.login(process.env.API_USER, process.env.API_PASS, process.env.NAMESPACE);

  /*** List all reports for a specified folder ID ***/
  console.dir(await ca.get_reports('<folder ID>'), { depth: null });

  /*** List all reports for a specified folder ID ***/
  console.dir(await ca.get_permissions('<report ID or folder ID>'), { depth: null });
}

test();
```

### Running as a simple REST API
Start the server
```javascript
npm run start
```

Access the below endpoints.
```
http://localhost:3000/get_reports?folder_id=<folder_id>
http://localhost:3000/get_permissions?folder_id=<object_id>
```
