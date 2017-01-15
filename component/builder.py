# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import odoo
from odoo import api, models
from .core import MetaComponent, all_components


class ComponentBuilder(models.AbstractModel):
    """ Build the component classes

    And register them in a global registry.
    The classes are built using the same mechanism
    than the Odoo one, meaning that a final class
    that inherits from all the ``_inherit`` is created.
    This class is kept in the ``all_components`` global
    registry with the Components ``_name`` as keys.

    This is an Odoo model so we can hook the build of the components at the end
    of the registry loading with ``_register_hook``, after all modules are
    loaded.

    """
    _name = 'component.builder'
    _description = 'Component Builder'

    @api.model_cr
    def _register_hook(self):
        all_components.clear()

        graph = odoo.modules.graph.Graph()
        graph.add_module(self.env.cr, 'base')

        self.env.cr.execute(
            "SELECT name "
            "FROM ir_module_module "
            "WHERE state IN ('installed', 'to upgrade', 'to update')"
        )
        module_list = [name for (name,) in self.env.cr.fetchall()
                       if name not in graph]
        graph.add_modules(self.env.cr, module_list)

        for module in graph:
            self.load_components(module.name, all_components)

    def load_components(self, module, registry):
        for component_class in MetaComponent._modules_components[module]:
            component_class._build_component(registry)
