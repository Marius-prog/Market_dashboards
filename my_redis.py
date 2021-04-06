import json

import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

name = redis_client.get('name')

print(name)

redis_client.set('microsoft_fundmentals_data', json.dumps({'pe': 33}))
