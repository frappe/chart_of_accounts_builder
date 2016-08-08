import frappe

def get_context(context):
	filters = {
		'forked': 0
	}
	if frappe.form_dict.search:
		filters.update({'country': ('like', '%' + frappe.form_dict.search + '%')})

	# standard sample charts
	context.sample_charts = frappe.get_all("Company", filters=filters,
		fields=["name", "country", "forked", "submitted", "stars", "owner"],
		order_by = 'stars desc, country asc')	
		
		
	# User contributed charts
	filters.update({
		"forked": 1,
		"submitted": 1
	})
	context.contributed_charts = frappe.get_all("Company", filters=filters,
		fields=["name", "country", "forked", "submitted", "stars", "owner"],
		order_by = 'stars desc, country asc')
		
	for d in context.contributed_charts:
		d.submitted_by = frappe.db.get_value("User", d.owner, "full_name")
		
	# User's WIP chart
	filters.update({
		"forked": 1,
		"submitted": 0,
		"owner": frappe.session.user
	})
	context.my_open_charts = frappe.get_all("Company", filters=filters,
		fields=["name", "country", "forked", "submitted", "stars", "owner"],
		order_by = 'name')
	
	context.no_cache = True