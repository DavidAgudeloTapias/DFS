from flask import Flask, request, jsonify
import os
import grpc
from datanode_pb2 import StoreBlockRequest, RetrieveBlockRequest
from datanode_pb2_grpc import DataNodeServiceStub

class DataNodeClient:
    def __init__(self, address):
        self.channel = grpc.insecure_channel(address)
        self.stub = DataNodeServiceStub(self.channel)

    def store_block(self, block_id, data):
        request = StoreBlockRequest(block_id=block_id, data=data)
        return self.stub.StoreBlock(request)

    def retrieve_block(self, block_id):
        request = RetrieveBlockRequest(block_id=block_id)
        return self.stub.RetrieveBlock(request)

class NameNode:
    def __init__(self):
        self.files = {}
        self.data_nodes = ["172.31.88.105:50050", "172.31.84.218:50051", "172.31.94.91:50052"]
        self.block_size = 128 * 128  # Block size in bytes (128 KB)

    def add_file(self, file_name, file_path):
        file_size = os.path.getsize(file_path)
        num_blocks = (file_size + self.block_size - 1) // self.block_size
        blocks_info = []

        # Get the list of nodes that are not the data node to assign replicas
        for i in range(num_blocks):
            data_node_index = i % len(self.data_nodes)
            data_node = self.data_nodes[data_node_index]
            # Choose the replica node other than the same data node
            replica_nodes = self.data_nodes[:data_node_index] + self.data_nodes[data_node_index + 1:]
            replica_node_index = (i + 1) % len(replica_nodes)
            replica_node = replica_nodes[replica_node_index]

            block_id = f"{file_name}_block_{i}"
            blocks_info.append({
                "id": block_id,
                "data_node": data_node,
                "replica_node": replica_node,
                "start": i * self.block_size,
                "size": min(self.block_size, file_size - (i * self.block_size))
            })

        self.files[file_name] = blocks_info
        return blocks_info

    def get_file_block_info(self, file_name):
        file_info = self.files.get(file_name)
        if not file_info:
            return None
        
        for block in file_info:
            # The address format is "host:port"
            data_node_host, data_node_port = block['data_node'].split(':')
            replica_node_host, replica_node_port = block['replica_node'].split(':')
            
            block['data_node_uri'] = f"http://{data_node_host}:{data_node_port}/block/{block['id']}"
            block['replica_node_uri'] = f"http://{replica_node_host}:{replica_node_port}/block/{block['id']}"
        return file_info

app = Flask(__name__)
name_node = NameNode()
current_dir = os.path.dirname(os.path.abspath(__file__))
temp_storage_path = os.path.join(current_dir, 'temp_storage')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    file_name = file.filename
    if not os.path.exists(temp_storage_path):
        os.makedirs(temp_storage_path)

    file_path = os.path.join(temp_storage_path, file_name)
    file.save(file_path)

    blocks_info = name_node.add_file(file_name, file_path)

    for block in blocks_info:
        data_node_address = block["data_node"]
        replica_node_address = block["replica_node"]
        block_id = block["id"]
        start_byte = block["start"]
        block_size = block["size"]

        with open(file_path, "rb") as f:
            f.seek(start_byte)
            block_data = f.read(block_size)

        data_node_client = DataNodeClient(data_node_address)
        store_response = data_node_client.store_block(block_id, block_data)

        if not store_response.success:
            return jsonify({"error": f"Failed to store block {block_id} at {data_node_address}"}), 500

        replica_node_client = DataNodeClient(replica_node_address)
        replica_response = replica_node_client.store_block(block_id, block_data)

        if not replica_response.success:
            return jsonify({"error": f"Failed to replicate block {block_id} at {replica_node_address}"}), 500

    return jsonify({"message": f"File {file_name} uploaded successfully", "blocks_info": blocks_info}), 200

@app.route('/download', methods=['GET'])
def download():
    file_name = request.args.get('file_name')
    if not file_name:
        return jsonify({"error": "No file name provided"}), 400

    file_info = name_node.get_file_block_info(file_name)
    if not file_info:
        return jsonify({"error": "File not found"}), 404

    return jsonify({"blocks_info": file_info})

if __name__ == '__main__':
    app.run(debug=True, host='172.31.86.179', port=5000)
