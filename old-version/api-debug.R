# Plumber

library(plumber)

setwd('~/1. Projects/3. RProject/PlumbeR/')

pr <- plumb('api-build.R')
# pr$run(host = '0.0.0.0', port = 8080, swagger = F)

# Running at:
# http://192.168.0.184:8080/PLD
# http://192.168.0.139:8080/PLD
# http://172.20.10.6:8080/PLD


# plumb(file='api-build-v2.R')$run(port = 8608, swagger = F)
# curl -X POST "http://192.168.0.184:8080/upload_file" -H "accept: */*" -H "Content-Type: multipart/form-data" -F "req=@Senior.zip;type=application/x-zip-compressed"





