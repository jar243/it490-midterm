import requests

api_url = "https://api.themoviedb.org/3/authentication/token/new?api_key=291050bd6f830358af2856e014e9dec6"
response = requests.get(api_url)

print (response)

