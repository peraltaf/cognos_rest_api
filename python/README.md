# Cognos Analytics REST API using NodeJS

This is a simple Python script that utilizes the Cognos Analytics REST API to pull all of the reports in a specified folder and getting the permissions/users of a specified object.

## Installation

Install the necessary modules specified in requirement.txt in your Python environment.

```bash
pip install -r requirements.txt
```

## Usage
Modify the config.ini file update the entries for url, namespace, and user for both the [dev] and [prod] sections.

### Running as a standalone script
Run the example.py script
```bash
python example.py
```

The script will prompt you to enter your password and then the folder ID you want to get the contents of as well as its permissions/users. It will also prompt you to enter a file name to export results for the folder contents as a JSON object and folder permissions also as a JSON object.

### Running as a simple REST API
Modify the config.ini file and add a password entry for both the [dev] and [prod] sections. It should look like below
```
[global]
loglevel=INFO


[dev]	
url: url_to_dev_api
namespace: AD1-LDAP
user: my_username
password: my_password

[prod]	
url: url_to_prod_api
namespace: AD1-LDAP
user: my_username
password: my_password
```

Start the server
```bash
python server.py
```

Access the below endpoints.
```
http://localhost:5000/get_reports?folder_id=<folder_id>
http://localhost:5000/get_permissions?object_id=<object_id>
```
