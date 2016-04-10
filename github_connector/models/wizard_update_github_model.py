# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api

from .abstract_github_model import _GITHUB_TYPE


class WizardUpdateGithubModel(models.TransientModel):
    _name = 'wizard.update.github.model'

    # Columns Section
    child_update = fields.Boolean(string='Update Child Objects', default=False)

    @api.multi
    def button_update_github_model(self):
        for wizard in self:
            model_obj = self.env[self._context['active_model']]
            objects = model_obj.browse(self._context['active_ids'])
            objects.update_from_github(wizard.child_update)
