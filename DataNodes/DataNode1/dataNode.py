import grpc
import os
from concurrent import futures
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
shared_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'Shared'))
sys.path.append(shared_dir)

from datanode_pb2 import StoreBlockResponse, RetrieveBlockResponse
from datanode_pb2_grpc import DataNodeServiceServicer, add_DataNodeServiceServicer_to_server

class DataNodeService(DataNodeServiceServicer):
    def __init__(self, storage_path, other_data_nodes):
        self.address = f'localhost:{data_node_port}'
        self.blocks = {}
        self.storage_path = storage_path
        self.other_data_nodes = other_data_nodes

    def StoreBlock(self, request, context):
        block_id = request.block_id
        data = request.data
        block_path = os.path.join(self.storage_path, block_id)

        try:
            with open(block_path, "wb") as f:
                f.write(data)
            self.blocks[block_id] = block_path
            print(f"Block {block_id} stored at {block_path}")
            return StoreBlockResponse(success=True)
        except IOError as e:
            print(f"I/O error when storing block {block_id}: {e}")
            return StoreBlockResponse(success=False)
        except Exception as e:
            print(f"Error when storing block {block_id}: {e}")
            return StoreBlockResponse(success=False)

    def RetrieveBlock(self, request, context):
        block_id = request.block_id
        block_path = self.blocks.get(block_id)
        if block_path and os.path.exists(block_path):
            with open(block_path, "rb") as f:
                data = f.read()
            return RetrieveBlockResponse(data=data)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Block not found')
            return RetrieveBlockResponse()

def serve(storage_path, port, other_data_nodes):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_DataNodeServiceServicer_to_server(DataNodeService(storage_path, other_data_nodes), server)
    server.add_insecure_port(f'localhost:{port}')
    print(f'DataNode listening on port {port}')
    server.start()
    print('gRPC server started')
    server.wait_for_termination()

if __name__ == '__main__':
    storage_directory = os.path.join(current_dir, 'storage')  # Relative path to the storage directory
    data_node_port = os.getenv('DATA_NODE_PORT', 50050)
    other_nodes = ["localhost:50051", "localhost:50052"]  # List of other DataNodes to replicate to

    if not os.path.exists(storage_directory):
        os.makedirs(storage_directory)

    serve(storage_directory, data_node_port, other_nodes)
