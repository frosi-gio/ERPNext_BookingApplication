from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Appointment"),
			"items": [
				{
					"type": "doctype",
					"name": "Event",
					"description": _("Event")
				},
                {
					"type": "doctype",
					"name": "Employee Schedule",
					"description": _("Employee Schedule")
				},
                {
					"type": "doctype",
					"name": "Holiday List",
					"description": _("Holiday List")
				}
			]
        },
        {
			"label": _("Main Masters"),
			"items": [
				{
					"type": "doctype",
					"name": "Item",
					"description": _("Item")
				},
				{
					"type": "doctype",
					"name": "Customer",
					"description": _("Customer")
				},
				{
					"type": "doctype",
					"name": "Employee",
					"description": _("Employee")
				},
				{
					"type": "doctype",
					"name": "Territory",
					"description": _("Territory")
				},
				{
					"type": "doctype",
					"name": "Price List",
					"description": _("Price List")
				},
				{
					"type": "doctype",
					"name": "Item Price",
					"description": _("Item Price")
				},
			]
		},
        {
			"label": _("POS"),
			"items": [
				{
                "type": "page",
                "name": "pos",
                "label": _("POS"),
                "description": _("Point of Sale")
				},
                {
                "type": "doctype",
                "name": "POS Settings",
                "description": _("Setup mode of POS (Online / Offline)")
                },
                {
					"type": "doctype",
					"name": "POS Profile",
					"description": _("POS Profile")
				}
			]
		},
        {
        "label": _("Settings"),
        "items": [
            {
                "type": "doctype",
                "name": "Booking Settings",
                "description": _("Booking Settings")
            },
            {
            "type": "doctype",
            "name":"Terms and Conditions",
            "label": _("Terms and Conditions Template"),
            "description": _("Template of terms or contract.")
            },
            {
            "type": "doctype",
            "name":"Mode of Payment",
            "description": _("e.g. Bank, Cash, Credit Card")
            }
	
			]
		},
    		{
			"label": _("Booking Reports"),
			"items": [
				{
					"type": "report",
					"name": "Next Day Summary",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Sales Register",
					"is_query_report": True
				},
				{
					"type": "page",
					"name": "sales-analytics",
					"label": _("Sales Analytics"),
					"icon": "fa fa-bar-chart",
				},
				{
					"type": "report",
					"name": "Sales Person-wise Transaction Summary",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Appointments Summary",
					"is_query_report": True
				}
			]
		}
    ]