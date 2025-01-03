# Oddpub API

This is a FastAPI application for processing PDF files using the oddpub functions: `pdf_convert`, `pdf_load`, and `open_data_search`.

## Project structure
services/
└── oddpub/
    ├── dockerfile
    ├── main.py
    ├── pyproject.toml
    └── README.md

## Requirements

- Python 3.11
- Docker for containerized deployment

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nimh-dsst/dsst-etl.git
   cd services/oddpub
   ```

2. **Build the Docker image**:
   ```bash
   docker build -t oddpub-api .
   ```

3. **Start the Docker container**:
   ```bash
   docker run -p 8071:8071 -v $PWD:/app  oddpub-api
   ```

## Usage

Access the API at `http://localhost:8071/oddpub` to upload a PDF file and receive JSON output.
Example curl command:

```bash
curl -X POST -F "file=@/path/to/your/file.pdf" http://localhost:80/oddpub
```

Response:

```json
{
  "article": "test1.txt",
  "is_open_data": false,
  "open_data_category": "",
  "is_reuse": false,
  "is_open_code": false,
  "is_open_data_das": false,
  "is_open_code_cas": false,
  "das": null,
  "open_data_statements": "",
  "cas": null,
  "open_code_statements": ""
}
```

