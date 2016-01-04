from __future__ import unicode_literals

import frappe

from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import get_charts_for_country

def setup_charts():
	frappe.local.flags.allow_unverified_charts = True

	# delete
	for company in frappe.get_all("Company"):
		if company.name != "Wind Power LLC":
			print "deleting {0}".format(company.name)
			frappe.delete_doc("Company", company.name)
			frappe.db.commit()

	for country in frappe.get_all("Country", fields=["name", "code"]):
		if country.name in countries:
			print "creating for {0}".format(country.name)

			charts = get_charts_for_country(country.name)

			for i, chart in enumerate(charts):
				company = frappe.new_doc("Company")
				company.company_name = "{0} - {1}".format(country.name, chart)
				company.country = country.name
				company.chart_of_accounts = chart
				company.abbr = country.code + str(i)
				company.default_currency = "USD"
				company.insert()
				frappe.db.commit()

countries = ("United States", "India", "Germany", "France", "Guatemala", "Nigeria")
