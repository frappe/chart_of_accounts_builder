from __future__ import unicode_literals

import frappe

from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import get_charts_for_country

def setup_charts(delete_existing=True):
	frappe.local.flags.allow_unverified_charts = True

	# delete
	if delete_existing:
		for company in frappe.get_all("Company"):
			if company.name not in ("Wind Power LLC", "Test Company"):
				print "deleting {0}".format(company.name)
				frappe.delete_doc("Company", company.name)
				frappe.db.commit()

	print "-"*40
	for country in frappe.get_all("Country", fields=["name", "code"]):
		charts = get_charts_for_country(country.name)
		for i, chart in enumerate(charts):
			if (chart != "Standard" or country.name == "United States"):
				company_name = "{0} - {1}".format(country.name, chart)
				
				if not frappe.db.exists("Company", company_name):
					print company_name
					
					company = frappe.new_doc("Company")
					company.company_name = company_name
					company.country = country.name
					company.chart_of_accounts = chart
					company.abbr = country.code + str(i+1)
					company.default_currency = "USD"
					company.insert()
					frappe.db.commit()