import frappe

def get_context(context):
	# fetch all the country
	context.country = [d.name for d in frappe.db.get_all('Country')]

	filters = {
		'forked': 0
	}

	if frappe.form_dict.search:
		filters.update({
			"country": frappe.form_dict.search
		})

	# standard sample charts
	sample_charts = frappe.get_all("Company", filters=filters,
		fields=["name", "country", "forked", "submitted", "stars", "owner"])	
		
		
	# User contributed charts
	filters.update({
		"forked": 1,
		"submitted": 1
	})

	contributed_charts = frappe.get_all("Company", filters=filters,
		fields=["name", "country", "forked", "submitted", "stars", "owner", "chart_of_accounts"])

	all_charts = contributed_charts + sample_charts

	context.all_charts = sorted([d for d in all_charts],
		key=lambda rule:rule.stars, reverse=True)

	for d in context.all_charts:
		d.submitted_by = frappe.db.get_value("User", d.owner, "full_name")
		
	# User's chart
	context.my_charts = frappe.get_all("Company", filters={"owner": frappe.session.user},
		fields=["name", "country", "forked", "submitted", "stars", "owner", "chart_of_accounts_name"],
		order_by = 'name')
	
	context.no_cache = True