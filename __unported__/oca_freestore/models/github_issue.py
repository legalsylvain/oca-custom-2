# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

#import logging
#import os

#from git import Repo
#from subprocess import check_output
#from datetime import datetime
#from os.path import join as opj

from openerp import models, fields, api, exceptions, _

#from openerp.modules import load_information_from_description_file
#from openerp.modules.module import MANIFEST

#_logger = logging.getLogger(__name__)


class GithubIssue(models.AbstractModel):
    _name = 'github.issue'
    _inherit = ['github.connector']

    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository', readonly=True,
        required=True)

    type = fields.Selection(
        selection=[('issue', 'Issue'), ('pull_request', 'Pull Request')],
        string='Type')


    github_id = fields.Integer(string='Github ID', readonly=True,
    required=True)

    title = fields.Char(string='Title', readonly=True, required=True)

    body = fields.Char(string='Body', readonly=True, required=True)

    author_id = fields.Many2one(
        comodel_name='res.partner', string='Author', readonly=True,
        required=True)

    # Custom Section
    def github_2_odoo(self, data):
        partner_obj = self.env['res.partner']
        partner = partner_obj.create_or_update_from_github(data['user'], True),
        return {
            'github_id': data['id'],
            'title': data['title'],
            'body': data['body'],
            'author_id': partner.id,
            'type': data.get('pull_request', False)
                and 'pull_request' or 'issue',
        }

    # Custom Section
    @api.model
    def create_or_update_from_github(self, data, repository):
        print data
        res = self.search([('github_id', '=', data['id'])])
        if not res:
            odoo_data = self.github_2_odoo(data)
            odoo_data.update({'repository_id': repository.id})
            res = self.create(odoo_data)
        return res
