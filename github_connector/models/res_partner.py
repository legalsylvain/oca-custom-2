# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'abstract.github.model']

    _github_type = 'user'
    _github_login_field = 'login'

    # Column Section
    team_ids = fields.Many2many(
        string='Teams', comodel_name='github.team',
        relation='github_team_partner_rel', column1='partner_id',
        column2='team_id', readonly=True)

    team_qty = fields.Integer(
        string='Teams Quantity', compute='_compute_team_qty', store=True)

    # Constraints Section
    _sql_constraints = [
        (
            'github_login_uniq', 'unique(github_login)',
            "Two partners with the same Github Login ?"
            " Dude, it is impossible !")
    ]

    # Compute Section
    @api.multi
    @api.depends('team_ids', 'team_ids.member_ids')
    def _compute_team_qty(self):
        for partner in self:
            partner.team_qty = len(partner.team_ids)

    # Overloadable Section
    @api.model
    def get_odoo_data_from_github(self, data):
        res = super(ResPartner, self).get_odoo_data_from_github(data)
        res.update({
            'name':
            data['name'] and data['name'] or
            '%s (Github)' % data['login'],
            'website': data['blog'],
            'email': data['email'],
            'image': self.get_base64_image_from_github(data['avatar_url']),
        })
        return res
