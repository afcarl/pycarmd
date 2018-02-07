# pycarmd
This program is a Python implementation of (most) CarMD API services. 

http://dev-developer.carmd.com/v2.0/

Accessing the API
--------------
    from pycarmd import CarmdApi
    api = CarmdApi()

Decoding a VIN
--------------
    res = api.get_decode('VINNUMBER02XY')
    data = res.json()['data']

Getting all Vehicle Makes
-------------------------
    res = api.get_makes()
    data = res.json()['data']

Getting all Vehicle Models
--------------------------
    res = api.get_models(2010, 'Toyota')
    models = res.json()['data']



