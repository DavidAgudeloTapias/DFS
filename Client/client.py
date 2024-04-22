import requests
import argparse
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
shared_dir = os.path.abspath(os.path.join(current_dir, '..', 'NameNode'))
sys.path.append(shared_dir)

from nameNode import DataNodeClient

# NameNode server address
NAMENODE_URL = "http://172.31.86.179:5000"

def upload_file(file_path):
    """
    Upload a file to DFS.
    :param file_path: Path of the file to upload.
    """
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as file:
        files = {'file': (file_name, file)}
        response = requests.post(f"{NAMENODE_URL}/upload", files=files)
        if response.ok:
            print(f"File {file_name} uploaded successfully.")
            print(response.json())  # Show server response
        else:
            print(f"Error uploading file {file_name} -- Error code: {response.status_code}")

def download_file(file_name, save_path):
    """
    Download a file from DFS using gRPC.
    :param file_name: Name of the file to download.
    :param save_path: Path where to save the downloaded file.
    """
    # Get the block information of the file from the NameNode
    name_node_response = requests.get(f"{NAMENODE_URL}/download", params={'file_name': file_name})
    
    if name_node_response.ok:
        blocks_info = name_node_response.json()['blocks_info']

        # Print the block list and URIs for the user
        print(f"Block list and URIs for the file '{file_name}':")
        for block in blocks_info:
            print(f"Block ID: {block['id']}, DataNode URI: {block['data_node_uri']}, "f"ReplicaNode URI: {block.get('replica_node_uri', 'N/A')}")

        with open(os.path.join(save_path, file_name), 'wb') as file:
            for block in blocks_info:
                data_node_address = block["data_node"]
                
                # Attempt to download the block from the primary DataNode
                block_data = download_block_from_datanode(data_node_address, block["id"])
                
                # If the download fails on the primary node, try with the replica
                if not block_data and "replica_node_uri" in block:
                    block_data = download_block_from_datanode(block["replica_node_uri"], block["id"])
                
                if block_data:
                    file.write(block_data)
                else:
                    raise Exception(f"Error downloading block {block['id']} from node {data_node_address} and its replica.")
                    
            print(f"File '{file_name}' has been successfully downloaded and reconstructed.")
    else:
        raise Exception(f"Error retrieving file information for '{file_name}'. Status code: {name_node_response.status_code}")

def download_block_from_datanode(data_node_address, block_id):
    """
    Download a block from a DataNode using gRPC.
    :param data_node_address: URI of the DataNode.
    :param block_id: ID of the block to download.
    :return: Content of the block or None if the download fails.
    """
    try:
        data_node_client = DataNodeClient(data_node_address)
        response = data_node_client.retrieve_block(block_id)
        if response:
            return response.data
    except Exception as e:
        print(f"Error downloading block {block_id} from {data_node_address}: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="DFS CLI Client")
    parser.add_argument("--upload", help="Path of the file to upload", type=str)
    parser.add_argument("--download", help="Name of the file to download", type=str)
    parser.add_argument("--save", help="Path to save the downloaded file", type=str, default=".")
    args = parser.parse_args()

    if args.upload:
        upload_file(args.upload)
    elif args.download:
        download_file(args.download, args.save)
    else:
        print("Invalid arguments. Use --upload to upload or --download to download a file.")

if __name__ == "__main__":
    main()
