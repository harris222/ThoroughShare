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
    dbPassword = dbInfo['password']

    passwordHasher.verify(dbPassword, password)


    if passwordHasher.check_needs_rehash(dbPassword):
        print("rehashed password")
        client.user_info.users.update_one({"_id":dbInfo['_id']}, {"$set":{"password":passwordHasher.hash(password)}})

login("email@gmail.com", "password")



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

    def get(self, *args, **kwargs):
        #get_ducks = giphy_request(5)
        print("Get", self.request.arguments, dir(self.request))
        self.render("../regform.html")

    def post(self, *args, **kwargs):
        decoded_body = tornado.escape.to_unicode(self.request.body)
        body_arguments = decoded_body.split('&')
        account_info = dict([(tornado.escape.url_unescape(key), tornado.escape.url_unescape(value)) for key,value in map(lambda x: x.split('='), body_arguments)])
        print(account_info)
        self.render("../victims.html")

