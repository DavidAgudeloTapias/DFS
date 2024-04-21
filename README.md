# Distributed File System (DFS) Project

## Overview
This project implements a simplified Distributed File System (DFS) using Python. It integrates RESTful services and gRPC communication to manage files across multiple server nodes, ensuring data redundancy and high availability. The system includes a client module, a NameNode for metadata management, and DataNodes for data storage.

## Components
1. **Client Module (`client.py`)**: Handles file uploads and downloads, interfacing with the NameNode via RESTful API and DataNodes through gRPC for managing file data blocks.
2. **NameNode (`nameNode.py`)**: Manages metadata for the DFS, maintains the directory tree, and handles file operations, offering endpoints for client interactions.
3. **DataNode (`dataNode.py`)**: Stores actual file data blocks, supports storage and retrieval operations through gRPC.
4. **Protobuf Definitions (`datanode.proto`)**: Defines gRPC services for DataNode communication, detailing procedures for block storage and retrieval.

## Key Features
- **File Upload and Download**: Support for uploading files to the DFS, where files are split and distributed across various DataNodes. Provides functionality for downloading files by reassembling data blocks.
- **REST and gRPC Communication**: Uses REST for client to NameNode interactions and gRPC for efficient NameNode to DataNode communication, ensuring optimal performance and scalability.
- **Protocol Buffer File Generation**: Automates the creation of Python gRPC bindings from the `.proto` files using the command:
  ```bash
  python -m grpc_tools.protoc -I ./Shared --python_out=. --pyi_out=. --grpc_python_out=. ./Shared/datanode.proto

## Technologies Used
- **Programming Language**: Python
- **Communication**: REST, gRPC
- **Data Serialization**: Protocol Buffers
