import http.client

conn = http.client.HTTPSConnection("richard-duclos.eu.auth0.com")

payload = '{"client_id":"vWvZHFTiM0t0VGCUWzGuZNr5Iqia5odo","client_secret":"K3lMlvCSoX-rDr6l5Ez7sPtkoPSUQ-aFk_6o8Zj90PbWoCmTfLlyHqxDWhVK-Rq4","audience":"https://projet-moto/","grant_type":"client_credentials"}'

headers = {"content-type": "application/json"}

conn.request("POST", "/oauth/token", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
