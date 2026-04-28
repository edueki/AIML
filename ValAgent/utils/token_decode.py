import base64, json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzYyMDg1NTQwLCJleHAiOjE3NjIwODkxNDB9.vK0ykYPVtPwZ56aQ_ExkII95YzAaFBE9V8_buaFxhAE"
parts = token.split('.')
header  = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
print(header)
print(payload)
