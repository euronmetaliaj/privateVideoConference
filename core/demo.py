host = "http://localhost:5000/api/"

import requests

request = requests.post(host, json={"username": "euron", "password": "monitori", "check_client_state": "True",
                                    "scard_no": "4651-6531-6313-5"})
