# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class ReportLabTemplate(Document):
	def validate(self):
		"""Validate JSON fields before saving"""
		self.validate_json_field("fonts_config")
		self.validate_json_field("styles_config") 
		self.validate_json_field("test_data")
		
	def validate_json_field(self, fieldname):
		"""Validate that a field contains valid JSON or is empty"""
		value = self.get(fieldname)
		if value:
			try:
				# If it's already a dict/list, convert to JSON string
				if isinstance(value, (dict, list)):
					self.set(fieldname, json.dumps(value))
				else:
					# Try to parse as JSON to validate
					json.loads(value)
			except (json.JSONDecodeError, TypeError) as e:
				frappe.throw(f"Invalid JSON in {fieldname}: {str(e)}")
				
	def before_insert(self):
		"""Set default values for JSON fields if they're empty"""
		if not self.fonts_config:
			self.fonts_config = None
		if not self.styles_config:
			self.styles_config = None
		if not self.test_data:
			self.test_data = None
