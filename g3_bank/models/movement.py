from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError

class Movement(models.Model):
    _name = 'g3_bank.movement'
    _description = 'Movement'
    

    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)

    name = fields.Selection([
                            ('payment', 'Payment'),
                            ('deposit', 'Deposit')
                            ], string="Description", required=True)
                            
    timestamp = fields.Datetime(string="Date", required=True, default=fields.Datetime.now, readonly=True)
    amount = fields.Monetary(string="Amount", currency_field='currency_id', default=0.0)
    balance = fields.Monetary(string="Balance", currency_field='currency_id', default=0.0, readonly=True)
    
    #Ponemos un campo relacional que lo coge desde cuentas para poder ver el credito 
    credit_limit_info = fields.Monetary(related='account_id.creditLine', string="Account Credit")
    account_type = fields.Selection(related='account_id.typeAccount')
    
    account_id = fields.Many2one('g3_bank.account', string="Account", readonly=True)
    

    
    @api.model
    def create(self, vals):
        #creamos movimiento
        record = super(Movement, self).create(vals)
        
        # Capturamos el balance real y lo pasamos otra vez
        record.balance = record.account_id.balance
        return record
    
    @api.constrains('amount', 'name', 'account_id')
    def _check_amount_and_liquidity(self):
        for r in self:
            if r.amount <= 0:
                raise ValidationError("The amount must be greater than 0.")
            
            if r.name == 'payment':
                #Calculamos el balance que quedaria
                saldo_previo = r.account_id.beginBalance
                for move in r.account_id.movement_ids:
                    if move.id != r.id and move._origin.id != r.id:
                        if move.name == 'deposit':
                            saldo_previo += move.amount
                        elif move.name == 'payment':
                            saldo_previo -= move.amount
                
                limite_credito = r.account_id.creditLine if r.account_id.typeAccount == 'CREDIT' else 0.0
                total_disponible = saldo_previo + limite_credito
                
                # Si el pago es mayor que lo que tengo mas mi credito salta excepcion
                if r.amount > total_disponible:
                    raise ValidationError(
                                          "Insufficient funds.\n"
                                          "Available: %.2f (Balance: %.2f + Credit: %.2f)\n"
                                          "Attempted payment: %.2f" % 
                                          (total_disponible, saldo_previo, limite_credito, r.amount)
                                          )

    # Para calcular balance
    @api.depends('account_id.creditLine', 'account_id.balance')
    def _compute_credit_available(self):
        for r in self:
            if r.account_type == 'CREDIT':
                
                usado = abs(min(r.account_id.balance, 0.0))
                r.credit_available = r.account_id.creditLine - usado
            else:
                r.credit_available = 0.0

    def unlink(self):
        for record in self:
            last_movement = self.search([
                                        ('account_id', '=', record.account_id.id)
                                        ], order='timestamp desc, id desc', limit=1)

            if record.id != last_movement.id:
                raise ValidationError(
                                      "Solo puedes borrar el ultimo movimiento de la cuetna"
                                      )
        return super(Movement, self).unlink()