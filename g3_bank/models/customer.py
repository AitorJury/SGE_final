# -*- coding: utf-8 -*-
from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError
import re
from xml.dom import ValidationErr


EMAIL_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
ONLY_LETTERS_PATTERN = r'^[a-zA-Z]+$'

class Customer(models.Model):

    _description = 'Customer'
    _inherit = 'res.users'
    account_ids = fields.Many2many('g3_bank.account',
                                   #Solo muestran las cuentas que tengan saldo inicial y no esten asignadas a un cliente
                                   string='Cuentas con Saldo Inicial'
                                   )


    @api.constrains('login')
    def _check_login_format(self):
        for record in self:
            #Comprobar que el email cumpla con el formato
            if record.login and not re.match(EMAIL_PATTERN, record.login):
                raise ValidationError('El email debe tener el formato ')

    @api.onchange('login')
    def onchange_login(self):
        if self.login and not re.fullmatch(EMAIL_PATTERN, self.login):
            return {
                'warning': {
                    'title': 'Email invalido',
                    'message': 'El email debe tener el formato adecuado (nombre@dominio.com) '
                }
            }

    @api.constrains('city')
    def check_city_length(self):
        for record in self:
            if record.city and not re.fullmatch(ONLY_LETTERS_PATTERN, record.city):
                raise ValidationError('Solo se admiten caracteres no numericos.')

    @api.onchange('city')
    def onchange_city(self):
        if self.city and not re.fullmatch(ONLY_LETTERS_PATTERN, self.city):
            return {
                'warning': {
                    'title': 'Ciudad invalida',
                    'message': 'Solo se admiten caracteres no numericos.'
                }
            }

    @api.constrains('zip')
    def _check_zip_format(self):
        for record in self:
            #Comprobar que el zip cumpla con el formato
            if record.zip and not record.zip.isdigit():
                raise ValidationError('El código postal (ZIP) solo debe contener números.')
            if len(record.zip) != 5:
                raise ValidationError('El código postal debe tener exactamente 5 dígitos.')


    @api.onchange('zip')
    def onchange_zip(self):
        if self.zip:
            # Usamos regex para verificar que sean exactamente 5 números
            if not re.fullmatch(r'^\d{5}$', self.zip):
                return {
                    'warning': {
                        'title': 'Código Postal no válido',
                        'message': 'El ZIP debe tener exactamente 5 dígitos numéricos (ejemplo: 28001).'
                    }
                }

    @api.constrains('phone')
    def check_phone_format(self):
        for record in self:
            if record.phone and not record.phone.isdigit():
                raise ValidationError('El telefono solo debe contener digitos')

    @api.onchange('phone')
    def onchange_phone(self):
        if self.phone:
            # Usamos regex para verificar que sean exactamente 5 números
            if not self.phone.isdigit():
                return {
                    'warning': {
                        'title': 'Telefono no valido',
                        'message': 'El telefono solo debe contener digitos ejemplo(626170034)'
                    }
                }

#   Borrar solo si no tiene cuentas.
    def unlink(self):
        for record in self:
            # Buscamos si este usuario está en alguna cuenta de nuestro modelo
            accounts = self.env['g3_bank.account'].search([('customer_ids', 'in', record.id)])
            if accounts:
                raise ValidationError("The client '%s' cannot be removed because it has associated bank accounts." % record.name)
        return super(Customer, self).unlink()