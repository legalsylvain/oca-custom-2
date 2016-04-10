# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions, _


class GithubIssue(models.AbstractModel):
    _name = 'github.issue'
    _inherit = ['abstract.github.model']

    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository', readonly=True,
        required=True)

    issue_type = fields.Selection(
        selection=[('issue', 'Issue'), ('pull_request', 'Pull Request')],
        string='Type')

    title = fields.Char(string='Title', readonly=True, required=True)

    body = fields.Char(string='Body', readonly=True, required=True)

    author_id = fields.Many2one(
        comodel_name='res.partner', string='Author', readonly=True,
        required=True)

     Overloadable Section
    def github_type(self):
        return 'issue'

    def github_login_field(self):
        return 'number'

    def get_odoo_data_from_github(self, data):
        repository_obj = self.env['github.repository']
        partner_obj = self.env['res.partner']
        res = super(GithubIssue, self).get_odoo_data_from_github(data)
        organization = organization_obj.get_from_id_or_create(
            data['repository'])
        partner = organization_obj.get_from_id_or_create(
            data['user'])
        res.update({
            'github_id': data['id'],
            'title': data['title'],
            'body': data['body'],
            'author_id': partner.id,
            'repository_id': repository.id,
            'type': data.get('pull_request', False)
                and 'pull_request' or 'issue',
        })
        return res

    @api.multi
    def full_update(self):
        # TODO Load comment
        pass
#        self.button_sync_member()
