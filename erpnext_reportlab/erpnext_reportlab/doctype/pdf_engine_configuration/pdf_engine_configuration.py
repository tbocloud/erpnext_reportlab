# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class PDFEngineConfiguration(Document):
	def validate(self):
		"""Validate PDF Engine Configuration fields"""
		self.validate_engine_configuration()
	
	def validate_engine_configuration(self):
		"""Validate engine_configuration JSON field"""
		if self.engine_configuration:
			if isinstance(self.engine_configuration, str):
				try:
					json.loads(self.engine_configuration)
				except json.JSONDecodeError:
					# If invalid JSON, set to default
					self.engine_configuration = json.dumps({
						"quality": "high",
						"page_size": "A4",
						"orientation": "portrait"
					})
			elif isinstance(self.engine_configuration, dict):
				self.engine_configuration = json.dumps(self.engine_configuration)
		else:
			# Set default configuration
			self.engine_configuration = json.dumps({
				"quality": "high",
				"page_size": "A4",
				"orientation": "portrait"
			})
	
	def before_insert(self):
		"""Set defaults before inserting"""
		if not self.configuration_name:
			self.configuration_name = "Default ReportLab Configuration"
		if not self.engine_type:
			self.engine_type = "ReportLab"
		if not self.enabled:
			self.enabled = 1
