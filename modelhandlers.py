from models import User, Item, ItemCompletion, Session
from pkg_resources import StringIO
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.functions import random
import dbutils
import os
import simplejson
import tornado
import logging

logger = logging.getLogger('modelhandlers')



"""
username
item_id
<file>
"""
class ItemCompletionHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        username = self.get_argument('username')
        item_id = self.get_argument('item_id')
        try: file1 = self.request.files['file'][0]
        except: file1 = None
        final_string = ''
        session = Session()
        try:
            user = dbutils.get_or_create(session, User, username=username)
            item = dbutils.get_or_create(session, Item, item_id=item_id)
            item_completion = dbutils.get_or_create(session, ItemCompletion, item_id=item.id, user_id=user.id)

            if file1 is not None:
                original_fname = file1['filename']

                extension = os.path.splitext(original_fname)[1]
                final_filename = item_id + extension
                if not os.path.exists("./uploads"):
                    os.makedirs("./uploads")
                if not os.path.exists("./uploads/%s" % username):
                    os.makedirs("./uploads/%s" % username)
                output_file = open("./uploads/" + username + "/" + final_filename, 'wb')
                output_file.write(file1['body'])
                item_completion.file_path = "uploads/" + username + "/" + final_filename

            session.add(item_completion)
            session.commit()
            final_string = "You have crossed item " + item_id + " off your bucket list!"
        except Exception, e:
            session.rollback()
            logger.exception(e)
            final_string = "Oops!  Something went wrong.  Please try again"
        finally:
            Session.remove()
            self.finish(final_string)


"""
username
"""
class GetCompletedItemsHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        username = self.get_argument('username')

        session = Session()
        try:
            user = dbutils.get_or_create(session, User, username=username)
            item_array = []
            for item_completion in user.completed_items:
                item = item_completion.item
                info_dict = item.serialize()
                if item_completion.file_path is not None:
                    info_dict['image'] = item_completion.file_path
                else:
                    info_dict['image'] = ''
                item_array.append(info_dict)
#            completed_items = session.Query(ItemCompletion).filter()
        except Exception, e:
            session.rollback()
        Session.remove()
        self.finish(simplejson.dumps(item_array))

"""
username
"""
class CreateUserHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        username = self.get_argument('username')

        session = Session()
        try:
            user = dbutils.get_or_create(session, User, username=username)
            final_string = "User creation successful!"
        except Exception, e:
            session.rollback()
            final_string = "User creation failed."
        finally:
            Session.remove()
            self.finish(final_string)

class DefineItemHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        item_id = self.get_argument('itemid')
        description = self.get_argument('description', '')

        session = Session()
        try:
            item = dbutils.get_or_create(session, Item, item_id=item_id)
            item.description = description
            session.add(item)
            session.flush()
            session.commit()
            finish_string = "Item added"
#            completed_items = session.Query(ItemCompletion).filter()
        except Exception, e:
            session.rollback()
            finish_string = "Item not added"
        finally:
            Session.remove()
            self.finish(finish_string)


