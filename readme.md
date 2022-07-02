```
docker image pull ghcr.io/gaussmeter/lumen:1.0.1
docker container run --detach --publish 9000:9000 --name lumen --privileged ghcr.io/gaussmeter/lumen:1.0.1
./loop.sh
docker container rm -f lumen
```