# -*- coding: utf-8 -*-

from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class Account(models.Model):
    _name = 'g3_bank.account'
    _description = 'Account'

#   Mejora: Customer predefinido.
    def _default_customer(self):
        return [(4, self.env.user.id)]

# Campo técnico necesario para Monetary
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)

#   El id no se define, Odoo lo añade automáticamente
#   Utilizo name como la descripción de Account
    name = fields.Char(string='Description', required=True)
    balance = fields.Monetary(string='Balance', currency_field='currency_id', compute='_compute_balance', store=True)
    creditLine = fields.Monetary(string='Credit Line', currency_field='currency_id', default=0.0)
    beginBalance = fields.Monetary(string='Begin Balance', currency_field='currency_id', required=True)
    beginBalanceTimestamp = fields.Datetime(string='Opening Date', default=fields.Datetime.now)
    # La selección del tipo de cuenta
    typeAccount = fields.Selection([
                                   ('STANDARD', 'Standard'),
                                   ('CREDIT', 'Credit'),
                                   ], string='Account Type', required=True, default='STANDARD')
    
#   Relación con Customer (Muchos a Muchos)
    customer_ids = fields.Many2many('res.users', string='Customers', default=_default_customer, required=True,
                                    domain=[('active', '=', True), ('share', '=', False)])
#   Relación con Movement (Uno a Muchos)
    movement_ids = fields.One2many('g3_bank.movement', 'account_id', string='Movements')

#   Lógica para sumar el balance total.
    @api.depends('beginBalance', 'movement_ids.amount', 'movement_ids.name')
    def _compute_balance(self):
        for record in self:
            bal = record.beginBalance
            for move in record.movement_ids:
                # Si el movimiento es depósito suma, si es pago resta.
                if move.name == 'deposit':
                    bal += move.amount
                elif move.name == 'payment':
                    bal -= move.amount
            record.balance = bal

#   Mejora: Customer Obligatorio.
    @api.constrains('customer_ids')
    def _check_customer_ids(self):
        for record in self:
            if not record.customer_ids:
                raise ValidationError("An account must have at least one associated customer.")

#   Mejora: Credit Line solo positivo.
    @api.constrains('creditLine')
    def _check_credit_line(self):
        for record in self:
            if record.creditLine < 0:
                raise ValidationError("The credit line limit cannot be negative.")
            
#   Valida que el begin balance no sea negativo.
    @api.constrains('beginBalance')
    def _check_begin_balance(self):
        for record in self:
            if record.beginBalance < 0:
                raise ValidationError("The opening balance cannot be negative.")

#   Solo permite modificar 'name' y 'creditLine' (si es CREDIT).
    def write(self, vals):
        protected_fields = ['beginBalance', 'typeAccount']
        for field in protected_fields:
            if field in vals:
                raise UserError("The initial balance and account type are immutable after creation.")
        return super(Account, self).write(vals)

#   Solo se pueden borrar cuentas sin movimientos.
    def unlink(self):
        for record in self:
            if record.movement_ids:
                raise UserError("Cannot delete an account that has movements.")
        return super(Account, self).unlink()
    
#   Lógica para que salten advertencias cuando intentan cambiar cosas.
#    @api.onchange('beginBalance', 'typeAccount')
#    def _onchange_protected_fields(self):
#        # 'id' solo existe si el registro ya está en la base de datos.
#        if self._origin.id:
#            return {
#                'warning': {
#                    'title': "Modification Prohibited",
#                    'message': "You are attempting to modify a protected field. Changes to 'Begin Balance' or 'Account Type' will not be saved."
#                }
#            }

#   Validación para el límite de crédito.
#    @api.onchange('creditLine')
#    def _onchange_credit_line(self):
#        if self._origin.id and self.typeAccount == 'STANDARD':
#            return {
#                'warning': {
#                    'title': "Invalid Action",
#                    'message': "Credit line can only be modified for CREDIT accounts."
#                }
#            }

#   Accion de crear movimiento.
#    def action_create_movement(self):
#        self.ensure_one()
#        return {
#            'name': 'New Movement',
#            'type': 'ir.actions.act_window',
#            'res_model': 'g3_bank.movement',
#            'view_mode': 'form',
#            'target': 'new',
#            'context': {'default_account_id': self.id},
#        }

#    def action_unlink_movement(self):
#        if not self.movement_ids:
#            return True
#        movements_sorted = self.movement_ids.sorted(key=lambda r: (r.timestamp, r.id), reverse=True)
#        last_movement = movements_sorted[0]
#        last_movement.unlink()
#    
#        return True
