import frappe
from frappe.website.utils import get_comment_list

def get_context(context):
	company = frappe.utils.sanitize_html(frappe.form_dict_company)
	context.accounts = frappe.get_all("Account", filters={"company": company},
		fields=["account_name", "account_number", "name", "is_group", "parent_account", 
			"account_type", "company", "root_type", "tax_rate"], order_by="lft asc")

	context.title = company
	context.stars = frappe.db.get_value("Company", company, "stars")
	context.comment_list = get_comment_list("Company", company)
	context.reference_doctype = "Company"
	context.reference_name = company
	context.no_cache = True
