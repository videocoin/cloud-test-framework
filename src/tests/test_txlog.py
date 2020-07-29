import pytest
import logging
import time
import requests

from src.utils.mixins import VideocoinMixin
from src.models.stream import StreamFactory
from src.consts.input_values import TXLOG_API_URL

logger = logging.getLogger(__name__)


class TestTXLog(VideocoinMixin):

    @pytest.fixture(autouse=True)
    def create_stream_factory(self, cluster, user):
        self.stream_factory = StreamFactory(cluster, user.token)

    @pytest.mark.smoke
    def test_txlog_service(self):
        """
        Check txlog api health
        """
        url = '{}/api/v1/transactions?limit=5'.format(
            self.get_initial_value(TXLOG_API_URL),
        )
        response = requests.get(url)
        assert response.status_code == 200

        assert len(response.json().get('transactions', [])) == 5

    @pytest.mark.functional
    @pytest.mark.dependency(name='test_txlog_service_new_transactions', depends=["user_balance"], scope='session')
    def test_txlog_service_new_transactions(self, user):
        """
        Check txlog contains transactions for a new stream
        """
        try:
            new_stream = self.stream_factory.create_vod()
            time.sleep(5)
            new_stream.start()

            new_stream.wait_for_status('STREAM_STATUS_PREPARED')
            new_stream.upload_url('http://techslides.com/demos/sample-videos/small.mp4')
            new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
            url = '{}/api/v1/address/{}?limit=10'.format(
                self.get_initial_value(TXLOG_API_URL),
                new_stream.stream_contract_address,
            )
            response = requests.get(url)
            assert response.status_code == 200

            assert len(response.json().get('transactions'))

        finally:
            new_stream.delete()
