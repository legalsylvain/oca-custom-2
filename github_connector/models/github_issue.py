# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class GithubIssue(models.Model):
    _name = 'github.issue'
    _inherit = ['abstract.github.model.author']

    _github_type = 'issue'
    _github_login_field = 'number'

    # Column Section
    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository', readonly=True,
        required=True, ondelete='cascade')

    issue_type = fields.Selection(
        selection=[('issue', 'Issue'), ('pull_request', 'Pull Request')],
        string='Type')

    title = fields.Char(string='Title', readonly=True, required=True)

    body = fields.Char(string='Body', readonly=True)

    state = fields.Selection(selection=[
        ('open', 'Open'), ('closed', 'Closed')],
        string='State', readonly=True, required=True)

    comment_ids = fields.One2many(
        string='Comments', comodel_name='github.comment',
        inverse_name='issue_id', readonly=True)

    comment_qty = fields.Integer(
        string='Comments Quantity', compute='_compute_comment_qty',
        store=True)

    # Compute Section
    @api.multi
    @api.depends('comment_ids', 'comment_ids.issue_id')
    def _compute_comment_qty(self):
        for issue in self:
            issue.comment_qty = len(issue.comment_ids)

    # Overloadable Section
    def get_odoo_data_from_github(self, data):
        res = super(GithubIssue, self).get_odoo_data_from_github(data)
        res.update({
            'title': data['title'],
            'body': data['body'],
            'state': data['state'],
            'issue_type': data.get('pull_request', False)
            and 'pull_request' or 'issue',
        })
        return res

    @api.multi
    def full_update(self):
        self.button_sync_comment()

    # Action section
    @api.multi
    def button_sync_comment(self):
        comment_obj = self.env['github.comment']
        for issue in self:
            comment_ids = []
            for data in self.get_datalist_from_github(
                    'issue_comments',
                    [issue.repository_id.github_login, issue.github_login]):
                comment = comment_obj.get_from_id_or_create(
                    data, {'issue_id': issue.id})
                comment_ids.append(comment.id)
            issue.comment_ids = comment_ids
