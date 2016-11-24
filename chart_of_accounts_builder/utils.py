from __future__ import unicode_literals

import frappe, json, os, tarfile
from frappe import _
from frappe.utils import cint, random_string
from frappe.model.naming import append_number_if_name_exists
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts \
	import get_charts_for_country, get_account_tree_from_existing_company

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
				if not frappe.db.exists("Company", chart):
					print chart.encode('utf-8')

					company = frappe.new_doc("Company")
					company.company_name = chart
					company.country = country.name
					company.chart_of_accounts = chart
					company.abbr = country.code + str(i+1)
					company.default_currency = "USD"
					company.insert()
					frappe.db.commit()

@frappe.whitelist()
def update_account(args=None):
	frappe.local.flags.allow_unverified_charts = True
	if not args:
		args = frappe.local.form_dict
		args.pop("cmd")
	if not args.get("account_type"):
		args.account_type = None
	args.is_group = cint(args.is_group)
	account = frappe.get_doc("Account", args.name)
	account.update(args)
	account.flags.ignore_permissions = True
	if args.get("is_root"):
		account.flags.ignore_mandatory = True
	
	account.save()
	
	frappe.local.flags.allow_unverified_charts = False
	
@frappe.whitelist()
def delete_account(account):
	frappe.delete_doc("Account", account, ignore_permissions=True)

@frappe.whitelist()
def fork(company):
	ref_company = frappe.get_doc("Company", company)
	fork = create_company(ref_company.forked_from or ref_company.name, ref_company.country, 
		ref_company.default_currency, ref_company.chart_of_accounts, ref_company.name)
	
	return fork
	
def create_company(company_name, country, default_currency, chart_of_accounts, forked_from=None):
	frappe.local.flags.allow_unverified_charts = True
	
	company = frappe.new_doc("Company")
	company.country = country
	company.default_currency = default_currency
	company.chart_of_accounts = chart_of_accounts
	company.name = company_name
	company.abbr = random_string(3)
	company.forked = 1
	company.forked_from = forked_from
	company = append_number_if_name_exists(company)
	company.company_name = company.name
	
	company.flags.ignore_permissions = True
	
	company.insert(ignore_permissions=True)
	
	if frappe.local.message_log:
		frappe.local.message_log = []
		
	frappe.local.flags.allow_unverified_charts = False
	
	return company.name

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
	roots = frappe.db.sql("""select account_name, root_type from tabAccount
		where company=%s and ifnull(parent_account, '') = ''""", company, as_dict=1)
	if len(roots) < 4:
		frappe.throw(_("Number of root accounts cannot be less than 4"))

	for account in roots:
		if not account.root_type:
			frappe.throw(_("Please enter Root Type for {0}").format(account.account_name))
		elif account.root_type not in ("Asset", "Liability", "Expense", "Income", "Equity"):
			frappe.throw(_("Root Type for {0} must be one of the Asset, Liability, Income, Expense and Equity").format(account.account_name))

def validate_account_types(company):
	account_types_for_ledger = ["Cost of Goods Sold", "Depreciation", "Expenses Included In Valuation",
		"Fixed Asset", "Payable", "Receivable", "Stock Adjustment", "Stock Received But Not Billed"]

	for account_type in account_types_for_ledger:
		if not frappe.db.get_value("Account",
			{"company": company, "account_type": account_type, "is_group": 0}):

			frappe.throw(_("Please identify / create {0} Account (Ledger)").format(account_type))
			
	account_types_for_group = ["Bank", "Cash", "Stock"]

	for account_type in account_types_for_group:
		if not frappe.db.get_value("Account",
			{"company": company, "account_type": account_type, "is_group": 1}):

			frappe.throw(_("Please identify / create {0} Account (Group)").format(account_type))

def validate_accounts(company):
	for account in frappe.db.sql("""select name from tabAccount
		where company=%s and ifnull(parent_account, '') != '' order by lft, rgt""", company, as_dict=1):
			frappe.get_doc("Account", account.name).validate()
			

@frappe.whitelist()			
def add_star(company):
	stars_given_by = frappe.db.get_value("Company", company, "stars_given_by")
	
	if isinstance(stars_given_by, basestring):
		stars_given_by = json.loads(stars_given_by)
		
	if not stars_given_by:
		stars_given_by = []
		
	if frappe.session.user not in stars_given_by:
		stars_given_by.append(frappe.session.user)
		
	stars = len(stars_given_by)
	frappe.db.set_value("Company", company, "stars", stars)
	frappe.db.set_value("Company", company, "stars_given_by", json.dumps(stars_given_by))

	return stars

def get_home_page(user):
	return "/all_charts"

@frappe.whitelist()
def create_new_chart(country):
	frappe.local.flags.ignore_chart_of_accounts = True
	
	company = create_company(country + " - Chart of Accounts", country, "INR", None)
	
	frappe.local.flags.ignore_chart_of_accounts = False
	
	return company
	
@frappe.whitelist()	
def get_countries():
	return [d.name for d in frappe.get_all("Country")]
	

def export_submitted_coa(country=None):
	"""
		Make charts tree and export submitted charts as .json files 
		to public/files/submitted_charts
		:param country: Country name is optional
	"""
	
	filters = {"submitted": 1}
	if country:
		filters.update({"country": country})
		
	company_for_submitted_charts = frappe.get_all("Company", filters, ["name", "country"])
	
	for company in company_for_submitted_charts:
		account_tree = get_account_tree_from_existing_company(company.name)
		write_chart_to_file(account_tree, company)
		
def write_chart_to_file(account_tree, company):
	"""
		Write chart to json file and make tar file for all charts
	"""
	chart = {}
	chart["name"] = company.name
	chart["country_code"] = frappe.db.get_value("Country", company.country, "code")
	chart["tree"] = account_tree
	
	path = os.path.join(os.path.abspath(frappe.get_site_path()), "public", "files", "submitted_charts")
	frappe.create_folder(path)
	
	fpath = os.path.join(path, company.name + ".json")
	if not os.path.exists(fpath):
		with open(os.path.join(path, company.name + ".json"), "w") as f:
			f.write(json.dumps(chart, indent=4, sort_keys=True))
			
	with tarfile.open(os.path.join(path, "charts.tar.gz"), "w:gz") as tar:
		tar.add(path)