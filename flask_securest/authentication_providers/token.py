#########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

from itsdangerous import (TimedJSONWebSignatureSerializer,
                          SignatureExpired,
                          BadSignature)

from flask_securest import rest_security
from flask_securest.authentication_providers.abstract_authentication_provider \
    import AbstractAuthenticationProvider

USERNAME_FIELD = 'username'


class TokenAuthenticator(AbstractAuthenticationProvider):

    def __init__(self, secret_key, expires_in_seconds=600):
        self._secret_key = secret_key
        self._serializer = TimedJSONWebSignatureSerializer(self._secret_key,
                                                           expires_in_seconds)

    def generate_auth_token(self):
        return self._serializer.dumps(
            {USERNAME_FIELD: rest_security.get_request_user().username})

    def authenticate(self, auth_info, userstore):
        token = auth_info.token
        if not token:
            raise Exception('token not found on request')

        try:
            open_token = self._serializer.loads(token)
        except SignatureExpired:
            raise Exception('token expired')
        except BadSignature:
            raise Exception('invalid token')

        username = open_token.get(USERNAME_FIELD)
        if not username:
            raise Exception('username not found in token')

        user = userstore.get_user(username)
        if not user:
            raise Exception('failed to authenticate user "{0}", user not found'
                            .format(username))

        return user
