# Copyright (c) 2023, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class Trailers(Document):
	def before_save(self):
		if not self.trailer_number:
			self.trailer_number = self.plate_number
