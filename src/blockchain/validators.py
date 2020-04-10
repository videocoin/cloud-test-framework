import requests

import m3u8


class VCValidationError:
    text = ''

    def __init__(self, text):
        self.text = text


class Chunk:
    number = 0
    duration = 0

    def __init__(self, number, duration):
        self.number = number
        self.duration = duration

    def __eq__(self, other):
        if self.number == other.number and self.duration == other.duration:
            return True
        return False


class BaseValidator:
    name = ''
    description = ''
    errors = []
    infos = []
    is_valid = True

    def get_playlist(self, url):
        r = requests.get(url)
        return r.text

    def get_chunks(self, url):
        chunks = []
        playlist = self.get_playlist(url)
        m3u8_obj = m3u8.loads(playlist)
        for i, c in enumerate(m3u8_obj.segments):
            chunks.append(Chunk(i+1, c.duration))
        return chunks

    def to_json(self):
        return {self.name: {
            'description': self.description,
            'errors': [x.text for x in self.errors],
            'is_valid': self.is_valid,
        }}


class ChunkEventsValidator(BaseValidator):
    name = 'ChunkEventsValidator'
    description = 'Check stream chunk events'

    CHUNKS_EVENTS = [
        'ChunkProofSubmited',
        'ChunkProofValidated',
        'ChunkProofScrapped',
    ]

    def __init__(self, events, input_url, output_url):
        self.events = [x for x in events if x.get('event') in self.CHUNKS_EVENTS]
        self.input_url = input_url
        self.output_url = output_url
        self.errors = []

    def validate(self):
        output_chunks = self.get_chunks(self.output_url)
        for chunk in output_chunks:
            chunk_events = [x for x in self.events if x['args']['chunkId'] == chunk.number]
            if 'ChunkProofSubmited' not in [x.get('event') for x in chunk_events]:
                self.errors.append(VCValidationError('No corresponding ChunkProofSubmited event for chunk #{}'.
                                                     format(chunk.number)))
                self.is_valid = False
            if 'ChunkProofValidated' not in [x.get('event') for x in chunk_events]:
                self.errors.append(VCValidationError('No corresponding ChunkProofValidated event for chunk #{}'.
                                                     format(chunk.number)))
                self.is_valid = False

            if 'ChunkProofScrapped' in [x.get('event') for x in chunk_events]:
                self.errors.append(VCValidationError('ChunkProofScrapped event for chunk #{}'.
                                                     format(chunk.number)))
                self.is_valid = False


class InOutValidator(BaseValidator):
    name = 'InOutValidator'
    description = 'Compare input and output playlists'

    def __init__(self, input_url, output_url):
        self.input_url = input_url
        self.output_url = output_url
        self.errors = []

    def validate(self):
        r = requests.get(self.input_url)
        if r.status_code != 200:
            self.errors.append(VCValidationError('Can\'t access input url'))
            self.is_valid = False
            return
        r = requests.get(self.output_url)
        if r.status_code != 200:
            self.errors.append(VCValidationError('Can\'t access output url'))
            self.is_valid = False
            return
        input_chunks = self.get_chunks(self.input_url)
        output_chunks = self.get_chunks(self.output_url)
        if len(input_chunks) != len(output_chunks):
            self.errors.append(VCValidationError('Different chunk count in input and output'))
            self.is_valid = False
            return
        for i in range(len(input_chunks)):
            if (output_chunks[i].number != input_chunks[i].number) or \
                    (int(output_chunks[i].duration) != int(input_chunks[i].duration)):
                self.errors.append(VCValidationError('Different chunk #{} in input and output'.
                                                     format(input_chunks[i].number)))
                self.is_valid = False


class StreamStateInStreamManagerValidator(BaseValidator):
    name = 'StreamStateInStreamManagerValidator'
    description = 'Check stream chunk events'

    REQUIRED_STATE_EVENTS = [
        "StreamRequested",
        "StreamApproved",
        "StreamCreated",
        "ValidatorAdded",
        "StreamEnded",
    ]

    def __init__(self, events):
        self.event_names = [x.get('event') for x in events if x.get('event') in self.REQUIRED_STATE_EVENTS]
        self.errors = []

    def validate(self):
        for event_name in self.REQUIRED_STATE_EVENTS:
            if event_name not in self.event_names:
                self.errors.append(VCValidationError('Error: missing event {}'.format(event_name)))
                self.is_valid = False


class AccountFundedValidator(BaseValidator):
    name = 'AccountFundedValidator'
    description = 'Check account payments'

    BALANCE_EVENTS = [
        'AccountFunded',
        'Refunded',
        'Deposited',
        'OutOfFunds',
    ]

    def __init__(self, events):
        self.events = [x for x in events if x.get('event') in self.BALANCE_EVENTS]
        self.errors = []

    def validate(self):
        account_funded_events = [x for x in self.events if x.get('event') == 'AccountFunded']
        refunded_events = [x for x in self.events if x.get('event') == 'Refunded']
        deposited_events = [x for x in self.events if x.get('event') == 'Deposited']
        outofFundsEvents = [x for x in self.events if x.get('event') == 'OutOfFunds']

        totalAccountFunded, deposited, refunded = 0, 0, 0
        for e in account_funded_events:
            totalAccountFunded += e['args'].weiAmount
        for e in deposited_events:
            deposited += e['args'].weiAmount
        for e in refunded_events:
            refunded += e['args'].weiAmount
        if not refunded_events:
            self.errors.append(VCValidationError("Error: missing refunded events"))
            self.is_valid = False
        if bool(outofFundsEvents) and refunded > 0:
            self.errors.append(VCValidationError("Error: Inconsistant escrow events outOfFunds and refunded > 0"))
            self.is_valid = False
        else:
            self.infos.append("Info: escrow events tally: deposited({}) == totalAccountFunded({}) + refunded({})".
                              format(deposited, totalAccountFunded, refunded))


class ValidatorCollection:
    is_valid = True

    def __init__(self, events, input_url, output_url):
        self.events = events
        self.input_url = input_url
        self.output_url = output_url

    def validate(self):
        results = {}
        validator_1 = ChunkEventsValidator(
            events=self.events,
            input_url=self.input_url,
            output_url=self.output_url,
        )
        validator_1.validate()
        if not validator_1.is_valid:
            self.is_valid = False
        results.update(validator_1.to_json())

        # validator_2 = InOutValidator(
        #     input_url=self.input_url,
        #     output_url=self.output_url,
        # )
        # validator_2.validate()
        # if not validator_2.is_valid:
        #     self.is_valid = False
        # results.update(validator_2.to_json())

        validator_3 = StreamStateInStreamManagerValidator(
            events=self.events,
        )
        validator_3.validate()
        if not validator_3.is_valid:
            self.is_valid = False
        results.update(validator_3.to_json())

        validator_4 = AccountFundedValidator(
            events=self.events,
        )
        validator_4.validate()
        if not validator_4.is_valid:
            self.is_valid = False
        results.update(validator_4.to_json())

        return results
