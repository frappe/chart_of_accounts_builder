# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "chart_of_accounts_builder"
app_title = "Chart Of Accounts Builder"
app_publisher = "Frappe"
app_description = "Help users contribute Chart of Accounts"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "hello@frappe.io"
app_version = "0.0.1"
app_license = "MIT"
hide_in_installer = True

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/chart_of_accounts_builder/css/chart_of_accounts_builder.css"
# app_include_js = "/assets/chart_of_accounts_builder/js/chart_of_accounts_builder.js"

# include js, css files in header of web template
# web_include_css = "/assets/chart_of_accounts_builder/css/chart_of_accounts_builder.css"
# web_include_js = "/assets/chart_of_accounts_builder/js/chart_of_accounts_builder.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"
get_website_user_home_page = "chart_of_accounts_builder.utils.get_home_page"

website_context = {
	"brand_html": 'ERPNext Charts',
	"top_bar_items": [
		{"label": "Help", "url": "/help", "right":1},
	],
}

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "chart_of_accounts_builder.install.before_install"
# after_install = "chart_of_accounts_builder.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "chart_of_accounts_builder.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"chart_of_accounts_builder.tasks.all"
# 	],
# 	"daily": [
# 		"chart_of_accounts_builder.tasks.daily"
# 	],
# 	"hourly": [
# 		"chart_of_accounts_builder.tasks.hourly"
# 	],
# 	"weekly": [
# 		"chart_of_accounts_builder.tasks.weekly"
# 	]
# 	"monthly": [
# 		"chart_of_accounts_builder.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "chart_of_accounts_builder.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "chart_of_accounts_builder.event.get_events"
# }

fixtures = ["Custom Field"]