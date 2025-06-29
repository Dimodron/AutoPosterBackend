# Post Generate AI Service

## Generate code from .proto

## После того как скомпилсятся прописать в interface.analytic_service
```bash
python -m grpc_tools.protoc -I. --python_out=./interface/ --grpc_python_out=./interface/ analytic_service.proto
```