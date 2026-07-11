# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RnDomainBuilder(models.TransientModel):
    _name = 'rn.domain.builder'
    _description = 'Domain Builder'

    res_model = fields.Selection(
        selection='_selection_res_model',
        string='Model',
        required=True,
        default='sale.order',
    )
    description = fields.Text(
        string='Describe your filter',
        help='Example: confirmed sales orders, paid invoices this month',
    )
    suggestion_text = fields.Char(string='Type to see suggestions')
    suggestion_display = fields.Char(
        string='Suggestions',
        compute='_compute_suggestion_display',
    )
    domain_text = fields.Text(string='Generated Domain', readonly=True)
    record_count = fields.Integer(string='Records Found', readonly=True)
    warning_message = fields.Text(readonly=True)
    is_valid = fields.Boolean(default=False)

    @api.model
    def _selection_res_model(self):
        return [
            (row['model'], row['label'])
            for row in self.env['rn.domain.parser.service'].supported_models()
        ]

    @api.depends('suggestion_text', 'res_model')
    def _compute_suggestion_display(self):
        service = self.env['rn.domain.parser.service']
        for record in self:
            suggestions = service.suggest_for_partial(record.res_model, record.suggestion_text)
            record.suggestion_display = ', '.join(suggestions) if suggestions else ''

    @api.onchange('description', 'res_model')
    def _onchange_description(self):
        if not self.description or not self.res_model:
            return
        self.action_generate()

    def action_generate(self):
        self.ensure_one()
        if not self.description:
            raise UserError(_('Enter a plain-English filter description first.'))
        result = self.env['rn.domain.parser.service'].parse(
            self.res_model,
            self.description,
        )
        self.write({
            'domain_text': result['domain_text'],
            'record_count': result['record_count'],
            'warning_message': '\n'.join(result['warnings']) if result['warnings'] else False,
            'is_valid': result['valid'] and bool(result['domain']),
        })
        return self._reopen()

    def action_test(self):
        self.ensure_one()
        self.action_generate()
        if not self.is_valid:
            raise UserError(_('Fix validation issues before testing the domain.'))
        domain = self.env['rn.domain.parser.service'].load_domain_text(self.domain_text)
        action = self.env['ir.actions.act_window']._for_xml_id(self._action_xmlid_for_model())
        action['domain'] = domain
        action['name'] = _('Test: %s') % (self.description[:60])
        return action

    def _action_xmlid_for_model(self):
        mapping = {
            'sale.order': 'sale.action_orders',
            'account.move': 'account.action_move_out_invoice_type',
            'product.template': 'product.product_template_action_all',
            'crm.lead': 'crm.crm_lead_all_leads',
            'res.partner': 'contacts.action_contacts',
            'hr.employee': 'hr.open_view_employee_list_my',
            'purchase.order': 'purchase.purchase_rfq',
            'stock.picking': 'stock.action_picking_tree_all',
            'project.project': 'project.open_view_project_all',
        }
        xmlid = mapping.get(self.res_model)
        if not xmlid:
            raise UserError(_('No list action configured for %s') % self.res_model)
        return xmlid

    def action_save_history(self):
        self.ensure_one()
        self.action_generate()
        if not self.is_valid:
            raise UserError(_('Cannot save an invalid domain.'))
        self.env['rn.domain.history'].create({
            'name': (self.description or _('Domain'))[:128],
            'res_model': self.res_model,
            'description': self.description,
            'domain_text': self.domain_text,
            'record_count': self.record_count,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Saved'),
                'message': _('Domain saved to history.'),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_save_filter(self):
        self.ensure_one()
        self.action_generate()
        if not self.is_valid:
            raise UserError(_('Cannot save an invalid domain.'))
        domain = self.env['rn.domain.parser.service'].load_domain_text(self.domain_text)
        model = self.env['ir.model']._get(self.res_model)
        filter_rec = self.env['ir.filters'].create({
            'name': (self.description or _('Domain Builder'))[:128],
            'model_id': model.id,
            'domain': str(domain),
            'user_ids': [(6, 0, [self.env.user.id])],
            'is_default': False,
        })
        history = self.env['rn.domain.history'].create({
            'name': filter_rec.name,
            'res_model': self.res_model,
            'description': self.description,
            'domain_text': self.domain_text,
            'record_count': self.record_count,
            'filter_id': filter_rec.id,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Favorite Filter Saved'),
                'message': _('Filter %s created (%s records).') % (history.name, self.record_count),
                'type': 'success',
                'sticky': False,
            },
        }

    def _reopen(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.domain.builder',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    @api.model
    def action_open_builder(self):
        wizard = self.create({'res_model': 'sale.order'})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Domain Builder'),
            'res_model': 'rn.domain.builder',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }
