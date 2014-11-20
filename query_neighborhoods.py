import pymongo
import monary

from neighborhood_loader import parse_neighborhood_file


def loc_query(field, nbhd):
    return {field: {"$geoWithin": {"$geometry": nbhd["location"]}}}


def pymongo_count(hoodlist):
    client = pymongo.MongoClient()
    drop = client.taxi.drop
    pickup = client.taxi.pickup
    both = client.taxi.both

    for n in hoodlist.keys():
        num_drops = drop.find(loc_query("pickup_loc", hoodlist[n])).count()
        num_pickups = pickup.find(loc_query("drop_loc", hoodlist[n])).count()
        print str(hoodlist[n]["boroughCode"]) + ", " + n + ', ' + \
            str(num_drops) + ', ' + str(num_pickups)


def collection_count(hoodlist):
    with monary.Monary() as m:
        for n in hoodlist.keys():
            num_drops = m.count("taxi", "drop",
                                loc_query("pickup_loc", hoodlist[n]))
            num_pickups = m.count("taxi", "pickup",
                                  loc_query("drop_loc", hoodlist[n]))
            print str(hoodlist[n]["boroughCode"]) + ", " + n + ', ' + \
                str(num_drops) + ', ' + str(num_pickups)


def count_borough(hoodlist, borough_code):
    with monary.Monary() as m:
        total_drops = 0
        total_pickups = 0
        for n in hoodlist.keys():
            if hoodlist[n]["boroughCode"] == borough_code:
                num_drops = m.count("taxi", "drop",
                                    loc_query("pickup_loc", hoodlist[n]))
                num_pickups = m.count("taxi", "pickup",
                                      loc_query("drop_loc", hoodlist[n]))
                total_drops += num_drops
                total_pickups += num_pickups
                print str(hoodlist[n]["boroughCode"]) + ", " + n + ', ' + \
                    str(num_drops) + ', ' + str(num_pickups)


def get_timeVfreq(metric, collection, field):
    metric_query = "$" + metric
    id_field = "_id." + metric
    field_query = "$" + field

    with monary.Monary() as m:
        agg_pipe = [{"$group": {
                    "_id": {metric: {metric_query: field_query}},
                    "count": {"$sum": 1}}},
                    {"$sort": {"_id.hour": 1}}]
        drop_array = m.aggregate("taxi", collection, agg_pipe,
                                 [id_field, "count"], ["int32", "int32"])
    return drop_array


if __name__ == '__main__':
    data_fle = 'neighborhoods/nyc-pediacities-neighborhoods-v3-polygon.geojson'
    hoods = parse_neighborhood_file(data_fle)
