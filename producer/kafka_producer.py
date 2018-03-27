# coding=utf-8
import argparse
import json
import random
import time

import pymongo
import pymysql
from kafka import KafkaProducer
from pymongo import MongoClient


def get_cell(city_grid, lat, lng):
    div_y = float(
        city_grid[0]['north_latitude'] - city_grid[0]['south_latitude'])
    div_x = float(
        city_grid[0]['east_longitude'] - city_grid[0]['west_longitude'])
    init_x = float(city_grid[0]['west_longitude'])
    init_y = float(city_grid[0]['south_latitude'])

    miny, minx, maxy, maxx = lat, lng, lat, lng

    p_lat = abs(miny - init_y)
    i_lat = int(p_lat / div_y) * 50

    p_lng = abs(minx - init_x)
    i_lng = int(p_lng / div_x)

    return i_lat + i_lng


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mongodb", help="Mongodb server", required=True)
    parser.add_argument("--db", help="Mongodb database", required=True)
    parser.add_argument("--col", help="Mongodb collection", required=True)
    parser.add_argument("--kafka", help="Kafka server", required=True)

    args = parser.parse_args()
    client = MongoClient(args.mongodb, 27017)
    producer = KafkaProducer(bootstrap_servers=args.kafka)

    db = client[args.db]
    collection = db[args.col]
    filters = {}
    fields = {'created_at': 1, 'place': 1, 'user.screen_name': 1, 'text': 1,
              '_id': 1, 'extended_tweet.full_text': 1,
              'retweeted_status.text': 1, 'coordinates': 1,
              'retweeted_status.extended_tweet.full_text': 1}
    order = ['$natural', pymongo.DESCENDING]
    first = collection.find_one(filters, {'_id': 1}, sort=[order])

    _id = first['_id']

    sql_conn = pymysql.connect(
        host='mysql3.ctweb.inweb.org.br',
        user='root',
        password='s3cur3@3019.',
        db='festival',
        charset='utf8mb4',
        port=33060,
        cursorclass=pymysql.cursors.DictCursor)

    grid = []
    with sql_conn.cursor() as cursor:
        cursor.execute('SELECT * FROM grid_cell WHERE city_id = 1')
        for row in cursor:
            grid.append(row)

    sql_conn.close()

    while True:
        filters = {'_id': {'$gt': _id}}
        new_cursor = collection.find(filters, fields)
        is_first = False
        for row in new_cursor:
            if not is_first:
                _id = row['_id']
            if row['place']['name'] == 'Curitiba':
                # print row
                row['created_at'] = row['created_at'].isoformat()

                if 'retweeted_status' in row:
                    full_text = row['retweeted_status'].get('extended_tweet',
                                                            {}).get('full_text')
                    if full_text:
                        row['text'] = full_text
                    else:
                        row['text'] = row['retweeted_status']['text']
                    del row['retweeted_status']
                elif 'extended_tweet' in row:
                    row['text'] = row['extended_tweet'].get('full_text') or row[
                        'text']
                    del row['extended_tweet']
                send = True
                if 'coordinates' in row and row.get('coordinates'):
                    row['latitude'] = row['coordinates']['coordinates'][1]
                    row['longitude'] = row['coordinates']['coordinates'][0]
                    del row['coordinates']
                    send = True
                else:
                    bounds = [[-493893386, -491852249],
                              [-256453862, -253467362]]
                    row['latitude'] = random.randrange(*bounds[1]) * 0.0000001
                    row['longitude'] = random.randrange(*bounds[0]) * 0.0000001
                    print row['latitude'], row['latitude']
                    del row['coordinates']
                if send:
                    row['cell'] = get_cell(grid, row['latitude'],
                                           row['longitude'])

                    del row['place']
                    row['user'] = row['user']['screen_name']
                    future = producer.send('tweets_ctb', json.dumps(row))
                    future.get(timeout=5)
                else:
                    print '*',
            else:
                print '@',
        print 'Current Id', _id
        time.sleep(2)


if __name__ == '__main__':
    main()
