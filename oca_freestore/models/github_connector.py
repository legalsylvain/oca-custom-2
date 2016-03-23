# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import json
import requests
import urllib
import logging

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from openerp import models, exceptions, _

_logger = logging.getLogger(__name__)

# Disable log of Insecure call to HTTPS website
# TODO FIXME.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Disable useless requests log
logging.getLogger("requests").setLevel(logging.WARNING)


class GithubConnector(models.AbstractModel):
    _name = 'github.connector'

    _BASE = 'https://api.github.com/'

    _TYPE_KEYS = {
        'organization': {'url': 'orgs/%s'},
        'organization_members': {'url': 'orgs/%s/members', 'max': 100},
        'organization_repositories': {'url': 'orgs/%s/repos', 'max': 100},
        'organization_teams': {'url': 'orgs/%s/teams', 'max': 30},
        'user': {'url': 'users/%s'},
        'repository': {'url': 'repos/%s'},
        'repository_branches': {'url': 'repos/%s/branches', 'max': 100},
        'team_members': {'url': 'teams/%d/members', 'max': 100},
    }

    def _get_local_path(self, repository_branch_complete_name):
        path = self.env['ir.config_parameter'].get_param('github.local_path')
        return path + repository_branch_complete_name

    def _get_url(self, type, arguments, page):
        if type not in self._TYPE_KEYS:
            raise exceptions.Warning(
                _("Unimplemented Connection"),
                _("'%s' is not implemented.") % (type))
        if not page:
            return self._BASE + self._TYPE_KEYS[type]['url'] % tuple(arguments)
        else:
            return self._BASE +\
                (self._TYPE_KEYS[type]['url'] + '?per_page=%d&page=%d') % (
                    tuple(arguments) + (self._TYPE_KEYS[type]['max'], page,))

    def get_data_from_github(self, type, arguments, page=None):
        url = self._get_url(type, arguments, page)
        login = self.env['ir.config_parameter'].get_param('github.login')
        password = self.env['ir.config_parameter'].get_param('github.password')
        _logger.info("Calling %s" % (url))
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

    def get_datalist_from_github(self, type, arguments):
        page = 1
        datas = []
        while True:
            pending_datas = self.get_data_from_github(type, arguments, page)
            datas += pending_datas
            if pending_datas == [] or\
                    len(pending_datas) < self._TYPE_KEYS[type]['max']:
                break
            page += 1
        return datas

    def get_base64_image_from_github(self, url):
        stream = urllib.urlopen(url).read()
        return base64.standard_b64encode(stream)
