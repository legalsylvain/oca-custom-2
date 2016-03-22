# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import json
import requests
import urllib

from requests.auth import HTTPBasicAuth

from openerp import models


class GithubConnector(models.AbstractModel):
    _name = 'github.connector'

    def get_from_github(self, url):
        login = '****'
        password = '****'
        response = requests.get(
            url, verify=False, auth=HTTPBasicAuth(login, password))
        return json.loads(response.content)

    # TODO [IMP] move this function in a more core section
    # (or reuse existing one)
    def get_base64_image_from_url(self, url):
        stream = urllib.urlopen(url).read()
        return base64.standard_b64encode(stream)
