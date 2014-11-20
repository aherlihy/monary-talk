#!/bin/python
import sys

import json


def parse_neighborhood_file(hoodfile):
    with open(hoodfile) as f:
        # special case for multipolygon hoods bc descartes
        multi_polygons = {
            "Bayswater": ("Queens", 4),
            "Broad Channel": ("Queens", 4),
            "City Island": ("Bronx", 2),
            "Howard Beach": ("Queens", 4),
            "Jamaica Bay": ("Brooklyn", 3),
            "Marine Park": ("Brooklyn", 3),
            "Pelham Bay Park": ("Bronx", 2),
            "Pelham Islands": ("Bronx", 2)}
        neighborhoods = {k: {"location":
                                 {"type": "MultiPolygon",
                                  "coordinates": []},
                             "borough": v[0],
                             "boroughCode": v[1]}
                         for k, v in multi_polygons.items()}
        try:
            raw_data = json.load(f)['features']

            assert len(raw_data) == 310

            for nbhd in raw_data:
                area_name = str(nbhd["properties"]["neighborhood"])

                if area_name in multi_polygons.keys():
                    neighborhoods[area_name]["location"]["coordinates"].append(
                        nbhd["geometry"]["coordinates"])
                    continue

                # check file is the one we want
                assert str(nbhd["type"]) == "Feature"
                assert str(nbhd["geometry"]["type"]) == "Polygon"
                assert len(nbhd["geometry"]["coordinates"]) == 1
                assert [True if len(i) == 2 else False for i in
                          nbhd["geometry"]["coordinates"][0]]

                borough = nbhd["properties"]["borough"]
                borough_code = int(nbhd["properties"]["boroughCode"])
                geojson = nbhd["geometry"]

                neighborhoods[area_name] = {"location": geojson,
                                            "borough": borough,
                                            "boroughCode": borough_code}

            assert len(neighborhoods) == 266
        except:
            sys.exit("Malformed neighborhood file: did you get the file \
                 at http://blog.pediacities.com/2013/10/neighborhoods-map/?")
        return neighborhoods


def pretty_print(datas):
    for n in datas.keys():
        print str(datas[n]["boroughCode"]) + " : " + \
            datas[n]["borough"] + " : " + n
        print "\t" + str(datas[n]["location"])

def load_precomputed_maxmin(boroughs):
    max_d, min_d, max_p, min_p = -1, -1, -1, -1
    max_d_name, min_d_name, max_p_name, min_p_name = "", "", "", ""
    with open('neighborhoods/monary_count.csv') as f:
        for line in f:
            (c, x, y, z) = line.strip().split(", ")

            if int(c) not in boroughs:
                continue
            if max_d < int(y) or max_d < 0:
                max_d = int(y)
                max_d_name = x
            elif max_d == int(y):
                max_d_name += ", "
                max_d_name += x
            if min_d > int(y) or min_d < 0:
                min_d = int(y)
                min_d_name = x
            elif min_d == int(y):
                min_d_name += ", "
                min_d_name += x
            if max_p < int(z) or max_p < 0:
                max_p = int(z)
                max_p_name = x
            elif max_p == int(z):
                max_p_name += ", "
                max_p_name += x
            if min_p > int(z) or min_p < 0:
                min_p = int(z)
                min_p_name = x
            elif min_p == int(z):
                min_p_name += ", "
                min_p_name += x
    if min_d == 0:
        min_d = 1
    if min_p == 0:
        min_p = 1

    return {"max" : {"drops" : {"name": max_d_name, "count": max_d},
                     "pickups" : {"name": max_p_name, "count": max_p}},
            "min" : {"drops" : {"name": min_d_name, "count": min_d},
                     "pickups" : {"name": min_p_name, "count": min_p}}}



def load_precomputed_count(boroughs):
    hoods = {}

    with open('neighborhoods/monary_count.csv') as f:
        for line in f:
            (c, x, y, z) = line.strip().split(", ")

            if int(c) not in boroughs:
                continue

            # handle edge cases for duplicate names
            if str(x) == "Chelsea Staten Island":
                x = "Chelsea, Staten Island"
            if str(x) == "Bay Terrace Staten Island":
                x = "Bay Terrace, Staten Island"

            hoods[str(x)] = {"drops": int(y), "pickups": int(z)}
    return hoods


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Error: need to pass a neighborhoods geojson file")
    nfile = sys.argv[1]
    data = parse_neighborhood_file(nfile)
