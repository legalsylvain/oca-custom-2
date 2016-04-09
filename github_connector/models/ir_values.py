# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, _
UNIQUE_ACTION_ID = (
    1121141111061019911695109111100112349951161119511226115107)


class IrValues(models.Model):
    _inherit = 'ir.values'

    @api.model
    def get_actions(self, action_slot, model, res_id=False):
        """ Add an action to all models that inherit of abstract.github.model
        """
        res = super(IrValues, self).get_actions(
            action_slot, model, res_id=res_id)
        if action_slot == 'client_action_multi' and model in\
                ['res.partner', 'github.organization']:
            action = self.add_update_from_github_action(model, res_id=res_id)
            value = (UNIQUE_ACTION_ID, 'github_connector', action)
            res.insert(0, value)
        return res

    @api.model
    def add_update_from_github_action(self, model, res_id=False):
        action = self.env.ref(
            'github_connector.action_wizard_update_github_model')
        return {
            'id': action.id,
            'name': _('Update Github Model'),
            'res_model': u'wizard.update.github.model',
            'src_model': model,
            'type': u'ir.actions.act_window',
            'target': 'new',
        }