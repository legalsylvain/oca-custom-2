# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import urllib
from datetime import datetime

from openerp import api, fields, models, exceptions, _
from .github import Github


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
                github_model = self.get_github_for(self.github_type())
                data = github_model.get_by_url(data['url'])
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
        github_model = self.get_github_for(self.github_type())
        res = github_model.get([name])
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
        github_model = self.get_github_for(self.github_type())
        for item in self:
            if item._model._name == 'github.issue':
                # This Hack is not very beautiful
                # Github doesn't provides api to load a issue, by issue id
                # TODO Refactor me.
                res = github_model.get(
                    [item.repository_id.github_login, item.github_login])
            else:
                res = github_model.get([item.github_id], by_id=True)
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

    @api.multi
    def get_github_for(self, github_type):
        return Github(
            github_type,
            self.env['ir.config_parameter'].get_param('github.login'),
            self.env['ir.config_parameter'].get_param('github.password'))
