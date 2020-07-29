import pytest
import logging

from src.utils.mixins import VideocoinMixin

logger = logging.getLogger(__name__)


class TestUser(VideocoinMixin):
    @pytest.mark.first
    @pytest.mark.dependency(name='user_balance', scope='session')
    def test_testing_user_balance(self, user):
        """
        Check that testing user has enough money
        """
        assert user.balance > 100
