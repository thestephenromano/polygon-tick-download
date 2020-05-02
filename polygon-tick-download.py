import argparse
from datetime import datetime
import json
import requests
import ticks_pb2

base_url = 'https://api.polygon.io/v1/historic/crypto'


def download(url, api_key, limit=10000):
    result = []

    data = download_helper(url, api_key, limit)
    ticks = data['ticks']
    result.extend(ticks)
    print(len(ticks))

    while data['ticks']:
        num_ticks = len(ticks)
        offset = ticks[num_ticks - 1]['t']
        data = download_helper(url, api_key, limit, offset)
        ticks = data['ticks']
        if ticks:
            print(len(ticks))
            result.extend(ticks)

    return result


def download_helper(url, api_key, limit, offset=None):
    payload = {'limit': limit, 'apiKey': api_key, 'offset': offset}
    url = "%s" % (url)
    r = requests.get(url, params=payload)
    return json.loads(r.text)


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def main(cfrom, cto, start_date, api_key):
    print("cfrom-", cfrom)
    print("cto-", cto)
    print("start_date-", start_date)
    print("api_key-", api_key)

    url = "%s/%s/%s/%s" % (base_url, cfrom, cto, start_date)
    results = download(url, api_key)

    ticks = ticks_pb2.Ticks()
    ticks.symbol = "%s-%s" % (cfrom, cto)
    ticks.day = start_date.strftime("%Y-%m-%d")

    for result in results:
        tick = ticks.ticks.add()
        tick.timestamp = result['t']
        tick.size = result['s']
        tick.price = result['p']
        tick.exchange = result['x']
        for c in result['c']:
            tick.conditions.append(c)

    with open("foo.pbuf", "wb") as fout:
        fout.write(ticks.SerializeToString())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download tick data from Polygon.io')

    parser.add_argument('--cfrom', type=str, required=True, help='The currency from', default='BTC')
    parser.add_argument('--cto', type=str, required=True, help='The currency to', default='USD')
    parser.add_argument('--start_date', type=valid_date, help='The start date - format YYYY-MM-DD')
    parser.add_argument('--api_key', type=str, required=True, help='API key')

    args = parser.parse_args()
    main(args.cfrom, args.cto, args.start_date, args.api_key)
