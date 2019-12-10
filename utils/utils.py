import email
import poplib
import quopri
import re
import requests
import logging

from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

logger = logging.getLogger(__name__)


def get_raw_request(method, url, body={}):
    req = requests.Request(method, url, data=body)
    prepared = req.prepare()

    def pretty_print_POST(req):
        """
        Taken from https://stackoverflow.com/questions/20658572/python-requests-print-entire-http-request-raw
        ---
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in
        this function because it is programmed to be pretty
        printed and may differ from the actual request.
        """
        print(
            '{}\n{}\r\n{}\r\n\r\n{}'.format(
                '-----------START-----------',
                req.method + ' ' + req.url,
                '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
                req.body,
            )
        )

    pretty_print_POST(prepared)


def get_items_from_email(test_email, test_email_password, support_subject, *body_regex):
    """
    Remember to enable POP server stuff on the test email being used
    """
    if test_email.split('@')[1] == 'gmail.com':
        pop_server = 'pop.gmail.com'
    else:
        raise ValueError('Invalid email format or POP server not supported')

    pop_conn = poplib.POP3_SSL(pop_server)
    pop_conn.user(test_email)
    pop_conn.pass_(test_email_password)

    support_email = 'support@videocoin.network'

    # List of email is given in chronological ascending order
    email_count = len(pop_conn.list()[1])
    # if email_count > 0:
    #     logger.warning('Email count is not 0. Tests might pick up old emails.')
    #     logger.warning('Email count: %d', email_count)

    while email_count > 0:
        raw_email = b"\n".join(pop_conn.retr(email_count)[1])
        parsed_email = email.message_from_bytes(raw_email)
        email_from = parsed_email['From']
        parsed_email_from = re.match(r'^.* <(.+)>$', email_from).group(1)
        logger.debug(
            'Parsed email "From" line on email #%d: %s', email_count, parsed_email_from
        )
        subject = parsed_email['Subject']
        logger.debug('Email subject line on email #%d: %s', email_count, subject)

        email_body_str = None
        if parsed_email_from == support_email and subject == support_subject:
            # pdb.set_trace()
            body = parsed_email.get_payload()
            # Read more about quoted-printable encodings here:
            # https://stackoverflow.com/questions/15621510/how-to-understand-the-equal-sign-symbol-in-imap-email-text
            # https://docs.python.org/3.7/library/quopri.html
            email_body_bytes = quopri.decodestring(str(body[1]))

            # Having trouble with decoding using utf-8, have to use ISO-8859-1
            # https://stackoverflow.com/questions/23772144/python-unicodedecodeerror-utf8-codec-cant-decode-byte-0xc0-in-position-0-i
            email_body_str = email_body_bytes.decode('ISO-8859-1')
            # logger.debug('Full email body: %s', email_body_str)
            break
        email_count -= 1

    if email_count == 0:
        raise IndexError('Email cannot be found')

    try:
        regex_result = {}
        for regex in body_regex:
            result = re.search(regex.pattern, email_body_str).group(1)
            regex_result[regex.name] = result
            logger.debug('regex found for pattern %s: %s', regex.name, result)
    finally:
        pop_conn.dele(email_count)
        pop_conn.quit()
        return result if len(regex_result) == 1 else regex_result


def send_vid_to_account(address, amount):
    if type(amount) == float:
        amount = int(amount)
        logger.warning(
            'Cannot send float VID amount to address. '
            'Converting float value to integer'
        )

    body = {'account': address, 'amount': amount}

    res = requests.post(
        'http://faucet.dev.kili.videocoin.network',
        json=body,
        auth=('dev1', 'D6msEL93LJT5RaPk'),
    )
    res.raise_for_status()

    # return res.json()


def get_vid_balance_of_erc20(addr, network='rinkeby'):
    if network == 'rinkeby':
        network_url = 'https://rinkeby.infura.io'
        token_addr = '0x0A94F11D89e799A2a6b9EAdC784FfD3897592dD7'

    w3 = Web3(HTTPProvider(network_url))
    # Still don't really understand this...Read more here:
    # https://web3py.readthedocs.io/en/latest/middleware.html#geth-style-proof-of-authority
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    ABI = [
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": False,
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "payable": False,
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "type": "function",
        },
    ]
    vid_addr = w3.eth.contract(token_addr, abi=ABI)
    amt = vid_addr.functions.balanceOf(addr).call()

    return amt


def get_base_url(cluster):
    env = ''
    if cluster == 'snb':
        env = '.snb'
    return 'https://studio{}.videocoin.network'.format(env)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 0:
        addr = sys.argv[1]
        send_vid_to_account(addr, 20)
