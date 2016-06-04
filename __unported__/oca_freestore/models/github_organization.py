# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class GithubOrganization(models.Model):
    _name = 'github.organization'
    _inherit = ['github.connector']
    _order = 'name'

    # Columns Section
    name = fields.Char(string='Organization Name', required=True)

    billing_email = fields.Char(string='Billing Email', readonly=True)

    image = fields.Binary(string='Image', readonly=True)

    github_login = fields.Char(
        string='Github Name', required=True, help="The technical name of"
        " your organization on github.\n\nShould be organization_name if the"
        " url of your organization is https://github.com/organization_name/")

    description = fields.Char(string='Description', readonly=True)

    email = fields.Char(string='Email', readonly=True)

    website_url = fields.Char(string='Website URL', readonly=True)

    location = fields.Char(string='Location', readonly=True)

    public_member_ids = fields.Many2many(
        string='Members', comodel_name='res.partner',
        relation='github_organization_partner_rel', column1='organization_id',
        column2='partner_id', readonly=True)

    public_member_qty = fields.Integer(
        string='Members Quantity', compute='compute_public_member_qty',
        store=True)

    repository_ids = fields.Many2many(
        string='Repositories', comodel_name='github.repository',
        relation='github_organization_repository_rel',
        column1='organization_id', column2='repository_id', readonly=True)

    repository_qty = fields.Integer(
        string='Repositories Quantity', compute='compute_repository_qty',
        store=True)

    organization_serie_ids = fields.One2many(
        string='Organization Series',
        comodel_name='github.organization.serie',
        inverse_name='organization_id')

    ignore_repository_names = fields.Text(
        string='Ignored Repositories', help="Set here repository names you"
        " you want to ignore. One repository per line. Exemple:\n"
        "odoo-community.org\n"
        "OpenUpgrade\n")

    # Compute Section
    @api.multi
    @api.depends('public_member_ids')
    def compute_public_member_qty(self):
        for organization in self:
            organization.public_member_qty =\
                len(organization.public_member_ids)

    @api.multi
    @api.depends('repository_ids', 'repository_ids.organization_id')
    def compute_repository_qty(self):
        for organization in self:
            organization.repository_qty =\
                len(organization.repository_ids)

    # Custom Section
    def github_2_odoo(self, data):
        return {
            'name': data['name'],
            'description': data['description'],
            'location': data['location'],
            'website_url': data['blog'],
            'email': data['email'],
            'billing_email': data['billing_email'],
            'image': self.get_base64_image_from_github(data['avatar_url']),
        }

    # Action Section
    @api.multi
    def button_full_synchronize(self):
        return self.button_synchronize(True)

    @api.multi
    def button_light_synchronize(self):
        return self.button_synchronize(False)

    @api.multi
    def button_synchronize(self, full):
        partner_obj = self.env['res.partner']
        repository_obj = self.env['github.repository']
        team_obj = self.env['github.team']

        for organization in self:

            # Get organization data
            data = self.get_data_from_github(
                'organization', [organization.github_login])
            organization.write(self.github_2_odoo(data))

            # Get Members datas
            member_ids = []
            for data in self.get_datalist_from_github(
                    'organization_members', [organization.github_login]):
                partner = partner_obj.create_or_update_from_github(data, full)
                member_ids.append(partner.id)
            organization.public_member_ids = member_ids

            # Get Repositories datas
            repository_ids = []
            ignored_list = organization.ignore_repository_names and\
                organization.ignore_repository_names.split("\n") or []
            for data in self.get_datalist_from_github(
                    'organization_repositories', [organization.github_login]):
                if data['name'] not in ignored_list:
                    repository = repository_obj.create_or_update_from_github(
                        organization.id, data, full)
                    repository_ids.append(repository.id)
            organization.repository_ids = repository_ids

            # Get Teams datas
            team_ids = []
            for data in self.get_datalist_from_github(
                    'organization_teams', [organization.github_login]):
                team = team_obj.create_or_update_from_github(
                    organization.id, data, full)
                team_ids.append(team.id)
            organization.team_ids = team_ids
