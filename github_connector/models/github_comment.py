# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import markdown

from openerp import models, fields, api


class GithubComment(models.Model):
    _name = 'github.comment'
    _inherit = ['abstract.github.model.author']
    _order = 'github_id'

    _github_type = 'issue'
    _github_login_field = False

    # Column Section
    issue_id = fields.Many2one(
        comodel_name='github.issue', string='Issue / PR', readonly=True,
        required=True, ondelete='cascade')

    body = fields.Char(string='Body', readonly=True)

    html_body = fields.Html(
        string='HTML Body', readonly=True, compute='_compute_html_body')

    # Compute section
    @api.multi
    @api.depends('body')
    def _compute_html_body(self):
        for comment in self:
            comment.html_body = markdown.markdown(comment.body)

    # Overloadable Section
    def get_odoo_data_from_github(self, data):
        res = super(GithubComment, self).get_odoo_data_from_github(data)
        res.update({'body': data['body']})
        return res
