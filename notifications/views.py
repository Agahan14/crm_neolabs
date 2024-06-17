# import jwt
# import time
#
# def generate_jwt(auth_key_path, key_id, team_id):
#     # Load the APNs Auth Key
#     with open(auth_key_path, 'r') as f:
#         auth_key = f.read()
#
#     # Prepare the header
#     headers = {
#         'alg': 'ES256',
#         'kid': key_id,
#         'typ': 'JWT',
#     }
#
#     # Prepare the payload
#     now = int(time.time())
#     payload = {
#         'iss': team_id,
#         'iat': now,
#         'exp': now + 60 * 60,  # Expiration time is 1 hour from now
#         'aud': 'https://appleid.apple.com',
#         'sub': 'cms.neolabs.dev.neo',  # Your App ID
#     }
#
#     # Generate the JWT
#     return jwt.encode(payload, auth_key, algorithm='ES256', headers=headers)
#
# import os
# # Get the current working directory
# current_dir = os.getcwd()
#
# # Construct the absolute path of the AuthKey_KRXXNXQJJJ.p8 file
# auth_key_path = os.path.join(current_dir, '../AuthKey_KRXXNXQJJJ.p8')
# key_id = 'KRXXNXQJJJ'
# team_id = '6L9DH3S5SA'
#
# # valid_jwt = generate_jwt(
# #     auth_key_path=auth_key_path,
# #     key_id=key_id,
# #     team_id=team_id
# # )
# # print(valid_jwt)
#
# from apns2.client import APNsClient
# from apns2.credentials import TokenCredentials
#
# def get_apns_client(auth_key_path, key_id, team_id):
#     # Generate a JWT
#     # jwt_token = generate_jwt(auth_key_path, key_id, team_id)
#
#     # Set up the credentials
#     credentials = TokenCredentials(
#         auth_key_path=auth_key_path,
#         auth_key_id=key_id,
#         team_id=team_id,
#     )
#
#     # Create the APNs client
#     client = APNsClient(credentials=credentials, use_sandbox=True)
#
#     return client
#
#
#
# client = get_apns_client(
#     auth_key_path=auth_key_path,
#     key_id=key_id,
#     team_id=team_id)
#
# payload = {
#     "aps": {
#         "alert": {
#             "title": "Здарова, Заебал!",
#             "body": "Че там?"
#         },
#         "badge": 1,
#         "sound": "default"
#     },
#     "custom_data": {
#         "key1": "value1",
#         "key2": "value2"
#     }
# }
# import json
# from apns2.payload import Payload
# from apns2.client import Notification
# from apns2.errors import BadDeviceToken
#
# # Create a payload object
# # payload = Payload(=json.dumps(payload))
# token = '4a9a2638aeea54278c5cbc4f7407e09c9fbc5da5ca986a52895a07ef308effd8'
# # Create a notification request object
# notification = Notification(
#     payload=payload,
#     token=token
# )
#
# try:
#     response = client.send_notification(notification=notification, token_hex=token)
#     print('Notification sent:', response)
# except BadDeviceToken as e:
#     print('Invalid device token:', e)


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cms.settings")
# from django.conf import settings
# settings.configure()

#
# device = APNSDevice.objects.create(
#     registration_id="4a9a2638aeea54278c5cbc4f7407e09c9fbc5da5ca986a52895a07ef308effd8",
#     cloud_message_type="APNS",
# )
#
# try:
#     response = device.send_message("Здарова, заебал!")
#     print('Notification sent:', response)
# except BaseException as e:
#     print('Invalid device token:', e)
# # device.send_message("Здарова, заебал!")

from rest_framework.views import APIView
from rest_framework.response import Response
from push_notifications.models import APNSDevice
from .models import Notifcation

class PushNotificationView(APIView):

    def post(self, request, format=None):
        # Get the device token from the request data
        device_token = request.data.get('device_token')

        # Create an APNSDevice object with the device token
        device = APNSDevice.objects.create(
            registration_id=device_token
            # cloud_message_type='APNS'
        )
        notifications = Notifcation.objects.create(
            title='Hello',
            body='Privet',
            type='go'
        )
        payload = {
            'title': notifications.title,
            'body':notifications.body,
            'type':notifications.type
        }

        # Send a push notification to the device
        device.send_message(payload)

        # Return a success response
        return Response({'message': 'Push notification sent'})

