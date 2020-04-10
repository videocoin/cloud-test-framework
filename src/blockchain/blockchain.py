import os
import json
import functools
from datetime import datetime

from web3 import Web3
from web3.utils.contracts import find_matching_event_abi
from web3.utils.events import get_event_data
from web3.utils.filters import construct_event_filter_params
from web3.utils.abi import filter_by_type

from web3.middleware import geth_poa_middleware
import eth_utils


VERBOSE = False


def log_print(data):
    if VERBOSE:
        print(data)


def handle_streammanager_event(event):
    log_print(event)


def handle_stream_event(event):
    log_print(event)


def to_dict(data):
    result = {}
    for k, v in data.items():
        result[k] = v
    return result


class Blockchain:
    sm_abi_file = '/abis/StreamManager.json'
    st_abi_file = '/abis/Stream.json'
    blockchain_url = ''
    stream_id = None
    fromBlock = 0
    toBlock = 'latest'
    block_infos = {}

    def __init__(self, blockchain_url, stream_id,  stream_address, stream_manager_address):
        self.w3 = Web3(Web3.HTTPProvider(blockchain_url))
        self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        self.stream_id = int(stream_id)
        connected = self.w3.isConnected()
        if not connected:
            log_print('/n!!!! No connection to blockchain !!!!/n')
        if stream_address:
            self.add_stream(stream_address)
        if stream_manager_address:
            self.add_stream_manager(self.normalize_address(stream_manager_address))

    def normalize_address(self, address):
            as_bytes = eth_utils.to_bytes(hexstr=address)
            return eth_utils.to_normalized_address(as_bytes[-20:])

    def add_stream_manager(self, stream_manager_address):
        module_dir = os.path.dirname(__file__)
        file_path = module_dir + self.sm_abi_file
        with open(file_path) as f:
            info_streammanger_json = json.load(f)
            self.streammanager_abi = info_streammanger_json['abi']
            self.stream_manager_contract = self.w3.eth.contract(address=self.w3.toChecksumAddress(stream_manager_address), abi=self.streammanager_abi)

    def add_stream(self, stream_address):
        module_dir = os.path.dirname(__file__)
        file_path = module_dir + self.st_abi_file
        with open(file_path) as f:
            info_stream_json = json.load(f)
            self.stream_abi = info_stream_json['abi']
            self.stream_contract = self.w3.eth.contract(address=self.w3.toChecksumAddress(stream_address), abi=self.stream_abi)

    def get_block(self):
        return self.w3.eth.blockNumber

    def get_block_info(self, block_hash):
        if self.block_infos.get(block_hash):
            return self.block_infos.get(block_hash)
        else:
            data = self.w3.eth.getBlock(block_hash)
            self.block_infos[block_hash] = data
        return data

    def is_connected(self):
        return self.w3.isConnected()

    def get_event(self, contract_abi, contract_address, event_name, argument_filters=None):
        if not argument_filters:
            argument_filters = {}

        event_abi = find_matching_event_abi(contract_abi, event_name=event_name)

        _, event_filter_params = construct_event_filter_params(event_abi,
                                                               contract_address,
                                                               fromBlock=self.fromBlock,
                                                               toBlock=self.toBlock,
                                                               argument_filters=argument_filters
                                                               )
        found_logs = self.w3.eth.getLogs(event_filter_params)
        event_data = []
        for log in found_logs:
            event_data.append(get_event_data(event_abi, log))
        return event_data

    def get_stream_manager_events(self):
        result = []
        for event in self.get_stream_manager_event_names():
            log_print('Processing event=' + event)
            event_data = self.get_event(self.streammanager_abi, self.stream_manager_contract.address, event, argument_filters={'streamId': self.stream_id})
            for log in event_data:
                log = self.to_log_entry(log)
                result.append(log)
        return result

    def get_stream_events(self):
        result = []
        for event in self.get_stream_event_names():
            log_print('Processing event=' + event)
            event_data = self.get_event(self.stream_abi, self.stream_contract.address, event)

            for log in event_data:
                log = self.to_log_entry(log)
                result.append(log)
        return result

    def get_all_events(self):
        events = self.get_stream_events()
        events.extend(self.get_stream_manager_events())
        return events

    def get_stream_event_names(self):
        filters = [functools.partial(filter_by_type, 'event'), ]
        stream_events = eth_utils.toolz.pipe(self.stream_abi, *filters)
        events = [item['name'] for item in stream_events]
        return events

    def get_stream_manager_event_names(self):
        filters = [functools.partial(filter_by_type, 'event'), ]
        streammanager_events = eth_utils.toolz.pipe(self.streammanager_abi, *filters)
        events = [item['name'] for item in streammanager_events]
        return events

    def to_log_entry(self, record):
        log = to_dict(record)
        log['blockInfo'] = self.get_block_info(log['blockHash'])
        log['transactionInfo'] = self.w3.eth.getTransactionReceipt(log['transactionHash'])
        log['hash'] = str(log['transactionHash'].hex())
        log['datetime'] = datetime.fromtimestamp(log['blockInfo']['timestamp'])
        log_print(log)
        return log
