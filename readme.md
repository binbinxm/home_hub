# introduction
This repo is running on my home AP server(ubuntu). It will report all my home iot device status to aliyun iot server every 60 seconds, including temperature, humidity(DHT22 on arduino) and smart power switch(sp2).

Reverse control is TBD since nothing needs to be controlled yet.

# usage
Create a keys.py file which contain below message:

```
ProductKey = "xxx"
ClientId = "xxx"  # 自定义clientId
DeviceName = "xxx"
DeviceSecret = "xxx"
```

All above info can be found on my aliyun iot server.

And this file, keys.py, can be found on my private repo as well.
