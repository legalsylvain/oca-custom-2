# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class GithubRepository(models.Model):
    _name = 'github.repository.branch'
    _inherit = ['abstract.github.model']

    _github_type = 'repository_branches'
    _github_login_field = False

    # Column Section
    name = fields.Char(
        string='Name', readonly=True, select=True)

    complete_name = fields.Char(
        string='Complete Name', store=True, compute='_compute_complete_name')

    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository',
        required=True, select=True, readonly=True, ondelete='cascade')

    # Custom
    def create_or_update_from_name(self, repository_id, name):
        branch = self.search([
            ('name', '=', name), ('repository_id', '=', repository_id)])
        if not branch:
            branch = self.create({
                'name': name, 'repository_id': repository_id})
        return branch

    # Compute Section
    @api.multi
    @api.depends('name', 'repository_id.name')
    def _compute_complete_name(self):
        for branch in self:
            branch.complete_name =\
                branch.repository_id.name + '/' + branch.name
