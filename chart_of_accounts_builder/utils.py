from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import cint, random_string
from frappe.model.naming import append_number_if_name_exists
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import get_charts_for_country

def setup_charts(delete_existing=True):
	frappe.local.flags.allow_unverified_charts = True

	# delete
	# if delete_existing:
	# 	for company in frappe.get_all("Company"):
	# 		if company.name not in ("Wind Power LLC", "Test Company"):
	# 			print "deleting {0}".format(company.name)
	# 			frappe.delete_doc("Company", company.name)
	# 			frappe.db.commit()

	print "-"*40
	for country in frappe.get_all("Country", fields=["name", "code"]):
		charts = get_charts_for_country(country.name)
		for i, chart in enumerate(charts):
			if (chart != "Standard" or country.name == "United States"):
				company_name = "{0} - {1}".format(country.name, chart)

				if not frappe.db.exists("Company", company_name):
					print company_name.encode('utf-8')

					company = frappe.new_doc("Company")
					company.company_name = company_name
					company.country = country.name
					company.chart_of_accounts = chart
					company.abbr = country.code + str(i+1)
					company.default_currency = "USD"
					company.insert()
					frappe.db.commit()

@frappe.whitelist()
def update_account(args=None):
	if not args:
		args = frappe.local.form_dict
		args.pop("cmd")
	if not args.get("account_type"):
		args.account_type = None
	args.is_group = cint(args.is_group)
	account = frappe.get_doc("Account", args.name)
	account.update(args)
	account.flags.ignore_permissions = True
	account.save()

@frappe.whitelist()
def fork(company):
	ref_company = frappe.get_doc("Company", company)
	new_company_name = ref_company.name + " - " + frappe.session.user
	new_company_abbr = random_string(3)
	
	fork = frappe.new_doc("Company")
	fork.country = ref_company.country
	fork.default_currency = ref_company.default_currency
	fork.chart_of_accounts = ref_company.chart_of_accounts
	fork.name = new_company_name
	fork.abbr = new_company_abbr
	fork.forked = 1
	
	fork = append_number_if_name_exists(fork)
	fork.company_name = fork.name
	
	fork.insert(ignore_permissions=True)
	
	if frappe.message_log:
		frappe.message_log = []
	
	return fork.name

@frappe.whitelist()
def submit_chart(company):
	validate_roots(company)
	validate_account_types(company)
	validate_accounts(company)

	frappe.db.set_value("Company", company, "submitted", 1)

	notify_frappe_team(company)

def notify_frappe_team(company):
	subject = "New Chart of Accounts {chart_name} submitted".format(chart_name=company)
	message = """
		New Chart of Accounts: {chart_name}
		Country: {country}
		Submitted By: {user}
	""".format(chart_name=company,
		country=frappe.db.get_value("Company", company, "country"),
		user=frappe.session.user)

	frappe.sendmail(recipients="developers@erpnext.com", subject=subject, message=message)

def validate_roots(company):
	roots = frappe.db.sql("""select name, root_type from tabAccount
		where company=%s and ifnull(parent_account, '') = ''""", company, as_dict=1)
	if len(roots) < 4:
		frappe.throw(_("Number of root accounts cannot be less than 4"))

	for account in roots:
		if account.root_type not in ("Asset", "Liability", "Expense", "Income", "Equity"):
			frappe.throw(_("Root account type must be one of Asset, Liability, Income, Expense and Equity"))

def validate_account_types(company):
	account_types = ["Cost of Goods Sold", "Depreciation", "Expenses Included In Valuation",
		"Fixed Asset", "Payable", "Receivable", "Stock Adjustment", "Stock Received But Not Billed"]

	for account_type in account_types:
		if not frappe.db.get_value("Account",
			{"company": company, "account_type": account_type, "is_group": 0}):

			frappe.throw(_("Please identify / create {0} account").format(account_type))

	if not frappe.db.get_value("Account", {"company": company, "account_type": "Stock", "is_group": 1}):
		frappe.throw(_("Please identify / create account group for Stock under Asset"))

def validate_accounts(company):
	for account in frappe.db.sql("""select name from tabAccount
		where company=%s and ifnull(parent_account, '') != ''""", company, as_dict=1):
			frappe.get_doc("Account", account.name).validate()

def get_home_page(user):
	return "/all_charts"
