import requests
import json
import pytz
import datetime


class Graph_Parser:
    API_URL = "https://graph.facebook.com/v3.3/"
    TEMPLATE_FILE = "template.html"

    def __init__(self, token, fanpage):
        self.fanpage = fanpage
        self.token = token
        self.posts = list()

    def get_post(self, fields, limit, next=True):
        print("Getting all posts ...")
        url = "{}{}/posts?fields={}&limit={}&access_token={}".format(self.API_URL, self.fanpage, ",".join(fields),
                                                                     limit, self.token)
        resp = requests.get(url)
        data = json.loads(resp.text)
        self.posts += data["data"]
        while next:
            try:
                url = data["paging"]["next"]
                resp = requests.get(url)
                data = json.loads(resp.text)
                self.posts += data["data"]
            except KeyError:
                break

    def collect_data(self):
        data_list = list()
        taipei = pytz.timezone("Asia/Taipei")
        count = 0
        total = len(self.posts)
        for post in self.posts:
            count += 1
            try:
                this_post = {"message": post["message"],
                             "created_time": datetime.datetime.strptime(post["created_time"],
                                                                        "%Y-%m-%dT%H:%M:%S%z").astimezone(
                                 taipei).strftime("%Y-%m-%d %H:%M"),
                             "likes": post["reactions"]["summary"]["total_count"],
                             "comments": post["comments"]["summary"]["total_count"],
                             "shares": post["shares"]["count"], }
                data_list.append(this_post)
                print("Success {} ({}/{}).".format(post["id"], count, total))
            except KeyError as e:
                print("Failed  {} ({}/{}) Field {} not Found.".format(post["id"], count, total, e))
        return data_list

    @classmethod
    def save_as_html(cls, data):
        temp = "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>"
        with open(cls.TEMPLATE_FILE, "r", encoding="utf8") as f:
            template = f.read()
        body = ""
        count = 0
        for each in data:
            count += 1
            body += temp.format(count, each["message"], each["created_time"], each["likes"], each["comments"],
                                each["shares"])
        with open("AAA.html", "w", encoding="utf8") as f:
            f.write(template.replace("{{ tbody }}", body))
        print("File \'AAA.html\' output.")


if __name__ == '__main__':
    with open("setting.json", "r", encoding="utf8") as f:
        setting = json.load(f)
    parser = Graph_Parser(setting["token"], "AAAsec")
    parser.get_post(["message", "created_time", "reactions.limit(0).summary(total_count)",
                     "comments.limit(0).summary(total_count)", "shares"], 100)
    data = parser.collect_data()
    parser.save_as_html(data)
