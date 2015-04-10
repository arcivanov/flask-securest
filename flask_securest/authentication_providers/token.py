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


from flask import current_app, request
from itsdangerous import (TimedJSONWebSignatureSerializer,
                          SignatureExpired,
                          BadSignature)

from flask_securest import rest_security
from flask_securest.authentication_providers.abstract_authentication_provider \
    import AbstractAuthenticationProvider


DEFAULT_TOKEN_HEADER_NAME = 'Authentication-Token'
USERNAME_FIELD = 'username'


class TokenAuthenticator(AbstractAuthenticationProvider):

    def __init__(self, secret_key, expires_in=600):
        self._secret_key = secret_key
        self._serializer = TimedJSONWebSignatureSerializer(self._secret_key,
                                                           expires_in)

    def generate_auth_token(self):
        return self._serializer.dumps(
            {USERNAME_FIELD: rest_security.get_request_user().username})

    def authenticate(self, userstore):
        token = _get_auth_info_from_request()
        if not token:
            raise Exception('token is missing or empty')

        try:
            open_token = self._serializer.loads(token)
        except SignatureExpired:
            raise Exception('token expired')
        except BadSignature:
            raise Exception('invalid token')

        username = open_token.get(USERNAME_FIELD)
        if not username:
            raise Exception('invalid token')

        user = userstore.get_user(username)
        if not user:
            raise Exception('user not found')

        return user


def _get_auth_info_from_request():
    token_header_name = current_app.config.get('AUTH_TOKEN_HEADER_NAME',
                                               DEFAULT_TOKEN_HEADER_NAME)
    token = request.headers.get(token_header_name)
    if not token:
        raise Exception('Authentication header not found on request: {0}'
                        .format(token_header_name))
    return token
