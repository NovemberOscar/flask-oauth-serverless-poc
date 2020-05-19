from datetime import datetime, timedelta
from uuid import uuid4

from authlib.oauth2.rfc6749 import ClientMixin, TokenMixin
from authlib.oauth2.rfc6749.util import scope_to_list, list_to_scope
from pynamodb.attributes import UnicodeAttribute, ListAttribute, UTCDateTimeAttribute
from pynamodb.models import Model

from app import settings


class User(Model):
    class Meta:
        table_name = "kseonghyeon-oauth-test-proj-user"
        region = "ap-northeast-2"
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        max_retry_attempts = 3

    user_id = UnicodeAttribute(hash_key=True)
    email_address = UnicodeAttribute()

    def get_user_id(self):
        return self.user_id


class Client(Model, ClientMixin):
    class Meta:
        table_name = "kseonghyeon-oauth-test-proj-client"
        region = "ap-northeast-2"
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        max_retry_attempts = 3

    client_id = UnicodeAttribute(hash_key=True)
    client_secret = UnicodeAttribute()
    scope = ListAttribute(default=[])
    response_types = ListAttribute(default=[])
    allowed_redirect_uris = ListAttribute(null=False)
    token_endpoint_auth_method = UnicodeAttribute(default="client_secret_basic")

    def get_client_id(self):
        return self.client_id

    def get_default_redirect_uri(self):
        return self.allowed_redirect_uris[0]

    def get_allowed_scope(self, scope):
        if not scope:
            return ''
        allowed = set(scope_to_list(self.scope))
        return list_to_scope([s for s in scope.split() if s in allowed])

    def check_redirect_uri(self, redirect_uri):
        return redirect_uri in self.allowed_redirect_uris

    def has_client_secret(self):
        return bool(self.client_secret)

    def check_client_secret(self, client_secret):
        return self.client_secret == client_secret

    def check_token_endpoint_auth_method(self, method):
        return self.token_endpoint_auth_method == method

    def check_response_type(self, response_type):
        return response_type in self.response_types

    def check_grant_type(self, grant_type):
        return grant_type == "code"


class Token(Model, TokenMixin):
    class Meta:
        table_name = "kseonghyeon-oauth-test-proj-token"
        region = "ap-northeast-2"
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        max_retry_attempts = 3

    id = UnicodeAttribute(default=lambda: uuid4().hex)

    user_id = UnicodeAttribute(null=False)
    client_id = UnicodeAttribute(null=False)

    access_token = UnicodeAttribute(null=False)
    refresh_token = UnicodeAttribute()

    issued_at = UTCDateTimeAttribute(null=False, default=datetime.now)
    expires_at = UTCDateTimeAttribute(null=False, default=lambda: datetime.now() + timedelta(hours=5))

    def get_client_id(self):
        return self.client_id

    def get_scope(self):
        return list_to_scope(Client.get(hash_key=self.client_id).scope)

    def get_expires_in(self):
        return (self.expires_at - self.issued_at).seconds

    def get_expires_at(self):
        return self.expires_at
