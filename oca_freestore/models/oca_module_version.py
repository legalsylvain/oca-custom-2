# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api

class OcaModuleVersion(models.Model):
    _name = 'oca.module.version'

#    _inherits = {'oca.module': 'module_id'}

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

    license_id = fields.Many2one(
        comodel_name='oca.license', string='License', readonly=True)

    summary = fields.Char(string='Summary', readonly=True)

    website = fields.Char(string='Website', readonly=True)

    description = fields.Char(string='Description', readonly=True)

    version = fields.Char(string='Version', readonly=True)

    author = fields.Char(string='Author', readonly=True)

    # Compute Section
    @api.multi
    @api.depends('name', 'repository_branch_id.complete_name')
    def compute_complete_name(self):
        for module_version in self:
            module_version.complete_name =\
                module_version.repository_branch_id.complete_name +\
                '/' + module_version.name

    # Custom Section
    @api.model
    def manifest_2_odoo(self, info, repository_branch, module):
        oca_license_obj = self.env['oca.license']
        return {
            'summary': info['summary'],
            'website': info['website'],
            'author': info['author'],
            'description': info['description'],
            'version': info['version'],
            'license_id': oca_license_obj.create_if_not_exist(
                info['license']).id,
            'repository_branch_id': repository_branch.id,
            'module_id': module.id,
#            'image': get_base64_image_from_url(data['avatar_url']),
        }


    # TODO idea : set active == installable ?

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
            module_version.write(
                self.manifest_2_odoo(
                    info, repository_branch, module_version.module_id))
