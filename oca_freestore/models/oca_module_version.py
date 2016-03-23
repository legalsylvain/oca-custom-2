# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class OcaModuleVersion(models.Model):
    _name = 'oca.module.version'

    # Column Section
    name = fields.Char(
        string='Name', related='module_id.name', store=True, readonly=True,
        select=True)

    complete_name = fields.Char(
        string='Complete Name', compute='compute_complete_name', store=True)

    module_id = fields.Many2one(
        comodel_name='oca.module', string='Module', required=True,
        ondelete='cascade', select=True, auto_join=True, readonly=True)

    repository_branch_id = fields.Many2one(
        comodel_name='github.repository.branch', string='Repository Branch',
        readonly=True)

    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository',
        related='repository_branch_id.repository_id', store=True,
        readonly=True)

    organization_serie_id = fields.Many2one(
        comodel_name='github.organization.serie', string='Organization Serie',
        compute='_compute_organization_serie_id', readonly=True, store=True)

    license_id = fields.Many2one(
        comodel_name='oca.license', string='License', readonly=True)

    summary = fields.Char(string='Summary', readonly=True)

    website = fields.Char(string='Website', readonly=True)

    description = fields.Char(string='Description', readonly=True)

    version = fields.Char(string='Version', readonly=True)

    author = fields.Char(string='Author', readonly=True)

    author_ids = fields.Many2many(
        string='Authors', comodel_name='oca.author',
        relation='github_module_version_author_rel',
        column1='module_version_id', column2='author_id')

    # Compute Section
    @api.multi
    @api.depends('name', 'repository_branch_id.complete_name')
    def compute_complete_name(self):
        for module_version in self:
            module_version.complete_name =\
                module_version.repository_branch_id.complete_name +\
                '/' + module_version.name

    @api.multi
    @api.depends(
        'repository_branch_id', 'repository_branch_id.organization_id',
        'repository_branch_id.organization_id.organization_serie_ids',
        'repository_branch_id.organization_id.organization_serie_ids.name')
    def _compute_organization_serie_id(self):
        organization_serie_obj = self.env['github.organization.serie']
        for module_version in self:
            res = organization_serie_obj.search([
                ('organization_id', '=',
                    module_version.repository_branch_id.organization_id.id),
                ('name', '=', module_version.repository_branch_id.name)])
            module_version.organization_serie_id = res and res[0].id or False

    # Custom Section
    @api.model
    def manifest_2_odoo(self, info, repository_branch, module):
        oca_license_obj = self.env['oca.license']
        oca_author_obj = self.env['oca.author']
        author_ids = []
        author_lst = (type(info['author']) == list) and\
            info['author'] or \
            info['author'].split(',')
        for author in author_lst:
            author_ids.append(
                oca_author_obj.create_if_not_exist(author.strip()).id)
        res = {
            'summary': info['summary'],
            'website': info['website'],
            'author': info['author'],
            'description': info['description'],
            'version': info['version'],
            'license_id': oca_license_obj.create_if_not_exist(
                info['license']).id,
            'repository_branch_id': repository_branch.id,
            'module_id': module.id,
            'author_ids': [[6, False, author_ids]],
        }
        return res

    # Custom Section
    @api.model
    def create_or_update_from_manifest(self, info, repository_branch):
        module_obj = self.env['oca.module']
        module_version = self.search([
            ('name', '=', info['name']),
            ('repository_branch_id', '=', repository_branch.id)])

        if not module_version:
            # Create new module version
            module = module_obj.create_if_not_exist(info['name'])
            module_version.create(
                self.manifest_2_odoo(info, repository_branch, module))
        else:
            # Update module Version
            value = self.manifest_2_odoo(
                info, repository_branch, module_version.module_id)
            module_version.write(value)
