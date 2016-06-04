# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class OcaBinLib(models.Model):
    _name = 'oca.bin.lib'
    _order = 'module_version_qty desc'

    # Column Section
    name = fields.Char(
        string='Name', select=True, required=True, readonly=True)

    module_version_ids = fields.Many2many(
        comodel_name='oca.module.version', string='Module Versions',
        relation='module_version_bin_lib_rel', column1='bin_lib_id',
        column2='module_version_id', readonly=True)

    module_version_qty = fields.Integer(
        string='Module Versions Quantity',
        compute='_compute_module_version_qty', store=True)

    # Compute Section
    @api.multi
    @api.depends('module_version_ids', 'module_version_ids.bin_lib_ids')
    def _compute_module_version_qty(self):
        for bin_lib in self:
            bin_lib.module_version_qty = len(bin_lib.module_version_ids)

    # Custom Section
    @api.model
    def create_if_not_exist(self, name):
        binLib = self.search([('name', '=', name)])
        if not binLib:
            binLib = self.create({'name': name})
        return binLib
