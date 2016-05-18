# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class GithubRepository(models.Model):
    _name = 'github.repository'
    _inherit = ['abstract.github.model']
    _order = 'organization_id, name'

    _github_type = 'repository'
    _github_login_field = 'full_name'

    # Column Section
    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        required=True, select=True, readonly=True, ondelete='cascade')

    name = fields.Char(
        string='Name', select=True, required=True, readonly=True)

    description = fields.Char(string='Description', readonly=True)

    website = fields.Char(string='Website', readonly=True)

    issue_ids = fields.One2many(
        string='Issues + PR', comodel_name='github.issue',
        inverse_name='repository_id', readonly=True)

    issue_qty = fields.Integer(
        string='Issue + PR Quantity', compute='_compute_issue_qty',
        multi='issue', store=True)

    open_issue_qty = fields.Integer(
        string='Open Issue + PR Quantity', compute='_compute_issue_qty',
        multi='issue', store=True)

    only_issue_qty = fields.Integer(
        string='Issue Quantity', compute='_compute_issue_qty',
        multi='issue', store=True)

    only_open_issue_qty = fields.Integer(
        string='Open Issue Quantity', compute='_compute_issue_qty',
        multi='issue', store=True)

    only_pull_request_qty = fields.Integer(
        string='PR Quantity', compute='_compute_issue_qty',
        multi='issue', store=True)

    only_open_pull_request_qty = fields.Integer(
        string='Open PR Quantity', compute='_compute_issue_qty',
        multi='issue', store=True)

    # Compute Section
    @api.multi
    @api.depends('issue_ids.repository_id')
    def _compute_issue_qty(self):
        for repository in self:
            only_issue_qty = 0
            only_open_issue_qty = 0
            only_pull_request_qty = 0
            only_open_pull_request_qty = 0
            for issue in repository.issue_ids:
                if issue.issue_type == 'issue':
                    only_issue_qty += 1
                    if issue.state == 'open':
                        only_open_issue_qty += 1
                else:
                    only_pull_request_qty += 1
                    if issue.state == 'open':
                        only_open_pull_request_qty += 1
            repository.only_issue_qty = only_issue_qty
            repository.only_open_issue_qty = only_open_issue_qty
            repository.only_pull_request_qty = only_pull_request_qty
            repository.only_open_pull_request_qty = only_open_pull_request_qty
            repository.issue_qty = only_issue_qty + only_pull_request_qty
            repository.open_issue_qty =\
                only_open_issue_qty + only_open_pull_request_qty

    # Overloadable Section
    @api.model
    def get_odoo_data_from_github(self, data):
        organization_obj = self.env['github.organization']
        res = super(GithubRepository, self).get_odoo_data_from_github(data)
        organization = organization_obj.get_from_id_or_create(data['owner'])
        res.update({
            'name': data['name'],
            'github_url': data['url'],
            'description': data['description'],
            'website': data['homepage'],
            'organization_id': organization.id,
        })
        return res

    @api.multi
    def full_update(self):
        self.button_sync_issue()

    # Action section
    @api.multi
    def button_sync_issue(self):
        issue_obj = self.env['github.issue']
        for repository in self:
            issue_ids = []
            for data in self.get_datalist_from_github(
                    'repository_issues', [repository.github_login]):
                issue = issue_obj.get_from_id_or_create(
                    data, {'repository_id': repository.id})
                issue_ids.append(issue.id)
            repository.issue_ids = issue_ids

    # Action section
    @api.multi
    def button_sync_issue_with_comment(self):
        self.button_sync_issue()
        for repository in self:
            repository.issue_ids.button_sync_comment()
