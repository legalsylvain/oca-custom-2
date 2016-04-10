# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class GithubUser(models.Model):
    _name = 'github.user'
    _inherit = ['abstract.github.model']
    _order = 'name'

    # Columns Section
    name = fields.Char(
        string='User Name', required=True, readonly=True)

    # Overloadable Section
    def github_type(self):
        return 'user'
