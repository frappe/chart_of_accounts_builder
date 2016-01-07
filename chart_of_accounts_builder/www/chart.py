import frappe

def get_context(context):
	context.accounts = frappe.get_all("Account", filters={"company": frappe.form_dict.company},
		fields=["account_name", "name", "is_group", "parent_account", "account_type"], order_by="lft asc")

	context.parents = [{"name": "home", "title": "All Charts"}]
