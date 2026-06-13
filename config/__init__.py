# Use PyMySQL as the MySQLdb driver. PyMySQL is pure-Python, so it installs on
# cPanel shared hosting without the build tools mysqlclient needs. Optional in
# dev (SQLite), so a missing PyMySQL is fine there.
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass
