import pymongo
import tornado.web, tornado.template, tornado.escape
from argon2 import PasswordHasher
from argon2 import exceptions as argonExceptions
import urllib, requests, json, secrets, time, src.mongodb_password



database_access_client = pymongo.MongoClient(
        "mongodb+srv://dumfingDBAccessor:" + src.mongodb_password.password + "@chatapp-qv8xb.gcp.mongodb.net/test?retryWrites=true&w=majority")

info = database_access_client.user_info.users.find_one()

print(info)

passwordHasher = PasswordHasher()

def login(login, unhashed_password):
    dbInfo = database_access_client.user_info.users.find_one({"email":login})
    assert dbInfo is not None
    dbPassword = dbInfo.get('password')

    print(dbPassword, dbInfo)

    passwordHasher.verify(dbPassword, unhashed_password)

    new_password = dbPassword
    if passwordHasher.check_needs_rehash(dbPassword):
        print("rehashed password")
        new_password = passwordHasher.hash(unhashed_password)
        database_access_client.user_info.users.update_one({"_id":dbInfo['_id']}, {"$set":{"password":new_password}})

    dbInfo['password'] = new_password

    return dbInfo
try:
    login("email@gmail.com", "password")
except:
    print("Login failed")


class MainHandler(tornado.web.RequestHandler):

    roomHost = None

    def get(self, *args, **kwargs):
        print("Get", str(self.request.full_url), dir(self.request))

        autologin_info = self.get_secure_cookie("login_cookie")

        if autologin_info is not None:

            login_email, autologin_key = map(tornado.escape.url_unescape, autologin_info.decode('utf-8').split('&'))

            print(login_email, autologin_key)

            existing_login_cookie = database_access_client.user_info.login_cookies.find_one({'email':login_email})

            if existing_login_cookie['cookie'] == autologin_key:
                user_info = database_access_client.user_info.users.find_one({'email':login_email})
                print(login_email, 'autologged in')
                return self.login_user(user_info)
            else:
                print('login cookie does not match', existing_login_cookie, autologin_key)
                delete_result = database_access_client.user_info.login_cookies.delete_one({'_id':existing_login_cookie['_id']})
                self.clear_cookie('login_cookie')
                print('deleted 1 entry', delete_result)

        return self.render("../static/regform.html")


    def post(self, *args, **kwargs):
        decoded_body = tornado.escape.to_unicode(self.request.body)
        body_arguments = decoded_body.split('&')
        post_request_data = dict([(tornado.escape.url_unescape(key), tornado.escape.url_unescape(value)) for key,value in map(lambda x: x.split('='), body_arguments)])
        post_method = post_request_data.get('post_request_method')

        if post_method == 'register':
            existing_user_with_email = database_access_client.user_info.users.find_one({"email":post_request_data['email']})
            if existing_user_with_email is None:

                hashed_password = passwordHasher.hash(post_request_data['password'])

                new_client_info = {'email':post_request_data['email'], 'displayname':post_request_data['username'], 'password':hashed_password, 'learn':post_request_data['learn'], 'teach':post_request_data['teach']}
                print(database_access_client.user_info.users.insert_one(new_client_info))
                print(new_client_info['password'])

                self.login_user(new_client_info)
            else:
                # user already exists
                self.render("../static/login.html")
        elif post_method == 'login':
            try:
                print(post_request_data['username'], post_request_data['password'])
                verified_user_info = login(post_request_data['username'], post_request_data['password'])

                print("roomhost:",MainHandler.roomHost)
                random_login_cookie_info = secrets.token_urlsafe(64)

                self.set_secure_cookie("login_cookie", "%s&%s"%(tornado.escape.url_escape(post_request_data['username']), random_login_cookie_info))

                login_db_entry = {'email':post_request_data['username'], 'cookie':random_login_cookie_info, 'creation_time':time.time()}

                if database_access_client.user_info.login_cookies.update_one({'email':login_db_entry['email']}, {'$set':{'cookie':random_login_cookie_info, 'creation_time':time.time()}}).modified_count == 0:
                    database_access_client.user_info.login_cookies.insert_one(login_db_entry)

                return self.login_user(verified_user_info)
            except argonExceptions.VerifyMismatchError:
                print("nope")
                self.render('../static/login.html')

    def login_user(self, user_info):

        if MainHandler.roomHost is None:
            MainHandler.roomHost = {'displayname': user_info['displayname'],
                                    'learn': user_info['learn'],
                                    'teach': user_info['teach']}
        self.render("../templates/chat.html", other_person=MainHandler.roomHost['displayname'],
                    My_Id=user_info['email'], host_learn=MainHandler.roomHost['learn'],
                    host_share=MainHandler.roomHost['teach'])