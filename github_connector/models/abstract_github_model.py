# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import base64
import json
import requests
import urllib
import logging

from requests.auth import HTTPBasicAuth
#from requests.packages.urllib3.exceptions import InsecureRequestWarning

from openerp import api, fields, models, exceptions, _

_logger = logging.getLogger(__name__)

### Disable log of Insecure call to HTTPS website
### TODO FIXME.
##requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

### Disable useless requests log
##logging.getLogger("requests").setLevel(logging.WARNING)

_MAX_NUMBER_REQUEST = 30

_BASE_URL = 'https://api.github.com/'

_GITHUB_TYPE = [
    ('organization', 'Organization'),
    ('repository', 'Repository'),
    ('user', 'User'),
]

#Use the endpoint: https://api.github.com/user/:id, where :id is the ID of the user.

#Similar endpoints exist for repos and orgs, at https://api.github.com/repositories/:id and https://api.github.com/organizations/:id respectively.

_GITHUB_TYPE_URL = {
    'organization': {'url': 'orgs/%s', 'url_by_id': 'organizations/%s'},
    'user': {'url': 'users/%s', 'url_by_id': 'user/%s'},
    'repository': {'url': 'repos/%s', 'url_by_id': 'repositories/%s'},
#    'organization_members': {'url': 'orgs/%s/members', 'max': 100},
#    'organization_repositories': {'url': 'orgs/%s/repos', 'max': 100},
#    'organization_teams': {'url': 'orgs/%s/teams', 'max': 30},

#    'repository_branches': {'url': 'repos/%s/branches', 'max': 100},
#    'team_members': {'url': 'teams/%d/members', 'max': 100},
#    'repository_issues': {'url': 'repos/%s/issues', 'max': 100},
}


class AbtractGithubModel(models.AbstractModel):
    _name = 'abstract.github.model'

    github_id = fields.Char(
        string='Github Id', readonly=True)

    github_login = fields.Char(
        string='Github login', readonly=True)

    github_url = fields.Char(
        string='Github URL', readonly=True)

    github_create_date = fields.Datetime(
        string='Create Date on Github', readonly=True)

    github_write_date = fields.Datetime(
        string='Last Write Date on Github', readonly=True)

    github_last_sync_date = fields.Datetime(
        string='Last Sync Date with Github', readonly=True)

    # Constraints Section
    _sql_constraints = [(
            'github_login_uniq', 'unique(github_login)',
            "Two objects with the same Github Login ?"
            " I can't believe it !")]

    # Overloadable Section
    def github_type(self):
        raise exceptions.Warning(
            _("Unimplemented Feature"),
            _("Please define github_type function in child model."))

    def github_login_field(self):
        raise exceptions.Warning(
            _("Unimplemented Feature"),
            _("Please define github_login_field function in child model."))

    @api.model
    def get_odoo_data_from_github(self, data):
        return {
            'github_id': data['id'],
            'github_url': data['html_url'],
            'github_login': data[self.github_login_field()],
            'github_create_date': data['created_at'],
            'github_write_date': data['updated_at'],
            'github_last_sync_date':
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            
        }

    # Custom Public Function
    @api.model
    def get_from_id_or_create(self, github_id, github_name):
        res = self.search([('github_id', '=', 'github_id')])
        if not res:
            return self.create_from_name(github_name)
        else:
            return res

    @api.model
    def create_from_name(self, name):
        res = self._get_data_from_github([name], self.github_type())
        # search if ID doesn't exist in database
        current_object = self.search([('github_id', '=', res['id'])])
        if not current_object:
            # Create the object
            return self._create_from_github_data(res)
        else:
            # Manage the special case when the name changed...
            # TODO
            pass

    @api.multi
    def update_from_github(self):
        for item in self:
            res = self._get_data_from_github(
                [self.github_id], self.github_type(), by_id=True)
            item._update_from_github_data(res)

    def get_base64_image_from_github(self, url):
        stream = urllib.urlopen(url).read()
        return base64.standard_b64encode(stream)

    # Custom Private Function
    @api.model
    def _create_from_github_data(self, data):
        vals = self.get_odoo_data_from_github(data)
        return self.create(vals)

    @api.multi
    def _update_from_github_data(self, data):
        for item in self:
            # TODO Check on dates.
            vals = self.get_odoo_data_from_github(data)
            print vals
            return item.write(vals)


    def _get_url(self, github_type, arguments, by_id, page):
        if by_id:
            url = _GITHUB_TYPE_URL[github_type]['url_by_id']
        else:
            url = _GITHUB_TYPE_URL[github_type]['url']
        if github_type not in _GITHUB_TYPE_URL.keys():
            raise exceptions.Warning(
                _("Unimplemented Connection"),
                _("'%s' is not implemented.") % (github_type))
        if not page:
            return _BASE_URL + url % tuple(arguments)
        else:
            return _BASE_URL + (url + '?per_page=%d&page=%d') % (
                    tuple(arguments) + (_MAX_NUMBER_REQUEST, page))

    def _get_data_from_github(
            self, arguments, github_type, by_id=False, page=None):
        login = self.env['ir.config_parameter'].get_param('github.login')
        password = self.env['ir.config_parameter'].get_param('github.password')
        url = self._get_url(github_type, arguments, by_id, page)
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




##    def _get_local_path(self, repository_branch_complete_name):
##        path = self.env['ir.config_parameter'].get_param('github.local_path')
##        return path + repository_branch_complete_name



##"%(base_url)s" % {'base_url': 'coucou'}


##    def get_datalist_from_github(self, type, arguments):
##        page = 1
##        datas = []
##        while True:
##            pending_datas = self.get_data_from_github(type, arguments, page)
##            datas += pending_datas
##            if pending_datas == [] or\
##                    len(pending_datas) < self._TYPE_KEYS[type]['max']:
##                break
##            page += 1
##        return datas


