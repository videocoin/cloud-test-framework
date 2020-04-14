import pytest
import logging
import requests

from src.utils.mixins import VideocoinMixin
from src.consts.input_values import TXLOG_API_URL

logger = logging.getLogger(__name__)


class TestTXLog(VideocoinMixin):

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
