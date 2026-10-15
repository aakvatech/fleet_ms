# Copyright (c) 2023, VV SYSTEMS DEVELOPER LTD and Contributors
# See license.txt

# import frappe
from frappe.tests.utils import FrappeTestCase

# These link targets come from csf_tz, which CI does not install.
test_ignore = ["Files", "Unit of Measure"]


class TestTransportationOrder(FrappeTestCase):
	pass
