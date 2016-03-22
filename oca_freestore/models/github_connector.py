# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import json
import requests
import urllib

from requests.auth import HTTPBasicAuth

from openerp import models, exceptions, _


class GithubConnector(models.AbstractModel):
    _name = 'github.connector'

    def get_data_from_github(self, url):
        login = self.env['ir.config_parameter'].get_param('github.login')
        password = self.env['ir.config_parameter'].get_param('github.password')
        response = requests.get(
            url, verify=False, auth=HTTPBasicAuth(login, password))
        if response.status_code == 401:
            raise exceptions.Warning(
                _("Github Access Error"),
                _("Unable to authenticate to Github with the login '%s'.\n"
                "You should Check your credentials in the Odoo Parameters"
                " Menu.") % (login))
        elif response.status_code != 200:
            raise exceptions.Warning(
                _("Github Error"),
                _("The call to '%s' failed:\n"
                    "- Status Code: %d\n"
                    "- Reason: %s") % (
                    response.url, response.status_code, response.reason))
        return json.loads(response.content)

    # TODO [IMP] move this function in a more core section
    # (or reuse existing one)
    def get_base64_image_from_url(self, url):
        stream = urllib.urlopen(url).read()
        return base64.standard_b64encode(stream)
