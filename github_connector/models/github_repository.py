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

    # Column Section
    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        required=True, select=True, readonly=True, ondelete='cascade')

    name = fields.Char(
        string='Name', select=True, required=True, readonly=True)

    description = fields.Char(string='Description', readonly=True)

    website = fields.Char(string='Website', readonly=True)

    issue_ids = fields.One2many(
        string='Issues / PR', comodel_name='github.issue',
        inverse_name='repository_id', readonly=True)

    issue_qty = fields.Integer(
        string='Issue / PR Quantity', compute='_compute_issue_qty',
        multi='issue', store=True)

    only_issue_qty = fields.Integer(
        string='Issue Quantity', compute='_compute_issue_qty',
        multi='issue', store=True)

    only_pull_request_qty = fields.Integer(
        string='PR Quantity', compute='_compute_issue_qty',
        multi='issue', store=True)

    # Compute Section
    @api.multi
    @api.depends('issue_ids.repository_id')
    def _compute_issue_qty(self):
        for repository in self:
            only_issue_qty = 0
            only_pull_request_qty = 0
            repository.issue_qty = len(repository.issue_ids)
            for issue in repository.issue_ids:
                if issue.issue_type == 'issue':
                    only_issue_qty += 1
                else:
                    only_pull_request_qty += 1
            repository.only_issue_qty = only_issue_qty
            repository.only_pull_request_qty = only_pull_request_qty

    # Overloadable Section
    def github_type(self):
        return 'repository'

    def github_login_field(self):
        return 'full_name'

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

#    repository_branch_ids = fields.One2many(
#        comodel_name='github.repository.branch',
#        inverse_name='repository_id', string='Branches', readonly=True)


####    # Action Section
####    @api.multi
####    def button_analyze_issue(self):
####        return self._analyze_issue()



####    @api.multi
####    def _analyze_issue(self):
####        for repository in self:
########            # Delete all issues versions # TODO
########            module_versions = module_version_obj.search([
########                ('repository_branch_id', '=', repository_branch.id)])
########            module_versions.with_context(
########                dont_change_repository_branch_state=True).unlink()

########            # Delete all pull requests # TODO
########            git_commits = git_commit_obj.search([
########                ('repository_branch_id', '=', repository_branch.id)])
########            git_commits.with_context(
########                dont_change_repository_branch_state=True).unlink()
####            abstract_issue_obj = self.env['github.abstract.issue']

####            # Get Issues datas
####            issue_ids = []
####            for data in self.get_datalist_from_github(
####                    'repository_issues', [repository.complete_name]):
####                abstract_issue =\
####                    abstract_issue_obj.create_or_update_from_github(
####                        data, repository)
#####                repository_ids.append(repository.id)
#####            organization.repository_ids = repository_ids

####    # Custom Section
####    @api.model
####    def create_or_update_from_github(self, organization_id, data, full):
####        """Create a new repository or update an existing one based on github
####        datas. Return a repository."""
####        repository_branch_obj = self.env['github.repository.branch']
####        repository = self.search([('complete_name', '=', data['full_name'])])

####        if repository and not full:
####            return repository

####        # Get Full Datas from Github
####        odoo_data = self.github_2_odoo(
####            self.get_data_from_github('repository', [data['full_name']]))
####        odoo_data.update({'organization_id': organization_id})
####        if not repository:
####            repository = self.create(odoo_data)
####        else:
####            repository.write(odoo_data)

####        # Get Branches Data
####        branch_datas = self.get_datalist_from_github(
####            'repository_branches', [data['full_name']])
####        correct_series =\
####            repository.organization_id.organization_serie_ids.mapped('name')
####        for branch_data in branch_datas:
####            if branch_data['name'] in correct_series:
####                repository_branch_obj.create_or_update_from_name(
####                    repository.id, branch_data['name'])
####            else:
####                _logger.warning(
####                    "the branch '%s'/'%s' has been ignored." % (
####                        repository.complete_name, branch_data['name']))

####        return repository
