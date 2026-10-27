"""Service layer: business logic that routes call into.

Services talk to the database and enforce the app's rules, but know nothing
about HTTP (requests, redirects, templates). That keeps routes thin and lets
the logic be tested without a browser.
"""
