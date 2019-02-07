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
	if self.is_pos:
		employee = frappe.get_value("POS Profile", cstr(self.pos_profile), "employee")

		branch = frappe.db.get_value("Employee", cstr(employee), "branch")
		territory = frappe.db.get_value("Branch", cstr(branch), "territory")
		sales_person = frappe.get_value("Sales Person", {"employee":cstr(employee)}, "name")
		
		if not len(self.sales_team):
			sales_person_row = self.append('sales_team', {})
			sales_person_row.sales_person = sales_person
			sales_person_row.allocated_percentage = 100

		if not self.territory:
			self.territory = territory




	
	
