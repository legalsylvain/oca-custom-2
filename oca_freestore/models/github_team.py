# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class GithubTeam(models.Model):
    _name = 'github.team'
    _inherit = ['github.connector']

    # Column Section
    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        required=True, select=True, readonly=True)

    name = fields.Char(
        string='Name', select=True, required=True, readonly=True)

    github_id = fields.Integer(
        string='Github ID', required=True, readonly=True)

    github_name = fields.Char(
        string='Github Name', select=True, required=True, readonly=True)

    member_ids = fields.Many2many(
        string='Members', comodel_name='res.partner',
        relation='github_team_partner_rel', column1='team_id',
        column2='partner_id', readonly=True)

    member_qty = fields.Integer(
        string='Members Quantity', compute='compute_member_qty', store=True)

    description = fields.Char(string='Description', readonly=True)

    _sql_constraints = [
        (
            'github_name_uniq', 'unique(github_name)',
            "Two Teams with the same Github Name ? Are you drunk ?")
    ]

    # Compute Section
    @api.multi
    @api.depends('member_ids')
    def compute_member_qty(self):
        for team in self:
            team.member_qty = len(team.member_ids)

    # Custom Section
    def github_2_odoo(self, data):
        return {
            'name': data['name'],
            'github_id': data['id'],
            'github_name': data['slug'],
            'description': data['description'],
        }

    @api.model
    def create_or_update_from_github(self, organization_id, data, full):
        """Create a new team or update an existing one based on github
        datas. Return a team."""
        partner_obj = self.env['res.partner']
        per_page = 100
        team = self.search([('github_name', '=', data['slug'])])

        if team and not full:
            return team

        # Get Full Datas from Github
        odoo_data = self.github_2_odoo(data)
        odoo_data.update({'organization_id': organization_id})
        if not team:
            team = self.create(odoo_data)
        else:
            team.write(odoo_data)

        # Get members
        member_ids = []
        page = 1
        while True:
            datas = self.get_from_github(
                "https://api.github.com/teams/%d/members"
                "?per_page=%d&page=%d" % (
                    team.github_id, per_page, page))
            if datas == []:
                break
            for data in datas:
                partner = partner_obj.create_or_update_from_github(
                    data, False)
                member_ids.append(partner.id)
            if len(datas) < per_page:
                break
            page += 1
        team.member_ids = member_ids

        return team
