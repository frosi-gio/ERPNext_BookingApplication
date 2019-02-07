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




	
	
