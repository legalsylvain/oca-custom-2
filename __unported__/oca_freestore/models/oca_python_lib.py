# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class OcaPythonLib(models.Model):
    _name = 'oca.python.lib'
    _order = 'module_version_qty desc'

    # Column Section
    name = fields.Char(
        string='Name', select=True, required=True, readonly=True)

    module_version_ids = fields.Many2many(
        comodel_name='oca.module.version', string='Module Versions',
        relation='module_version_python_lib_rel', column1='python_lib_id',
        column2='module_version_id', readonly=True)

    module_version_qty = fields.Integer(
        string='Module Versions Quantity',
        compute='_compute_module_version_qty', store=True)

    # Compute Section
    @api.multi
    @api.depends('module_version_ids', 'module_version_ids.python_lib_ids')
    def _compute_module_version_qty(self):
        for python_lib in self:
            python_lib.module_version_qty = len(python_lib.module_version_ids)

    # Custom Section
    @api.model
    def create_if_not_exist(self, name):
        pythonLib = self.search([('name', '=', name)])
        if not pythonLib:
            pythonLib = self.create({'name': name})
        return pythonLib
