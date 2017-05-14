import requests
import json
import shutil
import os.path

token = ""
event_id = '1958682181033333'
image_width = 400
api_url = "https://graph.facebook.com/v2.9/"
list_limit = 1000
image_extension = '.jpeg'


def call_api(method, path, params=None, stream=False):
    if params is None:
        params = {}
    params["access_token"] = token
    params["limit"] = list_limit
    if method == 'POST':
        response = requests.post(api_url + path, params=params, stream=stream)
    else:
        response = requests.get(api_url + path, params=params, stream=stream)
    content_type = response.headers["Content-Type"]
    if content_type.find('application/json') > -1:
        r = (json.loads(response.content))
        return r['data']
    else:
        return response


attending_list = call_api("GET", "%s/attending" % (event_id,))

download_path = 'profile_images/'

for i, attending in enumerate(attending_list):
    file_path = download_path + attending["id"] + image_extension
    if not os.path.isfile(file_path):
        image_response = call_api("GET", "%s/picture" % (attending["id"]), params={"width": image_width}, stream=True)
        with open(file_path, 'wb') as f:
            image_response.raw.decode_content = True
            shutil.copyfileobj(image_response.raw, f)

with open('profiles_list.json', "w") as f:
    json.dump(attending_list, f)
