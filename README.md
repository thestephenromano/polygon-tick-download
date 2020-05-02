# polygon-tick-downloader

CLI application to download tick data from Polygon.io

## Installation

### Install requirements

    pip install requirements.txt

#### Generate Protobufs

    protoc -I=. --python_out=. ticks.proto

## Usage

    Download tick data from Polygon.io
    
    optional arguments:
      -h, --help            show this help message and exit
      --cfrom CFROM         The currency from
      --cto CTO             The currency to
      --start_date START_DATE
                            The start date - format YYYY-MM-DD
      --api_key API_KEY     API key

### Example

    $ python polygon-tick-download --cfrom BTC --cto USD --start_date 2020-04-28 --api_key {api key}
