
from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    discount = fields.Float()
    vat_amount = fields.Integer(compute='_compute_vat_amount')
    price_total_words = fields.Char(string="Price Total in Words", compute='_compute_price_total_words')

    def _number_to_words(self, number):
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        thousands = ["", "Thousand", "Million", "Billion"]

        if number == 0:
            return "Zero"

        words = ""
        if number < 0:
            words = "Minus "
            number = -number

        def _convert_chunk(num):
            chunk_words = ""
            if num >= 100:
                chunk_words += units[num // 100] + " Hundred "
                num %= 100
            if num >= 20:
                chunk_words += tens[num // 10] + " "
                num %= 10
            if num >= 10:
                chunk_words += teens[num - 10] + " "
                num = 0
            if num > 0:
                chunk_words += units[num] + " "
            return chunk_words

        chunk_count = 0
        while number > 0:
            chunk = number % 1000
            if chunk > 0:
                words = _convert_chunk(chunk) + thousands[chunk_count] + " " + words
            number //= 1000
            chunk_count += 1

        return words.strip()

    @api.depends('vat_amount')
    def _compute_price_total_words(self):
        for line in self:
            amount = line.vat_amount
            print("amount"*10,amount)
            if amount:
                # تحويل الجزء الصحيح والجزء العشري إلى كلمات
                integer_part = int(amount)
                decimal_part = int(round((amount - integer_part) * 100))

                integer_words = self._number_to_words(integer_part) + " Dirhams"
                if decimal_part > 0:
                    decimal_words = self._number_to_words(decimal_part) + " Fils"
                else:
                    decimal_words = ""

                # دمج النص النهائي
                line.price_total_words = (integer_words + " & " + decimal_words).strip() + " Only"
            else:
                line.price_total_words = ""


    @api.depends('price_total', 'price_subtotal')
    def _compute_vat_amount(self):
        for line in self:
            line.vat_amount = line.price_total - line.price_subtotal


