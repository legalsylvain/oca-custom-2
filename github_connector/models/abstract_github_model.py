# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import json
import requests
import urllib
import logging
from datetime import datetime
from requests.auth import HTTPBasicAuth

from openerp import api, fields, models, exceptions, _

_logger = logging.getLogger(__name__)

_MAX_NUMBER_REQUEST = 30

_BASE_URL = 'https://api.github.com/'

_GITHUB_TYPE = [
    ('organization', 'Organization'),
    ('repository', 'Repository'),
    ('user', 'User'),
]

_GITHUB_TYPE_URL = {
    'organization': {'url': 'orgs/%s', 'url_by_id': 'organizations/%s'},
    'user': {'url': 'users/%s', 'url_by_id': 'user/%s'},
    'repository': {'url': 'repos/%s', 'url_by_id': 'repositories/%s'},
    'team': {'url_by_id': 'teams/%s'},
    'issue': {'url': 'repos/%s/issues/%s'},
    'organization_members': {'url': 'orgs/%s/members'},
    'organization_repositories': {'url': 'orgs/%s/repos'},
    'organization_teams': {'url': 'orgs/%s/teams'},
    'team_members': {'url': 'teams/%s/members'},
    'repository_issues': {'url': 'repos/%s/issues?state=all'},
    'issue_comments': {'url': 'repos/%s/issues/%s/comments'},
    #    'repository_branches': {'url': 'repos/%s/branches', 'max': 100},
}

"""

This abstract model is used to share all features related to github model.
Note that some fields and function have to be defined in the inherited model.
(github_type for instance)

"""


class AbtractGithubModel(models.AbstractModel):
    _name = 'abstract.github.model'
    _github_type = None
    _github_login_field = None
    _need_individual_call = False

    github_id = fields.Char(
        string='Github Id', readonly=True, select=True)

    github_login = fields.Char(
        string='Github Technical Name', readonly=True, select=True)

    github_url = fields.Char(
        string='Github URL', readonly=True)

    github_create_date = fields.Datetime(
        string='Create Date on Github', readonly=True)

    github_write_date = fields.Datetime(
        string='Last Write Date on Github', readonly=True)

    github_last_sync_date = fields.Datetime(
        string='Last Sync Date with Github', readonly=True)

    # Overloadable Section
    def github_type(self):
        if self._github_type is None:
            raise exceptions.Warning(
                _("Unimplemented Feature"),
                _("Please define github_type function in child model."))
        else:
            return self._github_type

    def github_login_field(self):
        if self._github_login_field is None:
            raise exceptions.Warning(
                _("Unimplemented Feature"),
                _("Please define github_login_field function in child model."))
        else:
            return self._github_login_field

    @api.model
    def get_odoo_data_from_github(self, data):
        return {
            'github_id': data['id'],
            'github_url': data.get('html_url', False),
            'github_login': data.get(self.github_login_field(), False),
            'github_create_date': data.get('created_at', False),
            'github_write_date': data.get('updated_at', False),
            'github_last_sync_date':
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    @api.multi
    def full_update(self):
        pass

    # Custom Public Function
    @api.model
    def get_from_id_or_create(self, data, extra_data={}):
        """Search if the odoo object exists in database. If yes, returns the
            object. Otherwise, creates the new object.

            :param data: dict with github 'id' and 'url' keys
            :return: The searched or created object

            :Example:

            >>> self.env['github_organization'].get_from_id_or_create(
                {'id': 7600578, 'url': 'https://api.github.com/orgs/OCA'})
        """
        res = self.search([('github_id', '=', data['id'])])
        if not res:
            if self._need_individual_call:
                data = self._get_data_from_github_url(data['url'])
            return self._create_from_github_data(data, extra_data)
        else:
            return res

    @api.model
    def create_from_name(self, name):
        """Call Github API, using a url using github name. Load data and
            Create Odoo object accordingly, if the odoo object doesn't exist.

            :param name: the github name to load
            :return: The created object

            :Example:

            >>> self.env['github_organization'].create_from_name('OCA')
            >>> self.env['github_repository'].create_from_name('OCA/web')
        """
        res = self._get_data_from_github(self.github_type(), [name])
        # search if ID doesn't exist in database
        current_object = self.search([('github_id', '=', res['id'])])
        if not current_object:
            # Create the object
            return self._create_from_github_data(res)
        else:
            # Manage the special case when the name changed...
            # TODO
            pass

    def get_datalist_from_github(self, github_type, arguments):
        page = 1
        datas = []
        while True:
            pending_datas = self._get_data_from_github(
                github_type, arguments, False, page)
            datas += pending_datas
            if pending_datas == [] or\
                    len(pending_datas) < _MAX_NUMBER_REQUEST:
                break
            page += 1
        return datas

    @api.multi
    def button_update_from_github_light(self):
        return self.update_from_github(False)

    @api.multi
    def button_update_from_github_full(self):
        return self.update_from_github(True)

    @api.multi
    def update_from_github(self, child_update):
        """Call Github API, using a url using github id. Load data and
            update Odoo object accordingly, if the odoo object is obsolete.
            (Based on last write dates)

            :param child_update: set to True if you want to reload childs
                Objects linked to this object. (like members for teams)
        """
        for item in self:
            if item._model._name == 'github.issue':
                # This Hack is not very beautiful
                # Github doesn't provides api to load a issue, by issue id
                # TODO Refactor me.
                res = self._get_data_from_github(
                    item.github_type(),
                    [item.repository_id.github_login, item.github_login])
            else:
                res = self._get_data_from_github(
                    item.github_type(), [item.github_id], by_id=True)
            item._update_from_github_data(res)
        if child_update:
            self.full_update()

    def get_base64_image_from_github(self, url):
        stream = urllib.urlopen(url).read()
        return base64.standard_b64encode(stream)

    # Custom Private Function
    @api.model
    def _create_from_github_data(self, data, extra_data={}):
        vals = self.get_odoo_data_from_github(data)
        vals.update(extra_data)
        return self.create(vals)

    @api.multi
    def _update_from_github_data(self, data):
        for item in self:
            # TODO Check on dates.
            vals = self.get_odoo_data_from_github(data)
            return item.write(vals)

    @api.model
    def _get_data_from_github_url(self, url):
        _logger.info("Calling %s" % (url))
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

    def _get_data_from_github(
            self, github_type, arguments, by_id=False, page=None):
        # TODO Refactor me
        url = self._get_url(github_type, arguments, by_id, page)
        return self._get_data_from_github_url(url)

    def _get_url(self, github_type, arguments, by_id, page):
        if by_id:
            url = _GITHUB_TYPE_URL[github_type]['url_by_id']
        else:
            url = _GITHUB_TYPE_URL[github_type]['url']
        if github_type not in _GITHUB_TYPE_URL.keys():
            raise exceptions.Warning(
                _("Unimplemented Connection"),
                _("'%s' is not implemented.") % (github_type))
        complete_url = _BASE_URL + url % tuple(arguments)

        if page:
            complete_url += ('?' in complete_url and '&' or '?') +\
                'per_page=%d&page=%d' % (_MAX_NUMBER_REQUEST, page)
        return complete_url
