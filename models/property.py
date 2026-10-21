from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class Property(models.Model):
    _name = 'property'
    _description = 'Property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    def P1(self):
        print("property" * 1000)
        pass
    # تعريف الحقول
    name = fields.Char(string='Name', required=True, translate=True)
    ref = fields.Char(
        default='New',
                      readonly=True)
    country_id = fields.Many2one('res.country', string='Country',
                                 help="Apply only if delivery country matches.")
    postcode = fields.Char(required=True, size=5)
    description = fields.Text(tracking=1)
    date = fields.Date(default=fields.Date.context_today, tracking=1)
    create_time = fields.Datetime(default=fields.Datetime.now)
    next_time = fields.Datetime(compute='_compute_next_time', store=True)
    availability = fields.Date()
    expected_selling_date = fields.Date()
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    active = fields.Boolean(default=True)
    is_late = fields.Boolean(default=False)
    facade = fields.Integer()
    garden_area = fields.Integer()
    garden = fields.Boolean()
    garage = fields.Boolean()
    expected_price = fields.Float(digits=(0, 2))
    best_offer = fields.Float(compute='_compute_best_offer', string='Best Offer', store=True)
    best_man = fields.Char(compute='_compute_best_offer', string='Best Offer', store=True)
    # partner_phone = fields.Char(compute='_compute_best_offer', string='Best Offer phone')
    selling_price = fields.Float(digits=(0, 2))
    diff_price = fields.Float(compute='_compute_diff', string='Difference Price', store=True)
    owner_id = fields.Many2one('owner')
    address_id = fields.Many2one('res.partner')
    owner_phone = fields.Char(related='owner_id.phone', readonly=True)

    owner_address = fields.Char(related='owner_id.address', readonly=True)
    garden_orientation = fields.Selection([
        ("north", "North"),
        ("south", "South"),
        ("east", "East"),
        ("west", "West"),
    ], default="north")
    state = fields.Selection([
        ("draft", "Draft"),
        ("pending", "Pending"),
        ("sold", "Sold"),
        ("closed", "Closed"),
    ], default="draft")

    tag_ids = fields.Many2many('tag')
    line_ids = fields.One2many('property.line', 'property_id')
    offers_ids = fields.One2many('property.offers', 'property_id')

    # تحديد قيد SQL لضمان عدم تكرار الاسم
    _sql_constraints = [('unique_name', 'unique(name)', 'This name already exists.')]

    # لا زم الشرط يكون متحقق قبل الاستخدام
    # تحقق من عدد الغرف
    # عملت مشكله
    # @api.onchange('bedrooms')
    # def _check_bedrooms_zero(self):
    #      if self.bedrooms <= 0:
    #         print("self == 11111"*10)
    #         raise ValidationError("Please add a valid number of bedrooms greater than zero.")

    # تحقق من تاريخ البيع المتوقع

    # تغيير حالة العقار
    def action_draft(self):
        for rec in self:
            rec.create_property_history(rec.state, 'draft', 'Set to draft')
            rec.selling_price = 0
            rec.state = 'draft'

    def action_pending(self):
        for rec in self:
            rec.create_property_history(rec.state, 'pending', 'Set to pending')
            rec.selling_price = 0
            rec.state = 'pending'

    def action_sold(self):
        for rec in self:
            rec.create_property_history(rec.state, 'sold', 'Set to sold')
            if rec.selling_price >= 0:
                print(rec.selling_price)
                print("ss" * 10)
                rec.state = 'sold'
            else:
                raise ValidationError("Please add a valid number of Selling_price greater than zero.")

    def action_closed(self):
        print("action_closed " * 50)
        for rec in self:
            rec.create_property_history(rec.state, 'closed', 'Set to closed')
            rec.state = 'closed'

    # حساب الفرق بين السعر المتوقع وسعر البيع
    # @api.onchange('expected_price', 'selling_price')
    # def _compute_diff(self):
    #     for rec in self:
    #         print("diff_price"*50,rec)
    #         rec.diff_price = rec.expected_price - rec.selling_price

    @api.depends('expected_price', 'selling_price')
    def _compute_diff(self):
        for rec in self:
            rec.diff_price = rec.expected_price - rec.selling_price

    # تغيير القيمة المتوقعة للأسعار
    @api.model
    def write(self, vals):
        res = super(Property, self).write(vals)
        return res

    def unlink(self):
        res = super(Property, self).unlink()
        print(" unlink " * 30)
        return res
    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        res = super(Property, self)._search(domain, offset=0, limit=None, order=None, access_rights_uid=None)
        return res

    def action(self):
        print(self.env['property'])
        for owner in self.env['property'].search([]):
            print("Name:", owner)
            print("Owner Name:", owner.name)

    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        if self.expected_price <= 0:
            return {
                'warning': {
                    'title': 'Warning',
                    'message': 'The expected price must be a positive value.',
                    'type': 'notification'
                }
            }

    def check_expected_selling_date(self):
        for rec in self.search([]):
            if rec.expected_selling_date and rec.expected_selling_date < fields.Date.today() and rec.state not in [
                'sold', 'closed']:
                rec.is_late = True

    # إنشاء تاريخ العقار
    def create_property_history(self, old_state, new_state, reason):
        for rec in self:
            self.env['property.history'].create({
                "user_id": self.env.uid,
                "property_id": rec.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason or "",
                'line_ids': [(0, 0, {'description': line.description, 'area': line.area}) for line in rec.line_ids],
            })

    # تخصيص رقم تسلسلي عند إنشاء السجل
    @api.model
    def create(self, vals):
        res = super(Property, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('property_seq')

        return res

    # حساب الوقت التالي
    @api.depends('create_time')
    def _compute_next_time(self):
        for rec in self:
            if rec.create_time:
                rec.next_time = rec.create_time + timedelta(hours=6)
            else:
                rec.next_time = False

    # مثال على طريقة عمل مخصصة

    # طباعة معلومات المستخدم المنشئ
    def print_create_uid_and_user_id(self):
        for record in self:
            print(f'Record: {record.name}, Created by: {record.create_uid.name}, User Name: {self.env.user.name}')
            if record.create_uid.name == self.env.user.name:
                print("User is the creator.")

    # فتح واجهة المستخدم المتعلقة بالمالك
    def action_open_related_owner(self):
        self.ensure_one()  # تأكد من وجود سجل فردي فقط
        action = self.env['ir.actions.actions']._for_xml_id('app_one.owner_action')
        view_id = self.env.ref('app_one.owner_view_form').id
        action['res_id'] = self.owner_id.id
        action['views'] = [(view_id, 'form')]
        return action

    # إضافة دالة حساب أفضل عرض

    # @api.onchange('offers_ids')
    @api.depends('offers_ids.price', 'offers_ids.partner_id')
    def _compute_best_offer(self):
        for rec in self:
            if rec.offers_ids:
                print(rec.offers_ids)
                # العثور على أعلى سعر من العروض
                print(rec.offers_ids.mapped('price'))
                best_offer = max(rec.offers_ids.mapped('price'), default=0.0)

                rec.best_offer = best_offer

                # العثور على العرض الذي يحتوي على أعلى سعر
                best_offer_record = rec.offers_ids.filtered(lambda x: x.price == best_offer)

                # تعيين اسم الشريك المرتبط بأعلى عرض
                if best_offer_record:
                    rec.best_man = best_offer_record.partner_id.display_name
                    rec.partner_phone = best_offer_record.partner_id.phone
                else:
                    rec.best_man = ''
                    rec.partner_phone = ''
            else:
                rec.best_offer = 0.0
                rec.best_man = ''

    def action_open_change_state_wizard(self):
        actions=self.env['ir.actions.actions']._for_xml_id('app_one.change_state_wizard_action')
        actions['context'] ={'default_property_id':self.id}
        return actions
class PropertyOffers(models.Model):
    _name = 'property.offers'

    property_id = fields.Many2one('property')
    price = fields.Float()
    validity = fields.Integer()
    partner_id = fields.Many2one('res.partner', string='Owner', track_visibility='onchange')


class PropertyLines(models.Model):
    _name = 'property.line'

    property_id = fields.Many2one('property')
    area = fields.Float()
    description = fields.Char()


class Country(models.Model):
    _inherit = 'res.country'

    @api.model
    def _name_search(self, name='', domain=None, operator='ilike', limit=None, order=None):
        rnt=super()._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)
        ctx=self.env.context
        print(rnt)
        print(ctx)
        return rnt




class Install(models.Model):
    _inherit = 'ir.module.module'

    def P(self):
        print("p" * 1000)
        pass

    @api.model
    def button_install(self):
        print("button_immediate_install" * 100)

        # استدعاء دالة P باستخدام self
        self.P()
        # self.env['property'].P1()

        rnt = super(Install, self).button_install()

        return rnt