# Festival
API for delivering data processed by EUBra-BIGSEA ML models

#### Using docker
Build the container
```
docker build -t bigsea/festival .
```
Repeat [config](#config) stop and run using config file
```
docker run \
  -v $PWD/conf/festival-config.yaml:/usr/local/festival/conf/festival-config.yaml \
  -p 3329:3329\
  bigsea/festival
```
