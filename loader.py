import sys
from datetime import datetime
import zipfile
from decimal import Decimal

import pymongo

time_format = "%Y-%m-%d %H:%M:%S"

times_square = {"NLat": Decimal(40.7592), "SLat": Decimal(40.7520),
                "WLng": Decimal(-73.9908), "ELng": Decimal(-73.9836)}


def parse_trip_data(filename):
    documents = {"both": [], "pickup": [], "drop": []}
    with pymongo.MongoClient() as client:
        db = client.taxi
        with zipfile.ZipFile(filename) as z:
            with z.open(z.infolist()[0]) as f:
                first = True
                for line in f:
                    if first:
                        first = False
                        continue

                    (medallion, hack_license, vendor_id, rate_code,
                     store_and_fwd_flag, pickup_time, drop_time,
                     passenger_count, trip_time_in_secs, trip_distance,
                     pickup_lng, pickup_lat, drop_lng, drop_lat) = \
                        line.strip().split(',')

                    try:
                        pickup_in_ts = ((times_square["WLng"] <=
                                         Decimal(pickup_lng) <=
                                         times_square["ELng"]) and
                                        (times_square["NLat"] >=
                                         Decimal(pickup_lat) >=
                                         times_square["SLat"]))
                        drop_in_ts = ((
                                      times_square["WLng"] <=
                                      Decimal(drop_lng) <=
                                      times_square["ELng"]) and
                                      (times_square["NLat"] >=
                                      Decimal(drop_lat) >=
                                      times_square["SLat"]))
                    except:  # malformed or empty location data
                        continue

                    if pickup_in_ts and drop_in_ts:
                        collection = "both"
                    elif pickup_in_ts and not drop_in_ts:
                        collection = "pickup"
                    elif not pickup_in_ts and drop_in_ts:
                        collection = "drop"
                    else:
                        continue

                    doc = {
                        "medallion": medallion,
                        "license": hack_license,
                        "vendor": vendor_id,
                        "rate_code": int(rate_code),
                        "pickup_time": datetime.strptime(pickup_time,
                                                         time_format),
                        "drop_time": datetime.strptime(drop_time, time_format),
                        "passengers": int(passenger_count),
                        "trip_time": int(trip_time_in_secs),
                        "distance": float(trip_distance)}
                    try:
                        doc["pickup_loc"] = {
                            "type": "Point",
                            "coordinates": [float(pickup_lng),
                                            float(pickup_lat)]}
                    except:
                        pass
                    try:
                        doc["drop_loc"] = {
                            "type": "Point",
                            "coordinates": [float(drop_lng),
                                            float(drop_lat)]}
                    except:
                        pass
                    documents[collection].append(doc)

                    if len(documents["both"]) >= 4000:
                        db.both.insert(documents["both"])
                        documents["both"] = []
                    if len(documents["pickup"]) >= 4000:
                        db.pickup.insert(documents["pickup"])
                        documents["pickup"] = []
                    if len(documents["drop"]) >= 4000:
                        db.drop.insert(documents["drop"])
                        documents["drop"] = []
                if len(documents["both"]) != 0:
                    db.both.insert(documents["both"])
                if len(documents["pickup"]) != 0:
                    db.pickup.insert(documents["pickup"])
                if len(documents["drop"]) != 0:
                    db.drop.insert(documents["drop"])


if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.exit("Error: need to pass at least one zip file to load")
    for s in sys.argv[1:]:
        if s[-4:] != ".zip":
            sys.exit("Error: files passed into loader need to be .zip")
    data_files = sys.argv[1:]
    print('Inserting new documents...')
    for fname in data_files:
        print('\tParsing %s' % fname)
        parse_trip_data(fname)
    print('Done.')
