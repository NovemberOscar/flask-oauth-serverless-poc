import os

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
USER_DYNAMODB_TABLE_NAME = "kseonghyeon-oauth-test-proj-user"
