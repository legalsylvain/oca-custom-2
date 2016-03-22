# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'github.connector']

    # Column Section
    github_login = fields.Char(string='Github Login', select=True)

    has_github_account = fields.Boolean(
        compute='compute_has_github_account',
        string='Has Github Account', select=True, store=True, readonly=True)

    team_ids = fields.Many2many(
        string='Teams', comodel_name='github.team',
        relation='github_team_partner_rel', column1='partner_id',
        column2='team_id', readonly=True)

    # Constraints Section
    _sql_constraints = [
        (
            'github_login_uniq', 'unique(github_login)',
            "Two partners with the same Github Login ?"
            " Dude, it is impossible !")
    ]

    # Compute Section
    @api.depends('github_login')
    @api.multi
    def compute_has_github_account(self):
        for partner in self:
            partner.has_github_account = (partner.github_login is not False)

    # Custom Section
    def github_2_odoo(self, data):
        return {
            'name':
                data['name'] and data['name'] or
                '%s (Github)' % data['login'],
            'github_login': data['login'],
            'website': data['blog'],
            'email': data['email'],
            'image': self.get_base64_image_from_url(data['avatar_url']),
        }

    # Custom Section
    @api.model
    def create_or_update_from_github(self, data, full):
        """Create a new partner or update an existing one based on github
        datas. Return a partner."""
        partner = self.search([('github_login', '=', data['login'])])
        if partner and not full:
            return partner

        # Get Full Datas from Github
        odoo_data = self.github_2_odoo(self.get_from_github(
            'https://api.github.com/users/%s' % (data['login'])))

        if not partner:
            partner = self.create(odoo_data)
        else:
            partner.write(odoo_data)
        return partner
