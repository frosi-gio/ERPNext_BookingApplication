# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe.utils import flt, cint, cstr, today, getdate, get_datetime, time_diff_in_hours, now
from frappe.model.naming import make_autoname
import json
from frappe import _
import frappe.defaults
from six.moves import urllib
from erpnext.accounts.utils import get_fiscal_year

def validate(self, method):
	
	add_item_to_employee(self)
	
	# Get if the item group is an activity or not.
	is_activity = frappe.db.get_value("Item Group", self.item_group, "is_activity")
	
	# Check if activity type is exist or not.
	activity_name = frappe.db.get_value("Activity Type", self.name, "name")
	
	# Create an activity type if item group is an activity and not exist.
	if is_activity and not activity_name:
		activity_type = frappe.get_doc({
				"doctype":"Activity Type",
				"activity_type":str(self.name)
			})
		activity_type.flags.ignore_permissions = True
		activity_type.insert()


# ---------------------------------------------------------------------------
# Add Item and Item group Into Employee child table , Create Activity cost
# --------------------------------------------------------------------------- */
def add_item_to_employee(self):
	
	if frappe.db.get_value("Item Group", self.item_group, "is_activity"):	
		for emp in self.service_provider:
			#check if services exist in employee or not
			if not frappe.db.get_value("Services", {"parent":cstr(emp.provider),"service":cstr(self.name)}, "name"):
				
				insert_employee = {
					"service":str(self.name),
					"billing_rate":0,
					"category":str(self.item_group),
					"is_provided":"Yes"
				}
				Employee = frappe.get_doc("Employee",emp.provider)
				Employee.append("services",insert_employee)
				Employee.flags.ignore_permissions = True
				Employee.save()
				frappe.db.commit()
				

			#check if services type exist in employee or not
			if not frappe.db.get_value("Services Type", {"parent":str(emp.provider),"services":str(self.item_group)}, "name"):
				
				insert_employee_grp = {
					"services":str(self.item_group),
					"is_provided":"Yes"
				}
				Employee = frappe.get_doc("Employee",emp.provider)
				Employee.append("services_type",insert_employee_grp)
				Employee.flags.ignore_permissions = True
				Employee.save()
				frappe.db.commit()
				

			#check if Activity cost exist of employee or not
			if not frappe.db.get_value("Activity Cost", {"employee":emp.provider,"activity_type":self.name}, "name"):					
				enter_activity_cost(self,str(emp.provider),0,str(self.name))



def enter_activity_cost(self,employee,billing_rate,activity):
	
	activity_cost = frappe.get_doc({
			"doctype":"Activity Cost",
			"activity_type":activity,
			"billing_rate":billing_rate,
			"employee":employee
		})
	activity_cost.flags.ignore_permissions = True
	activity_cost.insert()




	
	
