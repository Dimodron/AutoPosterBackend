# Post Generate AI Service

## Generate code from .proto

## После того как скомпилсятся прописать в pb2_grpc путь interface.telegram_service_pb2 as telegram__service__pb2
```bash
python -m grpc_tools.protoc -I. --python_out=./interface --grpc_python_out=./interface telegram_service.proto
```