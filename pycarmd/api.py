import os, logging
import requests
from requests.auth import AuthBase

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

CMD_BASE_URL = 'http://api2.carmd.com/v2.0/'
CMD_DEFAULT_KEY = os.environ.get('CARMD_KEY', None)
CMD_DEFAULT_SECRET = os.environ.get('CARMD_SECRET', None)


class CarmdAuth(AuthBase):
    """
    requests.auth.AuthBase authentication class for CarmdApi.
    """
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def __call__(self, r):
        r.headers['authorization'] = self.key
        r.headers['partner-token'] = self.secret
        return r


class CarmdApi:
    """
    CarMD API: http://dev-developer.carmd.com/v2.0/

    Services Provided:
        - VIN Decode (our primary use case)
        - Safety Recalls
        - Predicted Repair Reports
        - Scheduled Maintenance Reports
        - Vehicle years, makes, and models that exist.
    """
    def __init__(self, key=None, secret=None):
        """
        :param key: (str, default None)
            Also known as 'authorization key'
            Looks like 'Basic eadafacaADWADAWFAXwadawfawgawga='

        :param secret: (str, default None)
            Also known as 'partner-token'
            Looks like XXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX

        """
        if key is None:
            key = CMD_DEFAULT_KEY
        if secret is None:
            secret = CMD_DEFAULT_SECRET
        if not all((key, secret)):
            raise KeyError("This object must be initialized with a key and secret value. "
                           "Alternatively, 'CARMD_KEY' and 'CARMD_SECRET' values can "
                           "be stored/retrieved from the operating system environment.")

        self._key = key
        self._secret = secret
        self._auth = CarmdAuth(key, secret)

    def get(self, service, params=None, **kwargs):
        url = CMD_BASE_URL + service
        kwargs['auth'] = self._auth
        return requests.get(url, params=params, **kwargs)

    def get_decode(self, vin):
        """
        Returns VIN explosion information for a given VIN.

        :param vin: (str)
            The VIN number to be decoded.

        :return: (requests.Response)

            {'data': {'vin': '5XYKTDA26DG338929', 'make': 'KIA', 'model': 'SORENTO',
                      'engineType': 'V6, 3.5L; DOHC; 24V', 'engine': 'V6, 3.5L; DOHC; 24V',
                      'year': 2013, 'aaia': '202996'},
            'message': {'code': 0, 'credentials': 'Valid', 'message': 'OK',
                        'version': 'v2.0.0', 'account': 'Free',
                        'method': 'Decode VIN', 'action': 'GET'}}
        """
        return self.get('decode', params={'vin': vin})

    def get_safety_recall(self, vehicle_id):
        """
        http://dev-developer.carmd.com/v2.0/get-safety-recalls/

        Retrieve a list of safety recalls for a specific vehicle.

        :param vehicle_id:
        :return:
        """
        return self.get('articles/safetyrecall', params={'vehicleID': vehicle_id})

    def get_predicted_repair(self, vehicle_id=None, tag=None, fleet_id=None):
        """
        http://dev-developer.carmd.com/v2.0/get-predicted-repair/

        Get predicted repair reports.
        Predicted repair reports are reports of possible upcoming issues for that vehicle.
        The report contains the likelihood of needing that repair occurring within the next 12 months.

        :param vehicle_id:
        :param tag:
        :param fleet_id:
        :return:
        """
        if vehicle_id is not None:
            params = {'vehicleID': vehicle_id}
        elif tag is not None:
            params = {'tag': tag}
        elif fleet_id is not None:
            params = {'fleetID': fleet_id}
        else:
            raise TypeError("Required paramater missing: "
                            "vehicle_id, tag, or fleet_id")
        return self.get('report/predicted', params=params)

    def get_warranty(self, vehicle_id):
        """
        Returns warranty information about a given vehicle ID.

        {
            "message": {
                "code": 0, "message": "OK",
                "credentials": "Valid", "version": "v2.0.0",
                "account": "Free", "method": "Get Vehicle Warranty",
                "action": "GET", "counter": 247
            },
            "data": [
                {
                    "name": "8 year / 80,000 miles", "desc": "Federal Emissions", "type": 2,
                    "notes": "", "maxMileage": 80000, "maxYear": 8, "isTransferable": true
                },
                {
                    "name": "5 year / 60,000 miles","desc": "Powertrain","type": 1,
                    "notes": "","maxMileage": 60000,"maxYear": 5,"isTransferable": true
                },
                {
                    "name": "3 year / 36,000 miles","desc": "Basic","type": 0,
                    "notes": "","maxMileage": 36000,"maxYear": 3,"isTransferable": true
                }
            ]
        }
        :return:
        """
        return self.get('articles/warranty', params={'vehicleID': vehicle_id})

    def get_maintenance(self, vin, mileage):
        """
        Get next scheduled maintenance items at a mileage and VIN.

        :param vin: (str)
            The target VIN.

        :param mileage: (int, str)
            Current vehicle mileage.

        :return: (requests.Response)
        """
        return self.get('maint/next', params={'vin': vin, 'mileage': str(mileage)})

    def get_years(self, make):
        """
        Retrieves a list of years for a vehicle of a certain make.
        This is a required step for finding the model of a vehicle.

        :param make: (str)
            The vehicle make (e.g. 'Toyota')

        :return: (requests.Response)
        """
        return self.get('decode', params={'make': make})

    def get_makes(self):
        """
        Get a list of vehicle makes, such as Toyota, Ford, etc.
        CarMD service assists in helping find a user’s year/make/model by starting with makes,
        then the service ‘Get vehicle year’, and then ‘Get vehicle model’.

        :return: (requests.Response)
        """
        return self.get('decode')

    def get_models(self, year, make):
        """
        Retrieves a list of models for a vehicle provided the make and year.

        :param year: (int, str)
            The 4-digit year.

        :param make: (str)
            The vehicle make.

        :return:(requests.Response)
        """
        return self.get('decode', params={'year': str(year), 'make': make})
