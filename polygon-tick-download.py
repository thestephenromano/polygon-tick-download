import argparse
from datetime import datetime, timedelta
import json
import requests
import ticks_pb2

base_url = 'https://api.polygon.io/v1/historic/crypto'


def download(url, api_key, limit=10000):
    result = []

    data = download_helper(url, api_key, limit)
    ticks = data['ticks']
    result.extend(ticks)

    while data['ticks']:
        num_ticks = len(ticks)
        offset = ticks[num_ticks - 1]['t']
        data = download_helper(url, api_key, limit, offset)
        ticks = data['ticks']
        if ticks:
            result.extend(ticks)

    print(url, 'ticks:', len(result))

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


def main(cfrom, cto, start_date, api_key, out_dir=None, end_date=None):
    print('cfrom-', cfrom)
    print('cto-', cto)
    print('start_date-', start_date)
    print('api_key-', api_key)
    print('out_dir-', out_dir)
    print('end_date-', end_date)

    delta = end_date - start_date
    date_list = [args.start_date + timedelta(days=x) for x in range(delta.days+1)]
    print(date_list)

    for date in date_list:
        url_path = "%s/%s/%s/%s" % (base_url, cfrom, cto, date.strftime("%Y-%m-%d"))
        print(url_path)

        results = download(url_path, api_key)

        ticks = ticks_pb2.Ticks()
        ticks.symbol = "%s-%s" % (cfrom, cto)
        ticks.day = date.strftime("%Y-%m-%d")

        for result in results:
            tick = ticks.ticks.add()
            tick.timestamp = result['t']
            tick.size = result['s']
            tick.price = result['p']
            tick.exchange = result['x']
            for c in result['c']:
                tick.conditions.append(c)

        if out_dir:
            fname = '%s/%s_%s' % (out_dir, ticks.symbol, ticks.day)
        else:
            fname = '%s_%s' % (ticks.symbol, ticks.day)

        with open(fname, 'wb') as fout:
            fout.write(ticks.SerializeToString())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download tick data from Polygon.io')

    parser.add_argument('--cfrom', type=str, required=True, help='The currency from', default='BTC')
    parser.add_argument('--cto', type=str, required=True, help='The currency to', default='USD')
    parser.add_argument('--start_date', type=valid_date, help='The start date - format YYYY-MM-DD')
    parser.add_argument('--api_key', type=str, required=True, help='API key')
    parser.add_argument('--out_dir', type=str, required=False, help='The output directory')
    parser.add_argument('--end_date', type=valid_date, required=False, help='The end date - format YYYY-MM-DD')

    args = parser.parse_args()
    main(args.cfrom, args.cto, args.start_date, args.api_key, args.out_dir, args.end_date)
