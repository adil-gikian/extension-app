from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

#rom flask_sqlalchemy import SQLAlchemy
from app import db, app


#db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
