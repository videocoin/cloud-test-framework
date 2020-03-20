import requests

from src.consts import endpoints
from src.models.base import BaseModel


class ProfileFactory(BaseModel):
    def all(self):
        response = requests.get(self.base_url + endpoints.PROFILE)
        response.raise_for_status()
        return response.json()['items']

    def get(self, profile_name=None):
        output_profiles = self.all()
        if not profile_name:
            # If profile_id nor profile_name is specified, assume
            # user will take any profile (the first)
            profile_id = output_profiles[0]['id']
        else:
            for profile in output_profiles:
                if profile['name'] == profile_name:
                    profile_id = profile['id']
        if not profile_id:
            raise ValueError('Profile does not exist')
        return profile_id


class Profiles(BaseModel):

    def __init__(self, cluster, token, id):
        self.id = id
        super().__init__(cluster, token)

    def json(self):
        response = requests.get(
            self.base_url + endpoints.PROFILE + '/' + self.id, headers=self.headers
        )
        response.raise_for_status()

        return response.json()

    @property
    def name(self):
        return self.json()['name']
