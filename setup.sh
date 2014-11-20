#! /bin/bash

sigint() {
    echo "exiting..."
    exit 1
}
trap 'sigint' SIGINT

killall mongod
rm -rf ./data
mkdir -p ./data/db
mongod --dbpath ./data/db/ --logpath ./data/log --fork

FILES=taxi/*
for f in $FILES
do
    echo "loading from " $f
    python loader.py $f
done
mongo localhost:27017/taxi --eval "printjson(db.both.ensureIndex({distance:1}))"
mongo localhost:27017/taxi --eval "printjson(db.pickup.ensureIndex({distance:1}))"
mongo localhost:27017/taxi --eval "printjson(db.drop.ensureIndex({distance:1}))"
