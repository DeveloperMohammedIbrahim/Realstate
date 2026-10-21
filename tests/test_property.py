# from odoo.tests.common import TransactionCase
# import datetime  # استيراد datetime هنا
#
# class TestProperty(TransactionCase):
#     def setUp(self, *args, **kwargs):
#         super(TestProperty, self).setUp()
#         self.property_01_record = self.env['property'].create({
#             'ref': 'PRT00009',
#             'state': 'draft',
#             'name': 'property 6 test',
#             'postcode': '66666',
#             'bedrooms': 5,
#             'selling_price': 1000,
#             'expected_price': 2000,
#             'active': True,
#             'diff_price': 1000,
#             'description': 'test',
#             'owner_id': 1,
#             'owner_phone': '011120555',
#             'owner_address': 'mmmmm',
#             'date': '2024-07-18',
#             'availability': '2024-07-20',
#             'expected_selling_date': '2024-07-21',
#             'is_late': False,
#             'living_area': 50,
#             'garden': True,
#             'garden_orientation': 'north',
#         })
#
#     def test_01_property_values(self):
#         property_id = self.property_01_record
#         expected_values = {
#             'ref': 'PRT00009',
#             'state': 'draft',
#             'name': 'property 6 test',
#             'postcode': '66666',
#             'bedrooms': 5,
#             'selling_price': 1000,
#             'expected_price': 2000,
#             'active': True,
#             'diff_price': 1000,
#             'description': 'test',
#             'owner_id': 1,
#             'owner_phone': '011120555',
#             'owner_address': 'mmmmm',
#             'date': '2024-07-18',
#             'availability': datetime.date(2024, 7, 20),  # تحويل القيمة الفعلية إلى نوع datetime.date
#             'expected_selling_date': '2024-07-21',
#             'is_late': False,
#             'living_area': 50,
#             'garden': True,
#             'garden_orientation': 'north',
#         }
#
#         # Compare each field individually or in small groups
#         for field, expected_value in expected_values.items():
#             if isinstance(expected_value, datetime.date):
#                 expected_value = expected_value.strftime('%Y-%m-%d')  # تحويل إلى نفس التنسيق المتوقع
#             actual_value = property_id[field]
#             self.assertEqual(actual_value, expected_value,
#                              f"Field '{field}' does not match. Expected: {expected_value}, Actual: {actual_value}")
#
#         # Or use assertRecordValues for a comprehensive comparison
#         # self.assertRecordValues(property_id, [expected_values])
from odoo.tests.common import TransactionCase
import datetime

class TestProperty(TransactionCase):
    s=datetime.date(2024, 7, 18)
    def setUp(self, *args, **kwargs):
        super(TestProperty, self).setUp()
        self.property_01_record = self.env['property'].create({
            'ref': 'PRT00009',
            'state': 'draft',
            'name': 'property 6 test',
            'postcode': '66666',
            'bedrooms': 5,
            'selling_price': 1000,
            'expected_price': 2000,
            'active': True,
            'diff_price': 1000,
            'description': 'test',

            'owner_phone': '011120555',
            'owner_address': 'mmmmm',

            'is_late': False,
            'living_area': 50,
            'garden': True,
            'garden_orientation': 'north',
        })

    def test_01_property_values(self):
        property_id = self.property_01_record
        expected_values = {
            'ref': 'PRT00009',
            'state': 'draft',
            'name': 'property 6 test',
            'postcode': '66666',
            'bedrooms': 5,
            'selling_price': 1000,
            'expected_price': 2000,
            'active': True,
            'diff_price': 1000,
            'description': 'test',

            'owner_phone': '011120555',
            'owner_address': 'mmmmm',

            'is_late': False,
            'living_area': 50,
            'garden': True,
            'garden_orientation': 'north',
        }
        # Compare each field individually or in small groups
        for field, expected_value in expected_values.items():
            if field == 'date' and isinstance(expected_value, datetime.date):
                expected_value = expected_value.strftime('%Y-%m-%d')  # تحويل إلى نفس التنسيق المتوقع
            actual_value = property_id[field]
            self.assertEqual(actual_value, expected_value,
                             f"Field '{field}' does not match. Expected: {expected_value}, Actual: {actual_value}")

        # Or use assertRecordValues for a comprehensive comparison
        # self.assertRecordValues(property_id, [expected_values])

        # Compare each field individually or in small groups
        for field, expected_value in expected_values.items():
            if field == 'owner_id':
                actual_owner_id = property_id.owner_id.id if property_id.owner_id else False
                self.assertEqual(actual_owner_id, expected_value,
                                 f"Field '{field}' does not match. Expected: {expected_value}, Actual: {actual_owner_id}")
            else:
                actual_value = property_id[field]
                self.assertEqual(actual_value, expected_value,
                                 f"Field '{field}' does not match. Expected: {expected_value}, Actual: {actual_value}")

        # Or use assertRecordValues for a comprehensive comparison
        # self.assertRecordValues(property_id, [expected_values])
