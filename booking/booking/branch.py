# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe.utils import flt, cint, cstr, add_days, getdate
from frappe.model.naming import make_autoname
import json
from frappe import _
import frappe.defaults

def validate(doc, method):

	# ---------------------------------------------------------------------------
	# create cost center
	# --------------------------------------------------------------------------- */
	default_cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
	get_parent_cost_center = frappe.db.get_value("Cost Center", default_cost_center, "parent_cost_center")

	doc_cost_center = frappe.db.get_value("Cost Center",str(doc.name) + " - " + str(frappe.db.get_value("Company", doc.company, "abbr")), "name")
	if not doc_cost_center:
		cost_center = frappe.get_doc({
				"doctype":"Cost Center",
				"cost_center_name": doc.name,
				"parent_cost_center":get_parent_cost_center,
				"company":doc.company,
				"is_group":0
			})
		cost_center.flags.ignore_permissions = True
		cost_center.insert()
		doc_cost_center = cost_center.name

	doc.cost_center = doc_cost_center
	frappe.db.set_value("Branch", doc.name, "cost_center", cstr(doc_cost_center))
	frappe.db.commit()

	# ---------------------------------------------------------------------------
	# create income account
	# --------------------------------------------------------------------------- */
	if not frappe.db.get_value("Account", {"company":doc.company,"account_name":doc.name},"name"):
		account = frappe.get_doc({
				"doctype":"Account",
				"account_name": doc.name,
				"company":doc.company,
				"account_type":"Income Account",
				"parent_account": "Direct Income - {0}".format(str(frappe.db.get_value("Company", doc.company,"abbr")))
			})
		account.flags.ignore_permissions = True
		account.insert()

	# ---------------------------------------------------------------------------
	# create print heading
	# --------------------------------------------------------------------------- */
	if not frappe.db.get_value("Print Heading",{"print_heading":str(doc.name)}, "name"):
		print_heading = frappe.get_doc({
					"doctype":"Print Heading",
					"print_heading": doc.name
				})
		print_heading.flags.ignore_permissions = True
		print_heading.insert()

	# ---------------------------------------------------------------------------
	# create and set territory
	# --------------------------------------------------------------------------- */
	doc_territory = frappe.db.get_value("Territory",{"territory_name":str(doc.name)}, "name")
	if not doc_territory:
		territory = frappe.get_doc({
					"doctype":"Territory",
					"territory_name": doc.name,
					"parent_territory": 'All Territories',
					"is_permitted":1
				})
		territory.flags.ignore_permissions = True
		territory.insert()
		doc_territory = territory.name
		
	doc.territory = doc_territory
	frappe.db.set_value("Branch", doc.name, "territory", cstr(doc_territory))
	frappe.db.commit()

	# ---------------------------------------------------------------------------
	# update warehouse, cost center, write off cost center in pos profile
	# --------------------------------------------------------------------------- */
	employee_list = frappe.get_all('Employee', filters={"branch":cstr(doc.name)}, fields=['name'])
	for employee in employee_list:

		pos_profile = frappe.get_all('POS Profile', filters={"employee":cstr(employee.name)}, fields=['warehouse','cost_center','write_off_cost_center'])

		for profile in pos_profile:
			if cstr(profile.warehouse) != cstr(doc.warehouse):
				frappe.db.set_value("POS Profile", {"employee": cstr(employee.name)}, "warehouse", cstr(doc.warehouse))
				frappe.db.commit()
			if cstr(profile.cost_center) != cstr(doc.cost_center):
				frappe.db.set_value("POS Profile", {"employee": cstr(employee.name)}, "cost_center", cstr(doc.cost_center))
				frappe.db.commit()
			if cstr(profile.write_off_cost_center) != cstr(doc.cost_center):
				frappe.db.set_value("POS Profile", {"employee": cstr(employee.name)}, "write_off_cost_center", cstr(doc.cost_center))
				frappe.db.commit()
	