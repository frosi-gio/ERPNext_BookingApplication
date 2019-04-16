// Copyright (c) 2016, August Infotech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Appointments Summary"] = {
	"filters": [

	{
			"fieldname":"barber",
			"label": __("Barber"),
			"fieldtype": "Link",
			"options": "Employee"
			
	},
	{
			"fieldname":"appointment_date",
			"label": __("Appointment Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80"
		}

	],
	onload: function(report) {
		report.page.add_inner_button(__("Add New Appointment"), function() {
			//frappe.set_route("List","Event")
			frappe.new_doc("Event");
		});
	}
}
