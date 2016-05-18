# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models

"""
    This Abstract Model manage some github model that have an author_id fields.
    For that models, a company_author_id fields is created and updated to
    manage corporates stats.

    Please note, that a partner can be part of many companies during his
    carrier, so changing parent_id of a partner will not change history,
    if history is not defined.
"""


class AbtractGithubModelAuthor(models.AbstractModel):
    _name = 'abstract.github.model.author'

    author_id = fields.Many2one(
        comodel_name='res.partner', string='Author', readonly=True,
        required=True)

    company_author_id = fields.Many2one(
        comodel_name='res.partner', string='Author Company')

    @api.model
    def create(self, vals):
        # Set related company of the author, if defined
        partner = self.env['res.partner'].browse(vals.get('author_id'))
        vals.update('company_author_id', partner.company_id.id)
        res = super(AbtractGithubModelAuthor, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('author_id'):
            # Set related company of the author, if defined
            partner = self.env['res.partner'].browse(vals.get('author_id'))
            if partner.company_id:
                vals.update('company_author_id', partner.company_id.id)
        res = super(AbtractGithubModelAuthor, self).write(vals)
        return res
