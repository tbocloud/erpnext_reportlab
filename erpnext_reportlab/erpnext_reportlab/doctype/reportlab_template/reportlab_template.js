// Copyright (c) 2025, sammish and contributors
// For license information, please see license.txt

frappe.ui.form.on("ReportLab Template", {
	refresh(frm) {
		// Add validation helpers for JSON fields
		['fonts_config', 'styles_config', 'test_data'].forEach(field => {
			if (frm.doc[field]) {
				frm.add_custom_button(__('Validate ' + field.replace('_', ' ').title()), () => {
					validate_json_field(frm, field);
				}, __('JSON Validation'));
			}
		});
	},

	fonts_config(frm) {
		validate_json_field(frm, 'fonts_config');
	},

	styles_config(frm) {
		validate_json_field(frm, 'styles_config');
	},

	test_data(frm) {
		validate_json_field(frm, 'test_data');
	}
});

function validate_json_field(frm, fieldname) {
	const value = frm.doc[fieldname];
	if (value && value.trim()) {
		try {
			JSON.parse(value);
			frappe.show_alert({
				message: __(`${fieldname.replace('_', ' ').title()} contains valid JSON`),
				indicator: 'green'
			}, 3);
		} catch (e) {
			frappe.show_alert({
				message: __(`Invalid JSON in ${fieldname.replace('_', ' ').title()}: ${e.message}`),
				indicator: 'red'
			}, 5);
			frappe.validated = false;
		}
	}
}
