# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "booking"
app_title = "Booking"
app_publisher = "August Infotech"
app_description = "Appointment Booking"
app_icon = "octicon octicon-ruby"
app_color = "#D10056"
app_email = "info@augustinfotech.com"
app_license = "GNU General Public Licence"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/booking/css/booking.css"
app_include_js = "/assets/js/booking.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/booking/css/booking.css"
# web_include_js = "/assets/booking/js/booking.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Employee": ["custom_scripts/employee.js"],
    "Event": ["custom_scripts/event.js"],
    "Branch": ["custom_scripts/branch.js"],
	"Customer":["custom_scripts/customer.js"],
	"Item":["custom_scripts/item.js"],
}

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "booking.utils.get_home_page"

# Generators
# ----------

fixtures = ["Workflow","Custom Field","Property Setter"]

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "booking.install.before_install"
# after_install = "booking.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "booking.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Item":{
		"validate" : "booking.booking.item.validate",
		"after_insert": "booking.booking.item.after_insert",
		"after_delete": "booking.booking.item.after_delete"
	},
	"Employee":{
		"validate" : "booking.booking.employee.validate",
		"on_update" : "booking.booking.employee.on_update",
		"after_insert": "booking.booking.employee.after_insert",
	},
	"Event":{
		"validate" : "booking.booking.event.validate",
		"after_insert" : "booking.booking.event.after_insert",
		"after_delete" : "booking.booking.event.after_delete",
		
	},
	"Branch":{
		"validate" : "booking.booking.branch.validate"
	},
	"POS Profile":{
		"validate" : "booking.booking.pos_profile.validate",
		"after_insert": "booking.booking.pos_profile.after_insert"
	},
	"Item Price":{
		"validate" : "booking.booking.item_price.validate"
	},
	"Sales Person":{
		"validate" : "booking.booking.sales_person.validate"
	},
	"Sales Invoice":{
		"validate" : "booking.booking.sales_invoice.validate",
		"after_insert" : "booking.booking.sales_invoice.after_insert"
	},
	"Territory":{
		"validate" : "booking.booking.territory.validate",
		"on_trash" : "booking.booking.territory.on_trash"
	},
	"Customer":{
		"validate" :"booking.booking.customer.validate",
		"after_insert":"booking.booking.customer.after_insert",
		"after_delete":"booking.booking.customer.after_delete"
	}
}


# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
			"15 18 * * *": [
				"booking.booking.event.send_event_summary_mail"
			]
		}
	# "all": [
	# 	"booking.tasks.all"
	# ],
	# "daily": [
	# 	"booking.tasks.daily"
	# ],
	# "hourly": [
	# 	"booking.tasks.hourly"
	# ],
	# "weekly": [
	# 	"booking.tasks.weekly"
	# ]
	# "monthly": [
	# 	"booking.tasks.monthly"
	# ]
}

# Testing
# -------

# before_tests = "booking.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "booking.event.get_events"
# }