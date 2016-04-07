# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class GithubRepository(models.Model):
    _name = 'github.repository'
    _inherit = ['github.connector']
    _order = 'organization_id, name'

    # Column Section
    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        required=True, select=True, readonly=True, ondelete='cascade')

    name = fields.Char(
        string='Name', select=True, required=True, readonly=True)

    complete_name = fields.Char(
        string='Complete Name', select=True, required=True, readonly=True)

    description = fields.Char(string='Description', readonly=True)

    website = fields.Char(string='Website', readonly=True)

    github_url = fields.Char(string='Github URL', readonly=True)

    repository_branch_ids = fields.One2many(
        comodel_name='github.repository.branch',
        inverse_name='repository_id', string='Branches', readonly=True)

    # Constraint Section
    _sql_constraints = [
        (
            'complete_name_uniq', 'unique(complete_name)',
            "Two Projects with the same Complete Name ? I don't think so.")
    ]

    # Action Section
    @api.multi
    def button_analyze_issue(self):
        return self._analyze_issue()

    # Custom Section
    def github_2_odoo(self, data):
        return {
            'name': data['name'],
            'complete_name': data['full_name'],
            'github_url': data['url'],
            'website': data['homepage'],
            'description': data['description'],
        }



    @api.multi
    def _analyze_issue(self):
        for repository in self:
####            # Delete all issues versions # TODO
####            module_versions = module_version_obj.search([
####                ('repository_branch_id', '=', repository_branch.id)])
####            module_versions.with_context(
####                dont_change_repository_branch_state=True).unlink()

####            # Delete all pull requests # TODO
####            git_commits = git_commit_obj.search([
####                ('repository_branch_id', '=', repository_branch.id)])
####            git_commits.with_context(
####                dont_change_repository_branch_state=True).unlink()
            abstract_issue_obj = self.env['github.abstract.issue']

            # Get Issues datas
            issue_ids = []
            for data in self.get_datalist_from_github(
                    'repository_issues', [repository.complete_name]):
                abstract_issue =\
                    abstract_issue_obj.create_or_update_from_github(
                        data, repository)
#                repository_ids.append(repository.id)
#            organization.repository_ids = repository_ids

    # Custom Section
    @api.model
    def create_or_update_from_github(self, organization_id, data, full):
        """Create a new repository or update an existing one based on github
        datas. Return a repository."""
        repository_branch_obj = self.env['github.repository.branch']
        repository = self.search([('complete_name', '=', data['full_name'])])

        if repository and not full:
            return repository

        # Get Full Datas from Github
        odoo_data = self.github_2_odoo(
            self.get_data_from_github('repository', [data['full_name']]))
        odoo_data.update({'organization_id': organization_id})
        if not repository:
            repository = self.create(odoo_data)
        else:
            repository.write(odoo_data)

        # Get Branches Data
        branch_datas = self.get_datalist_from_github(
            'repository_branches', [data['full_name']])
        correct_series =\
            repository.organization_id.organization_serie_ids.mapped('name')
        for branch_data in branch_datas:
            if branch_data['name'] in correct_series:
                repository_branch_obj.create_or_update_from_name(
                    repository.id, branch_data['name'])
            else:
                _logger.warning(
                    "the branch '%s'/'%s' has been ignored." % (
                        repository.complete_name, branch_data['name']))

        return repository
