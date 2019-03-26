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
	# ---------------------------------------------------------------------------
	# update item rate in employee service
	# --------------------------------------------------------------------------- */
	employee_list = frappe.get_all('Employee', filters={"employee_price_list":cstr(self.price_list)}, fields=['name'])
	for employee in employee_list:
		employee_service_rate = frappe.db.get_value("Services", {"parent":cstr(employee.name), "service":cstr(self.item_code)}, "billing_rate")
		if self.price_list_rate != employee_service_rate:
			frappe.db.set_value("Services", {"parent":cstr(employee.name), "service":cstr(self.item_code)}, "billing_rate", self.price_list_rate)
			frappe.db.commit()

	# ---------------------------------------------------------------------------
	# add/update item rate in all employee's price list having the same branch
	# --------------------------------------------------------------------------- */
	if self.is_from_object:
		price_list = self.price_list

		branch_by_price_list = frappe.db.get_value("Branch", str(price_list), "name")

		if branch_by_price_list:
		
			emp_price_list = frappe.get_all("Employee", filters=[["branch", "=", branch_by_price_list]],fields=["name","employee_price_list"])

			for pl in emp_price_list:
				if pl.employee_price_list:
					price_list_record_name = frappe.db.get_value("Item Price", {"price_list":str(pl.employee_price_list), "item_code":str(self.item_code)}, "name")

					if price_list_record_name:

						frappe.db.set_value("Item Price", {"price_list":str(pl.employee_price_list),"item_code":str(self.item_code)}, "price_list_rate", self.price_list_rate)
						frappe.db.commit()

					else:
						item_price = frappe.get_doc({
								"doctype":"Item Price",
								"price_list":pl.employee_price_list,
								"selling":1,
								"currency":frappe.db.get_value("Global Defaults", None, "default_currency"),
								"item_code":str(self.item_code),
								"price_list_rate":flt(self.price_list_rate),
								"item_name":frappe.db.get_value("Item", str(self.item_code), "item_name"),
								"item_description":frappe.db.get_value("Item", str(self.item_code), "description"),
								"is_from_object": 0
							})
						item_price.flags.ignore_permissions = True
						item_price.insert()




	
	
