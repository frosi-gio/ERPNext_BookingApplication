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
import frappe.desk.reportview

def validate(doc, method):
	if doc.is_service_provider and not hasattr(doc, '__islocal'):
		# ---------------------------------------------------------------------------
		# create activity cost
		# --------------------------------------------------------------------------- */
		for service in doc.services:
			activity_cost = frappe.db.get_value("Activity Cost", {"employee":doc.name,"activity_type":service.service}, "name")
			
			if not activity_cost:
				activity_cost = frappe.get_doc({
						"doctype":"Activity Cost",
						"activity_type":service.service,
						"billing_rate":service.billing_rate,
						"employee":doc.name
					})
				activity_cost.flags.ignore_permissions = True
				activity_cost.insert()
			
			if activity_cost:
				frappe.db.set_value("Activity Cost", str(activity_cost), "billing_rate", service.billing_rate)
				frappe.db.commit()

		# ---------------------------------------------------------------------------
		# create price list
		# --------------------------------------------------------------------------- */
		if not frappe.db.get_value("Price List",doc.employee_name,"name"):
			create_employee_price_list(doc)
		
		# ---------------------------------------------------------------------------
		# create item price
		# --------------------------------------------------------------------------- */	
		create_update_item_price(doc)

		# ---------------------------------------------------------------------------
		# create pos profile
		# --------------------------------------------------------------------------- */
		if not frappe.db.get_value("POS Profile", {"employee":cstr(doc.employee)}, "name"):
			create_pos_profile(doc)

		doc.company = frappe.db.get_value("Branch", doc.branch, "company")
		frappe.db.set_value("Employee", cstr(doc.name), "company", frappe.db.get_value("Branch", doc.branch, "company"))
		frappe.db.commit()

		# ---------------------------------------------------------------------------
		# create sales person
		# --------------------------------------------------------------------------- */
		if not frappe.db.get_value("Sales Person", {"employee":cstr(doc.employee)}, "name"):
			create_sales_person(doc,method)

def  after_insert(doc, method):
	if doc.is_service_provider:
		# ---------------------------------------------------------------------------
		# create activity cost
		# --------------------------------------------------------------------------- */
		for service in doc.services:
			activity_cost = frappe.db.get_value("Activity Cost", {"employee":doc.name,"activity_type":service.service}, "name")
			
			if not activity_cost:
				activity_cost = frappe.get_doc({
						"doctype":"Activity Cost",
						"activity_type":service.service,
						"billing_rate":service.billing_rate,
						"employee":doc.name
					})
				activity_cost.flags.ignore_permissions = True
				activity_cost.insert()
			
			if activity_cost:
				frappe.db.set_value("Activity Cost", str(activity_cost), "billing_rate", service.billing_rate)
				frappe.db.commit()

		# ---------------------------------------------------------------------------
		# create price list
		# --------------------------------------------------------------------------- */
		if not frappe.db.get_value("Price List",doc.employee_name,"name"):
			create_employee_price_list(doc)
		
		# ---------------------------------------------------------------------------
		# create item price
		# --------------------------------------------------------------------------- */	
		create_update_item_price(doc)

		# ---------------------------------------------------------------------------
		# create pos profile
		# --------------------------------------------------------------------------- */
		if not frappe.db.get_value("POS Profile", {"employee":cstr(doc.employee)}, "name"):
			create_pos_profile(doc)

		doc.company = frappe.db.get_value("Branch", doc.branch, "company")
		frappe.db.set_value("Employee", cstr(doc.name), "company", frappe.db.get_value("Branch", doc.branch, "company"))
		frappe.db.commit()

		# ---------------------------------------------------------------------------
		# create sales person
		# --------------------------------------------------------------------------- */
		if not frappe.db.get_value("Sales Person", {"employee":cstr(doc.employee)}, "name"):
			create_sales_person(doc,method)

# ---------------------------------------------------------------------------
# create sales person
# --------------------------------------------------------------------------- */
def create_sales_person(doc,method):
	sales_person = frappe.get_doc({
			"doctype":"Sales Person",
			"sales_person_name":cstr(doc.employee_name),
			"parent_sales_person":'Sales Team',
			"employee":cstr(doc.name),
			"enabled":1,
			"is_created_from_employee":1
		})
	sales_person.flags.ignore_permissions = True
	sales_person.insert()

def on_update(doc,method):
	# ---------------------------------------------------------------------------
	# update pos profile
	# --------------------------------------------------------------------------- */
	if frappe.db.get_value("POS Profile", {"employee":cstr(doc.employee)}, "name"):
		# ---------------------------------------------------------------------------
		# update pos profile warehouse
		# --------------------------------------------------------------------------- */
		pos_profile_warehouse = frappe.db.get_value("POS Profile", {"employee": cstr(doc.name)}, "warehouse")
		branch_warehouse = frappe.db.get_value("Branch", doc.branch, "warehouse")
		if branch_warehouse != pos_profile_warehouse:
			frappe.db.set_value("POS Profile", {"employee":cstr(doc.name)}, "warehouse", cstr(branch_warehouse))
			frappe.db.commit()

		# ---------------------------------------------------------------------------
		# update pos profile item groups
		# --------------------------------------------------------------------------- */
		for service_type in doc.services_type:
			pos_profile = frappe.get_doc("POS Profile", cstr(doc.employee_name) + " - " + cstr(doc.name))
			if service_type.is_provided == "Yes":
				if len(pos_profile.item_groups) > 0:
					pos_lambda = lambda i: "Yes" if cstr(pos_profile.item_groups[i].item_group).strip() == cstr(service_type.services).strip() else "No"
					is_exist = "No"
					for j in range(len(pos_profile.item_groups)):
						is_exist = pos_lambda(j)

						if is_exist == "Yes":
							break

					if is_exist == "No":
						# Add service in pos profile
						pos_profile.append("item_groups", {"item_group":cstr(service_type.services),"doctype":"POS Item Group"})
						pos_profile.flags.ignore_permissions = True
						pos_profile.save()
							
				if len(pos_profile.item_groups) == 0:
					# Add service in pos profile
					pos_profile.append("item_groups", {"item_group":cstr(service_type.services),"doctype":"POS Item Group"})
					pos_profile.flags.ignore_permissions = True
					pos_profile.save()
			elif service_type.is_provided == "No":
				# Delete service in pos pos profile
				service_name = frappe.db.get_value("POS Item Group", {"parent":cstr(pos_profile.name), "item_group":cstr(service_type.services)}, "name")
				delete = frappe.delete_doc("POS Item Group",cstr(service_name))
				frappe.db.commit()

		# ---------------------------------------------------------------------------
		# update pos profile price list
		# --------------------------------------------------------------------------- */
		pos_profile_price_list = frappe.db.get_value("POS Profile", {"employee": cstr(doc.name)}, "selling_price_list")
		if cstr(pos_profile_price_list) != cstr(doc.employee_price_list):
			frappe.db.set_value("POS Profile", {"employee":cstr(doc.name)}, "selling_price_list", cstr(doc.employee_price_list))
			frappe.db.commit()

		# ---------------------------------------------------------------------------
		# update pos print heading
		# --------------------------------------------------------------------------- */
		pos_profile_print_heading = frappe.db.get_value("POS Profile", {"employee": cstr(doc.name)}, "select_print_heading")
		print_heading = frappe.db.get_value("Print Heading", cstr(doc.branch), "name")
		if cstr(pos_profile_print_heading) != cstr(print_heading):
			frappe.db.set_value("POS Profile", {"employee":cstr(doc.name)}, "select_print_heading", cstr(print_heading))
			frappe.db.commit()

		# ---------------------------------------------------------------------------
		# update pos write off cost center
		# --------------------------------------------------------------------------- */
		pos_profile_write_off_cost_center = frappe.db.get_value("POS Profile", {"employee": cstr(doc.name)}, "write_off_cost_center")
		branch_cost_center = frappe.db.get_value("Branch", cstr(doc.branch), "cost_center")
		if cstr(pos_profile_write_off_cost_center) != cstr(branch_cost_center):
			frappe.db.set_value("POS Profile", {"employee":cstr(doc.name)}, "write_off_cost_center", cstr(branch_cost_center))
			frappe.db.commit()

		# ---------------------------------------------------------------------------
		# update pos cost center
		# --------------------------------------------------------------------------- */
		pos_profile_cost_center = frappe.db.get_value("POS Profile", {"employee": cstr(doc.name)}, "cost_center")
		branch_cost_center = frappe.db.get_value("Branch", cstr(doc.branch), "cost_center")
		if cstr(pos_profile_cost_center) != cstr(branch_cost_center):
			frappe.db.set_value("POS Profile", {"employee":cstr(doc.name)}, "cost_center", cstr(branch_cost_center))
			frappe.db.commit()

		# ---------------------------------------------------------------------------
		# update income account
		# --------------------------------------------------------------------------- */
		pos_profile_income_account = frappe.db.get_value("POS Profile", {"employee": cstr(doc.name)}, "income_account")
		income_account = cstr(doc.branch) + " - " + frappe.db.get_value("Company", doc.company, "abbr")
		if cstr(pos_profile_income_account) != cstr(income_account):
			frappe.db.set_value("POS Profile", {"employee":cstr(doc.name)}, "income_account", cstr(income_account))
			frappe.db.commit()

		# ---------------------------------------------------------------------------
		# update pos territory
		# --------------------------------------------------------------------------- */
		pos_profile_territory = frappe.db.get_value("POS Profile", {"employee": cstr(doc.name)}, "territory")
		territory = frappe.db.get_value("Branch", cstr(doc.branch), "territory")
		if cstr(pos_profile_territory) != cstr(print_heading):
			frappe.db.set_value("POS Profile", {"employee":cstr(doc.name)}, "territory", cstr(territory))
			frappe.db.commit()

# ---------------------------------------------------------------------------
# create pos profile
# --------------------------------------------------------------------------- */
def create_pos_profile(doc):
	item_groups = []
	for service_type in doc.services_type:
		if service_type.is_provided == 'Yes':
			item_groups.append({"doctype":"POS Item Group","item_group":cstr(service_type.services)})

	pos_profile = frappe.get_doc({	
			"doctype":"POS Profile",
			"pos_profile_name": str(doc.employee_name)+ " - "+ str(doc.name),
			"naming_series":"SINV-",
			"update_stock":1,
			"ignore_pricing_rule":1,
			"allow_delete":1,
			"allow_user_to_edit_rate":1,
			"allow_user_to_edit_discount":1,
			"allow_print_before_pay":1,
			"warehouse":frappe.db.get_value("Branch", doc.branch, "warehouse"),
			"select_print_heading": str(doc.branch),
			"selling_price_list": str(doc.employee_price_list),
			"write_off_account": "Write Off - " + str(frappe.db.get_value("Company", doc.company, "abbr")),
			"write_off_cost_center": str(doc.branch) + " - " + str(frappe.db.get_value("Company", doc.company, "abbr")),
			"income_account": str(doc.branch) + " - " + str(frappe.db.get_value("Company", doc.company, "abbr")),
			"cost_center": str(doc.branch) + " - " + str(frappe.db.get_value("Company", doc.company, "abbr")),
			"employee":str(doc.name),
			"item_groups":item_groups,
			"letter_head":frappe.db.get_value("Company", doc.company, "default_letter_head"),
			"tc_name":frappe.db.get_value("Company", doc.company, "default_selling_terms"),
			"taxes_and_charges":frappe.db.get_value("Sales Taxes and Charges Template",{"is_default":1}, "name"),
			"territory":frappe.db.get_value("Branch", doc.branch, "territory")
		})

	pos_profile.flags.ignore_permissions = True
	pos_profile.insert()	

# ---------------------------------------------------------------------------
# get employee by service filter
# --------------------------------------------------------------------------- */ 
def get_employee_name_by_service(doctype, txt, searchfield, start, page_len, filters):
	cond = ''
	if filters.get('service'):
		cond = 'and `tabServices`.service = "' + filters['service'] + '"'

	if filters.get('branch'):
		cond+= 'and `tabEmployee`.branch = "' + filters['branch'] + '"'

	return frappe.db.sql("""SELECT DISTINCT `tabEmployee`.name, `tabEmployee`.employee_name FROM `tabEmployee` LEFT JOIN `tabServices` ON `tabServices`.parent = `tabEmployee`.name
		WHERE `tabEmployee`.status = 'Active' AND `tabServices`.is_provided = 'Yes'
			 {cond} 
		ORDER BY
			`tabEmployee`.name ASC
		LIMIT {start}, {page_len}""".format(
			cond=cond,
			start=start,
			page_len=page_len))

def check_if_item_exist_in_price_list(self, item):
	return frappe.db.get_value("Item Price", {"price_list":str(self.employee_price_list), "item_code":str(item)}, "name")

# ---------------------------------------------------------------------------
# create and set price list in Employee
# --------------------------------------------------------------------------- */ 
def create_employee_price_list(self):
	price_list = frappe.get_doc({
			"doctype":"Price List",
			"price_list_name":self.employee_name,
			"selling":1
		})
	price_list.flags.ignore_permissions = True
	price_list.insert()	

	self.employee_price_list = price_list.name
	frappe.db.set_value("Employee", self.name, "employee_price_list", str(price_list.name))
	frappe.db.commit()

# ---------------------------------------------------------------------------
# create and update item price in Employee
# --------------------------------------------------------------------------- */ 
def create_update_item_price(doc):
	for service in doc.services:
		if service.is_provided == "Yes":
			price_list_record_name = check_if_item_exist_in_price_list(doc,service.service)
			if price_list_record_name:
				frappe.db.set_value("Item Price", {"price_list":str(doc.employee_price_list),"item_code":str(service.service)}, "price_list_rate", service.billing_rate)
				frappe.db.commit()
			else:
				item_price = frappe.get_doc({
						"doctype":"Item Price",
						"price_list":doc.employee_price_list,
						"selling":1,
						"currency":frappe.db.get_value("Global Defaults", None, "default_currency"),
						"item_code":str(service.service),
						"price_list_rate":flt(service.billing_rate),
						"item_name":frappe.db.get_value("Item", str(service.service), "item_name"),
						"item_description":frappe.db.get_value("Item", str(service.service), "description")
					})
				item_price.flags.ignore_permissions = True
				item_price.insert()
		elif service.is_provided == "No":
			# delete item from the price list if employee is not currently provide that service(item)
			 delete = frappe.delete_doc("Item Price",frappe.db.get_value("Item Price",{"price_list":doc.employee_price_list,"item_code":service.service},"name"))

# ---------------------------------------------------------------------------
# get list of services (item)
# --------------------------------------------------------------------------- */ 
@frappe.whitelist()			
def get_service_list(item_group):
	service_list = frappe.db.sql("""SELECT name FROM `tabItem` WHERE `tabItem`.item_group=%s""",(item_group),as_dict=1)
	return service_list