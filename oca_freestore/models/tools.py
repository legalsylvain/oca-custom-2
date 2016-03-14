# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import json
import requests
import urllib
import cStringIO

from requests.auth import HTTPDigestAuth
from requests.auth import HTTPBasicAuth

def get_from_github(url):
    print ">>>>>>>>>>>>>>>>>"
    print url
    response = requests.get(
        url, verify=False,
        auth=HTTPBasicAuth('*****', '*****'))
    return json.loads(response.content)

def get_base64_image_from_url(url):
    stream = urllib.urlopen(url).read()
    return base64.standard_b64encode(stream)
