import json
import math
from urllib.parse import parse_qs

from odoo import http
from odoo.http import request


class PropertyApi(http.Controller):

    # ============================================================
    # Helper Methods
    # ============================================================

    @staticmethod
    def valid_response(status, data, pagination_info=None):
        print("\n========== VALID RESPONSE ==========")
        print("Status:", status)
        print("Data:", data)
        print("Pagination Info:", pagination_info)
        print("====================================\n")

        response_body = {
            'data': data,
            'message': 'Property has been processed successfully',
        }

        if pagination_info:
            response_body['pagination_info'] = pagination_info

        return request.make_json_response(
            response_body,
            status=status
        )

    @staticmethod
    def invalid_response(error, status):
        print("\n========== INVALID RESPONSE ==========")
        print("Status:", status)
        print("Error:", error)
        print("=======================================\n")

        response_body = {
            'error': error
        }

        return request.make_json_response(
            response_body,
            status=status
        )

    # ============================================================
    # CREATE PROPERTY
    # ============================================================
    import json

    @http.route(
        "/v1/property/one",
        methods=['POST'],
        type='http',
        auth='none',
        csrf=False
    )
    def post_property(self):

        print("\n")
        print("========================================")
        print("        POST PROPERTY - START")
        print("========================================")

        print("HTTP Method:", request.httprequest.method)
        print("URL:", request.httprequest.url)

        try:

            # قراءة الـ raw body
            raw_data = request.httprequest.data

            print("Raw Data:")
            print(raw_data)

            # تحويل JSON إلى Python dictionary
            vals = json.loads(raw_data)

            print("Parsed JSON:")
            print(vals)

            # التحقق من name
            if not vals.get('name'):
                print("ERROR: name is required")

                return self.invalid_response(
                    'name is required',
                    400
                )

            print("Creating property...")

            res = request.env['property'].sudo().create(vals)

            print("Property created successfully!")
            print("ID:", res.id)
            print("Name:", res.name)

            return self.valid_response(
                201,
                {
                    "message": "Property has been created successfully",
                    "name": res.name,
                    "id": res.id,
                }
            )

        except json.JSONDecodeError as error:

            print("JSON ERROR:")
            print(error)

            return self.invalid_response(
                "Invalid JSON body",
                400
            )

        except Exception as error:

            print("ERROR:")
            print(type(error))
            print(error)

            return self.invalid_response(
                str(error),
                500
            )

    # ============================================================
    # GET ONE PROPERTY
    # ============================================================

    @http.route(
        "/v1/property/<int:property_id>",
        methods=['GET'],
        type='http',
        auth='none',
        csrf=False
    )
    def get_property(self, property_id):

        print("\n")
        print("========================================")
        print("        GET PROPERTY - START")
        print("========================================")

        print("1. HTTP Method:", request.httprequest.method)
        print("2. Property ID:", property_id)
        print("3. URL:", request.httprequest.url)

        try:

            print("4. Searching for property...")

            property_record = (
                request.env['property']
                .sudo()
                .browse(property_id)
            )

            print("5. Browse result:", property_record)

            if not property_record.exists():

                print("ERROR: Property does not exist")

                return self.invalid_response(
                    'property_id does not exist',
                    400
                )

            print("6. Property exists")
            print("   ID:", property_record.id)
            print("   Name:", property_record.name)

            response_data = {
                "name": property_record.name,
                "id": property_record.id,
                "postcode": property_record.postcode,
                "bedrooms": property_record.bedrooms,
                "selling_price": property_record.selling_price,
                "expected_price": property_record.expected_price,
            }

            print("7. Response data:")
            print(response_data)

            print("8. GET PROPERTY - END")

            return self.valid_response(
                200,
                response_data
            )

        except Exception as error:

            print("ERROR while getting property:")
            print("Exception:", error)

            return self.invalid_response(
                str(error),
                400
            )

    # ============================================================
    # DELETE PROPERTY
    # ============================================================

    @http.route(
        "/v1/property/<int:property_id>",
        methods=['DELETE'],
        type='http',
        auth='none',
        csrf=False
    )
    def delete_property(self, property_id):

        print("\n")
        print("========================================")
        print("        DELETE PROPERTY - START")
        print("========================================")

        print("1. HTTP Method:", request.httprequest.method)
        print("2. Property ID:", property_id)
        print("3. URL:", request.httprequest.url)

        try:

            print("4. Searching for property...")

            property_record = (
                request.env['property']
                .sudo()
                .browse(property_id)
            )

            print("5. Browse result:", property_record)

            if not property_record.exists():

                print("ERROR: Property does not exist")

                return self.invalid_response(
                    'property_id does not exist!',
                    400
                )

            print("6. Property exists")
            print("   ID:", property_record.id)
            print("   Name:", property_record.name)

            print("7. Deleting property...")

            property_record.unlink()

            print("8. Property deleted successfully")

            response_data = {
                "message": 'Property has been deleted successfully',
            }

            print("9. Response data:", response_data)
            print("10. DELETE PROPERTY - END")

            return self.valid_response(
                200,
                response_data
            )

        except Exception as error:

            print("ERROR while deleting property:")
            print("Exception:", error)

            return self.invalid_response(
                str(error),
                400
            )

    # ============================================================
    # GET PROPERTY LIST WITH PAGINATION
    # ============================================================

    @http.route(
        "/v1/properties/<int:off>",
        methods=['GET'],
        type='http',
        auth='none',
        csrf=False
    )
    def get_property_list(self, off):

        print("\n")
        print("========================================")
        print("        GET PROPERTY LIST - START")
        print("========================================")

        print("1. HTTP Method:", request.httprequest.method)
        print("2. Initial Offset:", off)
        print("3. URL:", request.httprequest.url)

        try:

            print("4. Reading query string...")

            params = parse_qs(
                request.httprequest.query_string.decode('utf-8')
            )

            print("5. Query Parameters:", params)

            property_domain = []

            page = None
            limit = 5

            print("6. Default limit:", limit)

            # ----------------------------------------------------
            # LIMIT
            # ----------------------------------------------------

            if params.get('limit'):

                limit = int(params.get('limit')[0])

                print("7. Limit received from URL:", limit)

            # ----------------------------------------------------
            # PAGE
            # ----------------------------------------------------

            if params.get('page'):

                page = int(params.get('page')[0])

                print("8. Page received from URL:", page)

            # ----------------------------------------------------
            # Calculate Offset
            # ----------------------------------------------------

            if page:

                off = (page - 1) * limit

                print("9. Calculated offset:", off)

            # ----------------------------------------------------
            # STATE FILTER
            # ----------------------------------------------------

            if params.get('state'):

                state = params.get('state')[0]

                property_domain.append(
                    ('state', '=', state)
                )

                print("10. State filter:", state)

            print("11. Final domain:", property_domain)
            print("12. Final offset:", off)
            print("13. Final limit:", limit)

            # ----------------------------------------------------
            # COUNT
            # ----------------------------------------------------

            print("14. Calculating property count...")

            property_count = (
                request.env['property']
                .sudo()
                .search_count(property_domain)
            )

            print("15. Property count:", property_count)

            # ----------------------------------------------------
            # SEARCH
            # ----------------------------------------------------

            print("16. Searching properties...")

            property_ids = (
                request.env['property']
                .sudo()
                .search(
                    property_domain,
                    order='id desc',
                    offset=off,
                    limit=limit
                )
            )

            print("17. Search result:", property_ids)
            print("18. Number of records:", len(property_ids))

            if not property_ids:

                print("ERROR: No records found")

                return self.invalid_response(
                    'There are no records!',
                    400
                )

            # ----------------------------------------------------
            # Prepare Response Data
            # ----------------------------------------------------

            print("19. Preparing response data...")

            data = []

            for property_id in property_ids:

                print(
                    "   Processing property:",
                    property_id.id,
                    property_id.name
                )

                data.append({
                    "name": property_id.name,
                    "id": property_id.id,
                    "postcode": property_id.postcode,
                    "bedrooms": property_id.bedrooms,
                    "selling_price": property_id.selling_price,
                    "expected_price": property_id.expected_price,
                })

            # ----------------------------------------------------
            # Pagination
            # ----------------------------------------------------

            pages = (
                math.ceil(property_count / limit)
                if limit
                else 1
            )

            pagination_info = {
                "page": page if page else 1,
                "limit": limit,
                "pages": pages,
                "count": property_count,
            }

            print("20. Pagination info:", pagination_info)
            print("21. Response data:", data)

            print("22. GET PROPERTY LIST - END")

            return self.valid_response(
                200,
                data,
                pagination_info=pagination_info
            )

        except Exception as error:

            print("ERROR while getting property list:")
            print("Exception:", error)

            return self.invalid_response(
                str(error),
                400
            )

    # ============================================================
    # GET ALL PROPERTIES
    # ============================================================

    @http.route(
        "/v1/properties",
        methods=['GET'],
        type='http',
        auth='none',
        csrf=False
    )
    def get_property_list_all(self):

        print("\n")
        print("========================================")
        print("        GET ALL PROPERTIES - START")
        print("========================================")

        print("1. HTTP Method:", request.httprequest.method)
        print("2. URL:", request.httprequest.url)

        try:

            print("3. Reading query string...")

            params = parse_qs(
                request.httprequest.query_string.decode('utf-8')
            )

            print("4. Query Parameters:", params)

            property_domain = []

            # ----------------------------------------------------
            # STATE FILTER
            # ----------------------------------------------------

            if params.get('state'):

                state = params.get('state')[0]

                property_domain.append(
                    ('state', '=', state)
                )

                print("5. State filter:", state)

            print("6. Final domain:", property_domain)

            # ----------------------------------------------------
            # SEARCH
            # ----------------------------------------------------

            print("7. Searching all properties...")

            property_ids = (
                request.env['property']
                .sudo()
                .search(property_domain)
            )

            print("8. Search result:", property_ids)
            print("9. Number of records:", len(property_ids))

            # ----------------------------------------------------
            # COUNT
            # ----------------------------------------------------

            property_count = (
                request.env['property']
                .sudo()
                .search_count(property_domain)
            )

            print("10. Property count:", property_count)

            if not property_ids:

                print("ERROR: No records found")

                return self.invalid_response(
                    'There are no records!',
                    400
                )

            # ----------------------------------------------------
            # Prepare Response
            # ----------------------------------------------------

            print("11. Preparing response data...")

            data = []

            for property_id in property_ids:

                print(
                    "   Processing property:",
                    property_id.id,
                    property_id.name
                )

                data.append({
                    "name": property_id.name,
                    "id": property_id.id,
                    "postcode": property_id.postcode,
                    "bedrooms": property_id.bedrooms,
                    "selling_price": property_id.selling_price,
                    "expected_price": property_id.expected_price,
                })

            print("12. Response data:", data)

            print("13. GET ALL PROPERTIES - END")

            return self.valid_response(
                200,
                data
            )

        except Exception as error:

            print("ERROR while getting all properties:")
            print("Exception:", error)

            return self.invalid_response(
                str(error),
                400
            )