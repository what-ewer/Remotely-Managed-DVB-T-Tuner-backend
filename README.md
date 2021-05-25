# Zdalnie zarządzany tuner telewizji cyfrowej - backend 

## Database Scheme
![db-scheme](documentation/dbscheme.png)



## Endpoints

Currently avalible + planned endpoints
| endpoint                  | type  | description                                   | implemented   
| -                         | -     | -                                             |  -    
| **tuner endpoints**       |       |                                               |         
| `/tuner/hearbeat?id=_`    | POST  | post information about tuner                  | ❌
| `/tuner/settings?id=_`    | GET   | get settings list for tuner                   | ❌
| `/tuner/orders?id=_`      | GET   | get a list of orders for tuner                | ✅
| `/tuner/recorded?id=_`    | POST  | get a list of already recorded show for tuner | ❌
| `/tuner/epd?id=_`         | POST  | post EPG of a tuner                           | ❌
| `/tuner/channels?id=_`    | POST  | post channels of a tuner                      | ❌
| **client endpoints**      |       |                                               | 
| `/client/heartbeat?id=_`  | GET   | get information about tuner                   | ❌
| `/tuner/orders?id=_`      | POST  | post orders for a tuner                       | ❌
| `/tuner/channels?id=_`    | GET   | get channels from a tuner                     | ❌
| **other endpoints**       |       |                                               |         
| `/generate/tables`        | GET   | generate tables for database                  | ✅
| `/generate/data`          | GET   | generate some example data for database       | ✅