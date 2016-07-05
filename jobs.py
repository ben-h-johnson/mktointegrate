from app.views import restClient
from flask.ext.script import Manager
from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
import imp
import os.path
from app import app, db
from datetime import datetime


manager = Manager(app)

#########################################################
#
#                    PERIODIC SYNC
#
#########################################################

# This task is run using Heroku Task Scheduler (similar to a cron job) every 5 minutes

@manager.command
def periodic_sync():
	
	# We only want to syncronize updates occurring since the last sync time
	last_sync_time = os.environ.get('LAST_SYNC', datetime.fromtimestamp(0).isoformat()))

	# To minimize duplication of API calls we will defer activities and changes occuring
	# after the sync starts to the next sync
	current_sync_time = str(datetime.now().isoformat())
	
	# 1) Get OAuth Token - Handled and managed by mktorest.py wrapper
	# 2) "Get Paging Token" (pass in timestamp from the end of last integration cycle)
	paging_token = restClient.get_paging_token(last_sync_time)
	# 3) "Get Lead Changes" (use token from (2))
	# 4) "Get Lead Activities" (use token from (2))
	# 5) Query SQL DB for updates to lead tables (or for staged/"flagged for sync" leads)
	# 6) Push changes from (3) to SQL DB
	# 7) Use "Create/update leads" to insert changes from (4) into Marketo

	# Clean up phase:
	os.environ['LAST_SYNC']=current_sync_time
	pass


#########################################################
#
#                 	  Database Jobs
#
#########################################################

# The following scripts and SQLALCHEMY-Migrate are used to fascilitate updates
# to the database model (models.py).

@manager.command
def db_create():
	db.create_all()
	if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
	    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
	    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
	else:
	    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

@manager.command
def db_downgrade():
	v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
	api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
	v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
	print('Current database version: ' + str(v))

@manager.command
def db_migrate():
	v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
	migration = SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (v+1))
	tmp_module = imp.new_module('old_model')
	old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
	exec(old_model, tmp_module.__dict__)
	script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
	open(migration, "wt").write(script)
	api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
	v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
	print('New migration saved as ' + migration)
	print('Current database version: ' + str(v))

@manager.command
def db_upgrade():
	api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
	v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
	print('Current database version: ' + str(v))


# Main
if __name__ == "__main__":
    manager.run()
