from flask import Flask, jsonify
import os
import random
import redis

app = Flask(__name__)

# Connect to Redis
redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

@app.route('/generate_numbers')
def generate_numbers():
    instance_name = os.environ.get("INSTANCE_NAME", "unknown")

    for _ in range(1000):
        num = random.randint(0, 100000)
        redis_client.lpush("numbers", num)
        redis_client.lpush(f"instance:{instance_name}", num)

    return jsonify({"status": "success", "instance_name": instance_name})

@app.route('/get_results')
def get_results():
    instance_keys = redis_client.keys("instance:*")
    instances = {}
    min_num = None
    max_num = None
    min_instance = None
    max_instance = None

    for key in instance_keys:
        instance_name = key.split(':')[1]
        numbers = redis_client.lrange(key, 0, -1)
        instances[instance_name] = len(numbers)

        for num in numbers:
            num = int(num)
            if min_num is None or num < min_num:
                min_num = num
                min_instance = instance_name
            if max_num is None or num > max_num:
                max_num = num
                max_instance = instance_name

    return jsonify({
        "instances": instances,
        "min_num": min_num,
        "min_instance": min_instance,
        "max_num": max_num,
        "max_instance": max_instance,
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
