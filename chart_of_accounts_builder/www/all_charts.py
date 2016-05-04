import frappe

def get_context(context):
	filters = {}
	if frappe.form_dict.search:
		filters = {'name': ('like', '%' + frappe.form_dict.search + '%')}

	context.charts = frappe.get_all("Company", filters=filters,
		fields=["name", "country", "forked", "submitted", "stars", "owner"],
		order_by = 'stars desc, name asc', limit=30)

	for d in context.charts:
		d.submitted_by = frappe.db.get_value("User", d.owner, "full_name")