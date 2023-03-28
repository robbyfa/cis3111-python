from flask import Flask, jsonify
from google.cloud import datastore
import random

app = Flask(__name__)
datastore_client = datastore.Client()

def generate_numbers(instance_name):
    numbers = [random.randint(0, 100000) for _ in range(1000)]
    instance_key = datastore_client.key('Instance', instance_name)
    entity = datastore.Entity(key=instance_key)
    entity.update({
        'name': instance_name,
        'numbers': numbers
    })
    datastore_client.put(entity)

@app.route('/generate')
def generate():
    instance_name = 'instance-' + str(random.randint(1, 10))
    generate_numbers(instance_name)
    return jsonify({'message': 'Numbers generated successfully'})

@app.route('/results')
def results():
    query = datastore_client.query(kind='Instance')
    instances = list(query.fetch())

    table = []
    all_numbers = []
    for instance in instances:
        table.append({
            'name': instance['name'],
            'total': len(instance['numbers'])
        })
        all_numbers.extend([(number, instance['name']) for number in instance['numbers']])

    largest = max(all_numbers, key=lambda x: x[0])
    smallest = min(all_numbers, key=lambda x: x[0])

    results = {
        'table': table,
        'largest': {'number': largest[0], 'name': largest[1]},
        'smallest': {'number': smallest[0], 'name': smallest[1]}
    }

    return jsonify(results)

    @app.route('/test')
def test():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
