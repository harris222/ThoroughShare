import pymongo
import tornado.web, tornado.template, tornado.escape
from argon2 import PasswordHasher
import urllib, requests, json


password = urllib.parse.quote_plus("tA!0GhfyevFK0an86NNEqGiH1vpkI6kjI@VrUs4%pz7YK3%Mj")
client = pymongo.MongoClient(
        "mongodb+srv://dumfingDB:" + password + "@chatapp-qv8xb.gcp.mongodb.net/test?retryWrites=true&w=majority")

info = client.user_info.users.find_one()

print(info)

passwordHasher = PasswordHasher()


def login(login, password):
    dbInfo = client.user_info.users.find_one({"email":login})
    assert dbInfo is not None
    dbPassword = dbInfo.get('password')

    passwordHasher.verify(dbPassword, password)


    if passwordHasher.check_needs_rehash(dbPassword):
        print("rehashed password")
        client.user_info.users.update_one({"_id":dbInfo['_id']}, {"$set":{"password":passwordHasher.hash(password)}})

try:
    login("email@gmail.com", "password")
except:
    print("Login failed")



def giphy_request(num):
    duck_images = []
    for i in range(num):
        ducky_gif = requests.get("https://api.giphy.com/v1/gifs/random",
                                 params={'api_key': 'zvoWWEzkswP1j8I4BQDCMyvsnYhuNKEQ', 'tag': 'duck',
                                         'rating': 'g'})
        json_ducky_info = json.loads(ducky_gif.content.decode('utf-8'))['data']['images']['original']['url']
        duck_images.append(json_ducky_info)
    return duck_images

class MainHandler(tornado.web.RequestHandler):

    roomName = None

    def get(self, *args, **kwargs):
        #get_ducks = giphy_request(5)
        print("Get", self.request.arguments, dir(self.request))
        self.render("../static/regform.html")

    def post(self, *args, **kwargs):
        decoded_body = tornado.escape.to_unicode(self.request.body)
        body_arguments = decoded_body.split('&')
        post_request_data = dict([(tornado.escape.url_unescape(key), tornado.escape.url_unescape(value)) for key,value in map(lambda x: x.split('='), body_arguments)])
        post_method = post_request_data.get('post_request_method')

        if post_method == 'register':
            existing_user_with_email = client.user_info.users.find_one({"email":post_request_data['email']})
            if existing_user_with_email is None:

                hashed_password = passwordHasher.hash(post_request_data['password'])

                new_client_info = {'email':post_request_data['email'], 'displayname':post_request_data['username'], 'password':hashed_password, 'learn':post_request_data['learn'], 'teach':post_request_data['teach']}

                if MainHandler.roomName is None:
                    MainHandler.roomName = post_request_data['username']

                print(client.user_info.users.insert_one(new_client_info))

                self.render("../static/chat.html", other_person=MainHandler.roomName, My_Id = post_request_data['email'])
            else:
                # user already exists
                self.render("../static/regform.html")

