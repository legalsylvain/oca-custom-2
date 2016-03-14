# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'OCA FreeStore',
    'version': '8.0.0.0.0',
    'category': 'Custom',
    'author': ['Sylvain LE GAL', 'Odoo Community Association (OCA)'],
    'summary': 'recover information from github repositories',
    'depends': [
        'base',
    ],
    'data': [
        'views/view_res_partner.xml',
        'views/view_github_organization.xml',
        'views/view_github_repository.xml',
        'views/view_github_repository_branch.xml',
        'views/view_github_team.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/res_groups.yml',
        'demo/github_organization.yml',
    ],
    'installable': True,
}
