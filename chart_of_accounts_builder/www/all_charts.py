import frappe

def get_context(context):
	context.charts = frappe.get_all("Company", fields=["name", "country", "forked", "submitted"])
