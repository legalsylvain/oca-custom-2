# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from subprocess import call, check_output
import os
from datetime import datetime
from os.path import join as opj

from openerp import models, fields, api

from openerp.modules import load_information_from_description_file

from .tools import get_from_github, get_base64_image_from_url

from openerp.modules.module import MANIFEST
from openerp.modules.module import README

import logging

_logger = logging.getLogger(__name__)


class GithubRepositoryBranch(models.Model):
    _name = 'github.repository.branch'

    # FIXME set a configuration setting
    _LOCAL_PATH = '/workspace/source_code/'

    _SELECTION_STATE = [
        ('to_download', 'To Download'),
        ('to_analyze', 'To Analyze'),
        ('analyzed', 'Analyzed'),
    ]

    # Column Section
    name = fields.Char(
        string='Name', select=True, required=True, readonly=True)

    complete_name = fields.Char(
        string='Complete Name', compute='compute_complete_name')
    # store=True


    state = fields.Selection(
        string='State', selection=_SELECTION_STATE, default='to_download')

    repository_id = fields.Many2one(
        comodel_name='github.repository', string='Repository',
        select=True, readonly=True)

    organization_id = fields.Many2one(
        comodel_name='github.organization', string='Organization',
        related='repository_id.organization_id', store=True,
        readonly=True)

    last_download_date = fields.Datetime(string='Last Download Date')

    last_analyze_date = fields.Datetime(string='Last Analyze Date')


    # Compute Section
    @api.multi
    @api.depends('name', 'repository_id.complete_name')
    def compute_complete_name(self):
        for repository_branch in self:
            repository_branch.complete_name =\
                repository_branch.repository_id.complete_name +\
                '/' + repository_branch.name

    # Custom Section
    def create_or_update_from_name(self, repository_id, name):
        repository_branch = self.search([
            ('name', '=', name), ('repository_id', '=', repository_id)])
        if not repository_branch:
            repository_branch = self.create({
                'name': name,
                'repository_id': repository_id})
        return repository_branch

    @api.multi
    def button_download_code(self):
        for repository_branch in self:
            complete_path = self._LOCAL_PATH + repository_branch.complete_name
            if not os.path.exists(complete_path):
                _logger.info("Cloning new repository into %s ..." %(complete_path))
                # Cloning the repository
                os.makedirs(complete_path)
                os.system("cd %s &&"
                " git clone https://github.com/%s.git -b %s ." % (
                    complete_path,
                    repository_branch.repository_id.complete_name,
                    repository_branch.name))
                repository_branch.write({
                    'last_download_date': datetime.today(),
                    'state':  'to_analyze',
                    })
            else:
                # Update repository
                _logger.info("Pulling existing repository %s ..." %(complete_path))
                res = check_output(['git', 'pull', 'origin', repository_branch.name], cwd=complete_path)
                if 'up-to-date' not in res:
                    repository_branch.write({
                        'last_download_date': datetime.today(),
                        'state':  'to_analyze',
                        })
                else:
                    repository_branch.write({
                        'last_download_date': datetime.today(),
                        })

    @api.multi
    def button_analyze_code(self):
        module_version_obj = self.env['oca.module.version']
        for repository_branch in self:
            complete_path = self._LOCAL_PATH + repository_branch.complete_name
            if not os.path.exists(complete_path):
                _logger.warning("Unable to analyse %s. Source code not found." %(complete_path))
            else:
                # Scan folder
                _logger.info("Analyzing repository %s ..." %(complete_path))
                for module_name in self.listdir(complete_path):
                    module_info = load_information_from_description_file(
                        module_name, complete_path + '/' + module_name)
                    if module_info.get('installable', False):
                        module_info['name'] = module_name
                        module_version_obj.create_or_update_from_manifest(
                            module_info, repository_branch)
                repository_branch.write({
                    'last_analyze_date': datetime.today(),
                    'state':  'analyzed',
                    })

    # Copy Paste from Odoo Core
    # This function is for the time being in another function.
    # (Ref: openerp/modules/module.py)
    def listdir(self, dir):
        def clean(name):
            name = os.path.basename(name)
            if name[-4:] == '.zip':
                name = name[:-4]
            return name
        def is_really_module(name):
            manifest_name = opj(dir, name, MANIFEST)
            zipfile_name = opj(dir, name)
            return os.path.isfile(manifest_name)
        return map(clean, filter(is_really_module, os.listdir(dir)))
