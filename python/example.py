from configparser import ConfigParser
import keyring
from getpass import getpass
import api
from json import dumps


def main():
    env = 'dev'
    config = ConfigParser(interpolation=None)
    config.read('config.ini')
    BASE_URL = config.get(env, 'url')
    USER = config.get(env, 'user')
    NAMESPACE = config.get(env, 'namespace')
    keyring.set_password(
        f'CA_{env}_{NAMESPACE}',
        USER,
        getpass(f'Input password for {USER} for namespace {NAMESPACE} in {env} environment: ')
    )
    PASSWORD = keyring.get_password(f'CA_{env}_{NAMESPACE}', USER)
    config.set(env, 'password', PASSWORD)

    ca = api.CognosAPI(BASE_URL, ssl_verify=False)
    ca.login(USER, PASSWORD, NAMESPACE)

    target_folder_id = input('Enter a folder ID: ') # inputs can be replaced with sys.args

    print(f'Getting folder contents for ID {target_folder_id}')
    folder_contents = ca.get_reports(target_folder_id)
    contents_file_nm = input('Enter a file name for the folder content JSON output (not including ".json" extension): ')
    with open(f'{contents_file_nm}.json', 'w') as outfile:
        print(f'Writing JSON file {contents_file_nm}.json with {len(folder_contents)} objects')
        outfile.write(dumps(folder_contents, indent=4))

    permissions = ca.get_folder_permissions(target_folder_id)
    permissions_file_nm = input('Enter a file name for the permissions JSON output (not including ".json" extension): ')
    with open(f'{permissions_file_nm}.json', 'w') as outfile:
        print(f'Writing JSON file {permissions_file_nm}.json with {len(permissions)} objects')
        outfile.write(dumps(permissions, indent=4))


if __name__ == '__main__':
    main()
