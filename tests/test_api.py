from pycarmd.api import CarmdApi

VIN_KIA_SORENTO = '5XYKTDA26DG338929'


def test_carmd_decode_vin():
    api = CarmdApi()
    res = api.get_decode(VIN_KIA_SORENTO)
    data = res.json()['data']
    year = data['year']
    make = data['make']
    model = data['model']
    assert year == 2013
    assert make == 'KIA'
    assert model == 'SORENTO'


def test_carmd_get_maintenance():
    api = CarmdApi()
    res2 = api.get_maintenance(VIN_KIA_SORENTO, 25350)
    data = res2.json()['data']
    for item in data:
        print(item)
        print("\n")