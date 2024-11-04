from flask import Flask, request, jsonify
from typing import Dict, Any
from db_engine import *

app = Flask(__name__)
db = SimpleDB("mydb")  # Initialize the database

@app.route('/create_table', methods=['POST'])
def create_table():
    table_name = request.json.get('table_name')
    result = db.create_table(table_name)
    db.save_db()
    return jsonify({"message": result})

@app.route('/insert_record', methods=['POST'])
def insert_record():
    table_name = request.json.get('table_name')
    key = request.json.get('key')
    data = request.json.get('data', {})

    if not isinstance(data, dict):
        return jsonify({"error": "Data must be a dictionary"}), 400

    result = db.insert(table_name, key, data)
    if "Error" in result:
        return jsonify({"error": result}), 400
    return jsonify({"message": result})

@app.route('/update_record', methods=['PUT'])
def update_record():
    table_name = request.json.get('table_name')
    key = request.json.get('key')
    data = request.json.get('data', {})

    if not isinstance(data, dict):
        return jsonify({"error": "Data must be a dictionary"}), 400

    result = db.update(table_name, key, data)
    if "Error" in result:
        return jsonify({"error": result}), 404
    return jsonify({"message": result})

@app.route('/delete_record', methods=['DELETE'])
def delete_record():
    table_name = request.json.get('table_name')
    key = request.json.get('key')

    result = db.delete(table_name, key)
    if "Error" in result:
        return jsonify({"error": result}), 404
    return jsonify({"message": result})

@app.route('/read_record', methods=['GET'])
def read_record():
    table_name = request.args.get('table_name')
    key = request.args.get('key')

    result = db.read(table_name, key)
    if isinstance(result, str) and "Error" in result:
        return jsonify({"error": result}), 404
    return jsonify({"record": result})

@app.route('/read_records', methods=['GET'])
def read_records():
    table_name = request.args.get('table_name')
    tree = db.tables.get(table_name)
    
    if not tree:
        return jsonify({"error": "Table not found"}), 404
    
    records = []
    node = tree.root
    
    # Traverse to leftmost leaf node
    while not node.leaf:
        node = node.children[0]
    
    # Collect all key-value pairs from leaf nodes
    while node:
        for i, key in enumerate(node.keys):
            records.append({"key": key, "value": node.values[i]})
        node = node.next_leaf
    
    return jsonify({"records": records})


@app.route('/save_db', methods=['POST'])
def save_db():
    db.save_db()
    return jsonify({"message": "Database saved successfully"})

if __name__ == "__main__":
    app.run(debug=True)
