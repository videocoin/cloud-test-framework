import pytest
import requests
import time

from src.consts import endpoints
from src.consts import expected_results
from src.consts import email_body_regex
from src.utils import utils
from src.models.user import User
from src.consts.input_values import NEW_ACCOUNT_EMAIL, NEW_ACCOUNT_PASSWORD
from src.utils.mixins import VideocoinMixin


class TestSignUp(VideocoinMixin):

    @pytest.mark.functional
    def test_signing_up(self, ):
        """
        Check success sign up flow
        """
        email = self.get_initial_value(NEW_ACCOUNT_EMAIL)
        password = self.get_initial_value(NEW_ACCOUNT_PASSWORD)
        name = 'Automation Account'
    
        self.sign_up(self.cluster, email, password, name)
        time.sleep(30)
        self.confirm_email(email, password)
        user = User(self.cluster, email, password, password)
        assert user.balance == 10
        assert user.wallet_address
        user.delete()

    @pytest.mark.functional
    def test_signing_up_with_an_existing_email_returns_error(self, user):
        """
        Check sign up with for a existing user
        """
        email = user.email
        password = user.password
        name = 'Automation Account'

        with pytest.raises(requests.HTTPError) as e:
            self.sign_up(user.cluster, email, password, name)

        assert e.value.response.status_code == 400
        assert e.value.response.json() == expected_results.SIGN_UP_WITH_EXISTING_EMAIL_ERROR

    @pytest.mark.functional
    def test_signing_up_with_short_name_returns_error(self, user):
        """
        Check sign up with wrong data
        """
        email = user.email
        password = user.password
        name = 'K'

        with pytest.raises(requests.HTTPError) as e:
            self.sign_up(user.cluster, email, password, name)

        assert e.value.response.status_code == 400
        assert e.value.response.json() == expected_results.SIGN_UP_WITH_SHORT_NAME_ERROR

    @pytest.mark.functional
    @pytest.mark.parametrize('password', ['1234567890', 'no_number_password', '2short'])
    def test_signing_up_with_invalid_password_returns_error(self, user, password):
        """
        Check sign up with wrong data
        """
        email = user.email
        password = password
        name = 'Automation Account'

        with pytest.raises(requests.HTTPError) as e:
            self.sign_up(user.cluster, email, password, name)

        assert e.value.response.status_code == 400
        assert e.value.response.json() == expected_results.SIGN_UP_WITH_INVALID_PASSWORD

    def confirm_email(self, email, email_password):
        subject = 'Confirm Email'
        token_regex = email_body_regex.CONFIRMATION_URL_REGEX
        confirm_url = utils.get_items_from_email(email, email_password, subject, token_regex)
        r = requests.get(confirm_url)
        assert r.status_code == 200

    def sign_up(self, cluster, email, password, name):
        body = {
            'email': email,
            'password': password,
            'confirm_password': password,
            'name': name,
        }
        base_url = utils.get_base_url(cluster)
        res = requests.post(base_url + endpoints.SIGN_UP, json=body)
        res.raise_for_status()
    
        return res.json()
