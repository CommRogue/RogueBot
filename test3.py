# Ensure your pyOpenSSL pip package is up to date
# Example posting a image URL:

import requests
r = requests.post(
    "https://api.deepai.org/api/deepdream",
    data={
        'image': 'https://www.telegraph.co.uk/content/dam/news/2016/09/08/107667228_beech-tree-NEWS_trans_NvBQzQNjv4BqplGOf-dgG3z4gg9owgQTXEmhb5tXCQRHAvHRWfzHzHk.jpg',
    },
    headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}
)
print(r.json())
print("ew")