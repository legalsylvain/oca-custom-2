# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api

from .tools import get_from_github, get_base64_image_from_url


class GithubRepositoryBranch(models.Model):
    _name = 'github.repository.branch'

    # Column Section
    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository',
        select=True, readonly=True)

    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Repository',
        related='repository_id.organization_id', store=True,
        readonly=True)

    name = fields.Char(
        string='Name', select=True, required=True, readonly=True)

    complete_name = fields.Char(
        string='Complete Name', compute='compute_complete_name')


    # Compute Section
    @api.multi
    @api.depends('name', 'repository_id.complete_name')
    def compute_complete_name(self):
        for repository_branch in self:
            repository_branch.complete_name =\
                repository_branch.repository_id.complete_name +\
                '/' + repository_branch.name

    # Custom Section
    def create_or_update_from_name(self, repository_id, name):
        repository_branch = self.search([
            ('name', '=', name), ('repository_id', '=', repository_id)])
        if not repository_branch:
            repository_branch = self.create({
                'name': name,
                'repository_id': repository_id})
        return repository_branch
