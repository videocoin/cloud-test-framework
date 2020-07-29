import os

LINK = 'LINK'
BASE_URL = 'BASE_URL'
API_URL = 'API_URL'

ACCOUNT_EMAIL_DEFAULT = 'ACCOUNT_EMAIL_DEFAULT'
EMAIL_PASSWORD = 'EMAIL_PASSWORD'
ACCOUNT_PASSWORD_DEFAULT = 'ACCOUNT_PASSWORD_DEFAULT'
NEW_ACCOUNT_EMAIL = 'NEW_ACCOUNT_EMAIL'
NEW_ACCOUNT_PASSWORD = 'NEW_ACCOUNT_PASSWORD'
DEPOSIT_ADDRESS_METAMASK = 'DEPOSIT_ADDRESS_METAMASK'
PRIVATE_KEY_METAMASK = 'PRIVATE_KEY_METAMASK'
DEPOSIT_ADDRESS_DUMPSTER = 'DEPOSIT_ADDRESS_DUMPSTER'
DEPOSIT_ADDRESS_TOO_SHORT = 'DEPOSIT_ADDRESS_TOO_SHORT'
RINKEBY_VID_BANK = 'RINKEBY_VID_BANK'
STREAM_MANAGER_CONTRACT_ADDR = 'STREAM_MANAGER_CONTRACT_ADDR'
TXLOG_API_URL = 'TXLOG_API_URL'
NATIVE_GAS_AMOUNT = 'NATIVE_GAS_AMOUNT'
RPC_NODE_URL = 'RPC_NODE_URL'
TEST_USER_INFORMATION = 'TEST_USER_INFORMATION'

# common vars
SENDGRID_KEY = 'SENDGRID_KEY'
REPORT_EMAILS = 'REPORT_EMAILS'

VALUES = {
    'dev': {
        'LINK': 'https://console.dev.videocoin.network/',
        'BASE_URL': 'https://console.dev.videocoin.network',
        'API_URL': 'https://dev.videocoin.network',
        'ACCOUNT_EMAIL_DEFAULT': 'kudorussiaru@gmail.com',
        'EMAIL_PASSWORD': 'P@$$w0rd',
        'ACCOUNT_PASSWORD_DEFAULT': 'tester123',

        'NEW_ACCOUNT_EMAIL': 'videocointtest@yandex.ru',
        'NEW_ACCOUNT_PASSWORD': 'r5ooFn9Jinwg1Mb2',

        'DEPOSIT_ADDRESS_METAMASK': '0x1C4215Fcf5599173BBbc8cDb9119aE42b44ce2D4',
        'PRIVATE_KEY_METAMASK': (
            '523FC9D14D9610691BE281348968976FD397788EED49B1DB8949005ECA85B2E0'
        ),
        'DEPOSIT_ADDRESS_DUMPSTER': '0x3F8d126aa636B64C919129b42e1fe0C498cEdF5c',
        'DEPOSIT_ADDRESS_TOO_SHORT': '0x1C4215Fcf5599173BBbc8cDb9119aE42b44ce',

        'RINKEBY_VID_BANK': '0x00125ab819af65163bba61c1b14b23d662c246ca',

        'STREAM_MANAGER_CONTRACT_ADDR': '0x000000000000000000000000000000000000101',

        'TXLOG_API_URL': 'https://symphony.dev.videocoin.net',

        'NATIVE_GAS_AMOUNT': 1000000000000000000,
        'RPC_NODE_URL': os.environ.get('RPC_NODE_URL_DEV'),
        'SENDGRID_KEY': os.environ.get('SENDGRID_KEY'),
        'REPORT_EMAILS': os.environ.get('REPORT_EMAILS'),
        'TEST_USER_INFORMATION':  {
            'id': '3b6c89e3-098e-41e9-4d6b-71310ec247b0',
            'email': 'kudorussiaru@gmail.com',
            'first_name': 'test',
            'last_name': 'user',
            'is_active': True,
            'account': {
                'id': '25237a3c-d0bc-45d2-75c8-3f835f0012e3',
                'address': '0x00125Ab819Af65163bBa61C1B14B23D662C246CA',
            }
        },
    },
    'snb': {
        'LINK': 'https://console.snb.videocoin.network/',
        'BASE_URL': 'https://console.snb.videocoin.network',
        'API_URL': 'https://snb.videocoin.network',
        'ACCOUNT_EMAIL_DEFAULT': 'kudorussiaru@gmail.com',
        'EMAIL_PASSWORD': 'P@$$w0rd',
        'ACCOUNT_PASSWORD_DEFAULT': 'tester123',

        'NEW_ACCOUNT_EMAIL': 'videocointtest@yandex.ru',
        'NEW_ACCOUNT_PASSWORD': 'r5ooFn9Jinwg1Mb2',

        'DEPOSIT_ADDRESS_METAMASK': '0x1C4215Fcf5599173BBbc8cDb9119aE42b44ce2D4',
        'PRIVATE_KEY_METAMASK': (
            '523FC9D14D9610691BE281348968976FD397788EED49B1DB8949005ECA85B2E0'
        ),
        'DEPOSIT_ADDRESS_DUMPSTER': '0x3F8d126aa636B64C919129b42e1fe0C498cEdF5c',
        'DEPOSIT_ADDRESS_TOO_SHORT': '0x1C4215Fcf5599173BBbc8cDb9119aE42b44ce',

        'RINKEBY_VID_BANK': '0x00125ab819af65163bba61c1b14b23d662c246ca',

        'STREAM_MANAGER_CONTRACT_ADDR': '0x000000000000000000000000000000000000101',

        'TXLOG_API_URL': 'https://txlog.dev.kili.videocoin.network',

        'NATIVE_GAS_AMOUNT': 1000000000000000000,
        'RPC_NODE_URL': os.environ.get('RPC_NODE_URL_SNB'),
        'SENDGRID_KEY': os.environ.get('SENDGRID_KEY'),
        'REPORT_EMAILS': os.environ.get('REPORT_EMAILS'),
        'TEST_USER_INFORMATION':  {
            'id': 'b2c96236-0f97-4f59-702d-c07277a2b200',
            'email': 'kudorussiaru@gmail.com',
            'first_name': 'test',
            'last_name': 'user',
            'is_active': True,
            'account': {
                'id': '25237a3c-d0bc-45d2-75c8-3f835f0012e3',
                'address': '0x00Eb351e3fA562DEeAeAE844d5D0A736da6e0578',
            }},
    },
    'kili': {
        'LINK': 'https://console.videocoin.network',
        'BASE_URL': 'https://console.videocoin.network',
        'API_URL': 'https://videocoin.network',

        'ACCOUNT_EMAIL_DEFAULT': 'kudorussiaru@gmail.com',
        'EMAIL_PASSWORD': 'P@$$w0rd',
        'ACCOUNT_PASSWORD_DEFAULT': 'tester123',

        'NEW_ACCOUNT_EMAIL': 'videocointtest@yandex.ru',
        'NEW_ACCOUNT_PASSWORD': 'r5ooFn9Jinwg1Mb2',

        'DEPOSIT_ADDRESS_METAMASK': '0x1C4215Fcf5599173BBbc8cDb9119aE42b44ce2D4',
        'PRIVATE_KEY_METAMASK': (
            '523FC9D14D9610691BE281348968976FD397788EED49B1DB8949005ECA85B2E0'
        ),
        'DEPOSIT_ADDRESS_DUMPSTER': '0x3F8d126aa636B64C919129b42e1fe0C498cEdF5c',
        'DEPOSIT_ADDRESS_TOO_SHORT': '0x1C4215Fcf5599173BBbc8cDb9119aE42b44ce',

        'RINKEBY_VID_BANK': '0x00125ab819af65163bba61c1b14b23d662c246ca',

        'STREAM_MANAGER_CONTRACT_ADDR': '0x000000000000000000000000000000000000101',

        'TXLOG_API_URL': 'https://txlog.dev.kili.videocoin.network',

        'NATIVE_GAS_AMOUNT': 1000000000000000000,
        'RPC_NODE_URL': os.environ.get('RPC_NODE_URL_KILI'),
        'SENDGRID_KEY': os.environ.get('SENDGRID_KEY'),
        'REPORT_EMAILS': os.environ.get('REPORT_EMAILS'),
        'TEST_USER_INFORMATION':  {
            'id': '',
            'email': 'kgoautomation@gmail.com',
            'first_name': 'test',
            'last_name': 'user',
            'is_active': True,
            'account': {
                'id': '25237a3c-d0bc-45d2-75c8-3f835f0012e3',
                'address': '0x003d07A64C2FeFc8C1654EF742F9AF4088354090',
            }
        },
    },
}


def get_initial_value(cluster, variable):
    return VALUES[cluster][variable]
