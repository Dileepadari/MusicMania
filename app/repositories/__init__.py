"""Data access. One module per table, each returning sqlite3.Row objects.

Every query here is parameterised. The routes never build SQL themselves.
"""
