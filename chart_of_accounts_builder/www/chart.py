import frappe
from frappe.website.utils import get_comment_list

def get_context(context):
	context.accounts = frappe.get_all("Account", filters={"company": frappe.form_dict.company},
		fields=["account_name", "account_number", "name", "is_group", "parent_account", 
			"account_type", "company", "root_type", "tax_rate"], order_by="lft asc")
	
	context.stars = frappe.db.get_value("Company", frappe.form_dict.company, "stars")
	context.comment_list = get_comment_list("Company", frappe.form_dict.company)
	context.reference_doctype = "Company"
	context.reference_name = frappe.form_dict.company
	context.no_cache = True