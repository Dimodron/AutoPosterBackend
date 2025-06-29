# Post Generate AI Service

## Generate code from .proto

## После того как скомпилсятся прописать в interface.ai_generation_service_pb2
```bash
python -m grpc_tools.protoc -I. --python_out=./interface/ --grpc_python_out=./interface/ ai_service.proto
```