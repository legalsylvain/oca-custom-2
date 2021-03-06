# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.tools import html_sanitize


class OcaModule(models.Model):
    _name = 'oca.module'
    _order = 'name'

    # Column Section
    name = fields.Char(
        string='Name', select=True, required=True, readonly=True)

    module_version_ids = fields.One2many(
        comodel_name='oca.module.version', inverse_name='module_id',
        string='Versions')

    module_version_qty = fields.Integer(
        string='Module Version Quantity',
        compute='_compute_module_version_qty', store=True)

    author_ids = fields.Many2many(
        string='Authors', comodel_name='oca.author',
        compute='compute_author', relation='github_module_author_rel',
        column1='module_id', column2='author_id', multi='author',
        store=True)

    author_list = fields.Char(
        string='Authors List', compute='compute_author', multi='author',
        store=True)

    organization_serie_ids = fields.Many2many(
        string='Organization Series', comodel_name='github.organization.serie',
        compute='_compute_organization_serie_ids',
        relation='github_module_organization_serie_rel',
        column1='module_id', column2='organization_serie_id', store=True)

    description_rst = fields.Char(
        string='RST Description of the last Version', store=True,
        readonly=True, compute='_compute_description', multi='description_rst')

    description_rst_html = fields.Html(
        string='HTML of the RST Description of the last Version', store=True,
        readonly=True, compute='_compute_description', multi='description_rst')

    dependence_module_version_ids = fields.Many2many(
        comodel_name='oca.module.version',
        string='Module Versions that depend on this module',
        relation='module_version_dependency_rel',
        column1='dependency_module_id', column2='module_version_id')

    dependence_module_version_qty = fields.Integer(
        string='Quantity of Module Versions that depend on this module',
        compute='_compute_dependence_module_version_qty')
    # , store=True FIXME

    # Compute Section
    @api.multi
    @api.depends(
        'module_version_ids', 'module_version_ids.description_rst_html')
    def _compute_description(self):
        module_version_obj = self.env['oca.module.version']
        for module in self:
            version_ids = module.module_version_ids.ids
            last_version = module_version_obj.search(
                [('id', 'in', version_ids)],
                order='organization_serie_id desc', limit=1)
            if last_version:
                module.description_rst = last_version.description_rst
                module.description_rst_html = last_version.description_rst_html
            else:
                module.description_rst = ''
                module.description_rst_html = html_sanitize(
                    "<h1 style='color:gray;'>" +
                    _("No Version Found") +
                    "</h1>")

    @api.multi
    @api.depends(
        'dependence_module_version_ids',
        'dependence_module_version_ids.dependency_module_ids')
    def _compute_dependence_module_version_qty(self):
        for module in self:
            module.dependence_module_version_qty =\
                len(module.dependence_module_version_ids)

    @api.multi
    @api.depends('module_version_ids')
    def _compute_module_version_qty(self):
        for module in self:
            module.module_version_qty = len(module.module_version_ids)

    @api.multi
    @api.depends('module_version_ids', 'module_version_ids.author_ids')
    def compute_author(self):
        for module in self:
            authors = []
            for version in module.module_version_ids:
                authors += version.author_ids
            authors = set(authors)
            module.author_ids = [x.id for x in authors]
            module.author_list = ', '.join(sorted([x.name for x in authors]))

    @api.multi
    @api.depends(
        'module_version_ids', 'module_version_ids.organization_serie_id')
    def _compute_organization_serie_ids(self):
        for module in self:
            organization_series = []
            for version in module.module_version_ids:
                organization_series += version.organization_serie_id
            module.organization_serie_ids = [
                version.organization_serie_id.id
                for version in module.module_version_ids]

    # Custom Section
    @api.model
    def create_if_not_exist(self, name):
        module = self.search([('name', '=', name)])
        if not module:
            module = self.create({'name': name})
        return module
