from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class Person(models.Model):
    _name = 'person'
    _description = 'Person'
    ref = fields.Char(
        default='New',
        readonly=True)

    def _get_report_base_filename(self):
        return 'person_report_' + self.name
    # تخصيص رقم تسلسلي عند إنشاء السجل
    @api.model
    def create(self, vals):
        res = super(Person, self).create(vals)
        res.confirmed_user_id=self.env.user.id
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('person_seq')

        return res
    name = fields.Char(string="Name", required=True)
    birth_date = fields.Date(string="Date of Birth", required=True)
    age = fields.Integer(string="Age", compute='_compute_age')
    is_married = fields.Boolean(string="Is Married", default=False)
    over = fields.Boolean(default=False)
    spouse_name = fields.Char(string="Spouse Name")
    spouse_birth_date = fields.Date(string="Spouse Date of Birth")
    spouse_age = fields.Integer(string="Spouse Age", compute='_compute_spouse_age')
    child_ids = fields.One2many('person.line', 'parent_id', string="Children", store=True)
    birthday_ids = fields.One2many('birthday', 'parent_id', string="Birthdays")
    child_n = fields.Integer(string="Children Num")
    num_children2 = fields.Integer(compute='_compute_rn', store=True)
    total_gift_price = fields.Float(string="Total Gift Price", compute='_compute_total_gift_price')
    the_eldest_boy = fields.Char(string="The eldest boy", compute='_compute_the_eldest_boy')
    confirmed_user_id = fields.Many2one('res.users',string='Confirmed User ')
    @api.depends('birthday_ids.gift_price', 'name')
    def _compute_total_gift_price(self):
        for record in self:
            if record.name:
                total_price = sum(self.env['birthday'].search([
                    ('father', '=', record.name)
                ]).mapped('gift_price'))
                record.total_gift_price = total_price
            else:
                record.total_gift_price = 0

    @api.depends('child_ids')
    def _compute_the_eldest_boy(self):
        for record in self:
            if record.child_ids:
                boys = record.child_ids.filtered(lambda l: l.gender == 'male')
                if boys:
                    eldest_boy = None
                    max_age = 0
                    birth_date_oldest = None

                    for boy in boys:
                        if boy.age and boy.age > max_age:
                            eldest_boy = boy
                            max_age = boy.age
                            birth_date_oldest = boy.birth_date
                        elif boy.age and boy.age == max_age:
                            if boy.birth_date < birth_date_oldest:
                                eldest_boy = boy
                                birth_date_oldest = boy.birth_date

                    record.the_eldest_boy = eldest_boy.name if eldest_boy else None
                else:
                    record.the_eldest_boy = None
            else:
                record.the_eldest_boy = None

    @api.onchange('child_n', 'child_ids')
    def _compute_rn(self):
        for record in self:
            record.num_children2 = len(record.child_ids)

    @api.constrains('child_n', 'child_ids')
    def _check_child_n(self):
        for record in self:
            if len(record.child_ids) > record.child_n:
                raise UserError(
                    f"The number of children ({record.child_n}) is less than the lines. Please update the number of children or remove the excess lines."
                )

            negative_ages = [f"{child.name} (Age: {child.age})" for child in record.child_ids if child.age < 0]
            if record.age < 0 or record.spouse_age < 0 or negative_ages:
                child_ages_info = ", ".join([f"{child.name}: {child.age}" for child in record.child_ids])
                error_message = (
                    f"Person's Age: {record.age}, Spouse's Age: {record.spouse_age}, Children: {child_ages_info}.\n"
                    "All ages must be positive. Please correct the birth dates."
                )
                if negative_ages:
                    error_message += f"\nNegative ages found in the following children: {', '.join(negative_ages)}."
                raise UserError(error_message)

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = datetime.today().date()
                age = today.year - record.birth_date.year - ((today.month, today.day) < (record.birth_date.month, record.birth_date.day))
                record.age = age
            else:
                record.age = 0

    @api.depends('spouse_birth_date')
    def _compute_spouse_age(self):
        for record in self:
            if record.spouse_birth_date:
                today = datetime.today().date()
                age = today.year - record.spouse_birth_date.year - ((today.month, today.day) < (record.spouse_birth_date.month, record.spouse_birth_date.day))
                record.spouse_age = age
            else:
                record.spouse_age = 0

    @api.onchange('is_married')
    def _onchange_is_married(self):
        if not self.is_married:
            self.spouse_name = False
            self.spouse_birth_date = False
            self.spouse_age = 0
            self.child_ids = [(5, 0, 0)]
            self.birthday_ids = [(5, 0, 0)]
            self.child_n = 0
            self.num_children2 = 0
            self.total_gift_price = 0.0
            self.the_eldest_boy = False

    def action_generate_xlsx_report(self):
        return self.env.ref('app_one.action_report_person_xlsx').report_action(self)



class PartnerXlsx(models.AbstractModel):
    _name = 'report.app_one.report_person_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, persons):
        # إنشاء ورقة في ملف Excel
        sheet = workbook.add_worksheet('Persons Report')

        # تنسيقات التقرير
        bold = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        border_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})

        # إعداد عرض الأعمدة
        sheet.set_column('A:A', 20)  # Name
        sheet.set_column('B:B', 15)  # Birth Date
        sheet.set_column('C:C', 10)  # Age
        sheet.set_column('D:D', 12)  # Is Married
        sheet.set_column('E:E', 10)  # Over
        sheet.set_column('F:F', 18)  # Total Gift Price
        sheet.set_column('G:G', 15)  # Num Children
        sheet.set_column('H:H', 20)  # Spouse Name
        sheet.set_column('I:I', 15)  # Spouse Birth Date
        sheet.set_column('J:J', 10)  # Spouse Age
        sheet.set_column('K:K', 15)  # Child Number
        sheet.set_column('L:L', 15)  # The Eldest Boy

        # إضافة عنوان التقرير مع توسيطه
        sheet.merge_range('A1:L1', 'Persons and Children Report', header_format)

        # إضافة العناوين الرئيسية لقسم بيانات الشخص
        sheet.write(1, 0, 'Person Information', bold)
        headers = [
            'Name', 'Birth Date', 'Age', 'Is Married', 'Over',
            'Total Gift Price', 'Num Children', 'Spouse Name',
            'Spouse Birth Date', 'Spouse Age', 'Child Number', 'The Eldest Boy'
        ]
        for col, header in enumerate(headers):
            sheet.write(2, col, header, bold)

        # كتابة بيانات السجلات
        row = 3
        for person in persons:
            sheet.write(row, 0, person.name or '', border_format)
            sheet.write(row, 1, person.birth_date or '', border_format)
            sheet.write(row, 2, person.age or '', border_format)
            sheet.write(row, 3, 'Yes' if person.is_married else 'No', border_format)
            sheet.write(row, 4, person.over or '', border_format)
            sheet.write(row, 5, person.total_gift_price or '', border_format)
            sheet.write(row, 6, person.num_children2 or '', border_format)
            sheet.write(row, 7, person.spouse_name or '', border_format)
            sheet.write(row, 8, person.spouse_birth_date or '', border_format)
            sheet.write(row, 9, person.spouse_age or '', border_format)
            sheet.write(row, 10, person.child_n or '', border_format)
            sheet.write(row, 11, person.the_eldest_boy or '', border_format)

            # إضافة عنوان لقسم بيانات الأطفال
            child_start_row = row + 2
            sheet.write(child_start_row, 0, 'Children Information', bold)
            child_headers = ['Child Name', 'Child Birth Date', 'Child Age', 'Child Gender']
            for col, header in enumerate(child_headers):
                sheet.write(child_start_row + 1, col, header, bold)

            # إضافة بيانات الأطفال
            row = child_start_row + 2
            for child in person.child_ids:
                sheet.write(row, 0, child.name or '', border_format)
                sheet.write(row, 1, child.birth_date or '', border_format)
                sheet.write(row, 2, child.age or '', border_format)
                sheet.write(row, 3, child.gender or '', border_format)
                row += 1

            # تعديل الصف لبيانات الشخص التالي
            row += 1  # لإضافة فراغ بين كل شخص وآخر

        return workbook


class PersonLine(models.Model):
    _name = 'person.line'
    _description = 'Person Line'

    name = fields.Char(string="اسم الطفل", required=True)
    birth_date = fields.Date(string="تاريخ الميلاد")
    age = fields.Integer(string="العمر", compute='_compute_age' ,store=True)
    gender = fields.Selection([('male', 'ذكر'), ('female', 'أنثى')], string="الجنس" ,store=True )
    parent_id = fields.Many2one('person', string="الوالد")


    @api.depends('birth_date','parent_id.name')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = datetime.today().date()
                birth_date = record.birth_date
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                record.age = age


                # تحقق مما إذا كان اليوم هو عيد ميلاد
                if today.month == birth_date.month and today.day == birth_date.day:
                    print("نعم، اليوم هو عيد ميلاد!")

                    # تحقق مما إذا كان هناك سجل عيد ميلاد موجود بالفعل
                    existing_birthday = self.env['birthday'].search([
                        ('birthday', '=', birth_date),
                        ('son', '=', record.name),
                        ('father', '=', record.parent_id.name)
                    ])

                    if not existing_birthday:
                        record.create_birthday()
                    else:
                        print("سجل عيد ميلاد موجود بالفعل.")
                else:
                    print("لا، اليوم ليس عيد ميلاد.")
            else:
                record.age = 0

    def create_birthday(self):
        for rec in self:
            self.env['birthday'].create({
                "son": rec.name,
                "father": rec.parent_id.name,
                "birthday": rec.birth_date,
            })
