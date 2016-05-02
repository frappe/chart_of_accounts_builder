import frappe

def get_context(context):
	filters = {}
	if frappe.form_dict.search:
		filters = {'name': ('like', '%' + frappe.form_dict.search + '%')}

	context.charts = frappe.get_all("Company", filters=filters,
		fields=["name", "country", "forked", "submitted", "stars"],
		order_by = 'name asc', limit=20)
