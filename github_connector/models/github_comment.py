# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions, _


class GithubComment(models.Model):
    _name = 'github.comment'
    _inherit = ['abstract.github.model']

    issue_id = fields.Many2one(
        comodel_name='github.issue', string='Issue / PR', readonly=True,
        required=True, ondelete='cascade')

    body = fields.Char(string='Body', readonly=True)

    author_id = fields.Many2one(
        comodel_name='res.partner', string='Author', readonly=True,
        required=True)

    # Overloadable Section
    def github_type(self):
        return 'issue'

    def github_login_field(self):
        return False

    def get_odoo_data_from_github(self, data):
        partner_obj = self.env['res.partner']
        res = super(GithubComment, self).get_odoo_data_from_github(data)
        partner = partner_obj.get_from_id_or_create(
            data['user'])
        res.update({
            'body': data['body'],
            'author_id': partner.id,
        })
        return res
