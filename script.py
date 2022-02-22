from instagram_private_api import Client, ClientCompatPatch
from credentials import USERNAME, PASSWORD
from datetime import datetime
import csv

user_name = USERNAME
password = PASSWORD


def start_api():
    api = Client(user_name, password)
    return api


def get_following(api, id):
    following = {}
    uuid = api.generate_uuid()
    users = api.user_following(id, uuid)
    while("next_max_id" in users.keys()):
        for user in users['users']:
            following[user['pk']] = user['username']
        max_id = users["next_max_id"]
        users = api.user_following(id, uuid, max_id=max_id)

    for user in users['users']:
        following[user['pk']] = user['username']

    return following


def get_followers(api, id):
    followers = {}
    uuid = api.generate_uuid()
    users = api.user_followers(id, uuid)
    while("next_max_id" in users.keys()):
        for user in users['users']:
            followers[user['pk']] = user['username']
        max_id = users["next_max_id"]
        users = api.user_followers(id, uuid, max_id=max_id)

    for user in users['users']:
        followers[user['pk']] = user['username']

    return followers


def get_not_follow_back(following, followers):
    not_follow_back = {}
    for key, value in following.items():
        if(key not in followers.keys()):
            not_follow_back[key] = value
    return not_follow_back


def get_recent_post_date(pk):
    last_post = api.user_feed(pk, count=1)['items']
    if not last_post:
        return datetime(1, 1, 1)

    last_post_time = last_post[0]['taken_at']
    last_post_time = datetime.fromtimestamp(last_post_time)
    return last_post_time


def populate_list_recent_post(dict):
    data = []
    i = 0
    for pk, username in dict.items():
        i += 1
        recent_post_date = get_recent_post_date(pk)
        data.append([pk, username, str(recent_post_date)])
        print((i/len(dict))*100)
    return data


def write_to_file(data):
    with open(user_name + '.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "date"])
        for row in data:
            row[1] = '=HYPERLINK("https://www.instagram.com/' + \
                row[1] + '/"' + ', "' + row[1] + '")'
        writer.writerows(data)


api = start_api()
id = api.authenticated_user_id
followers = get_followers(api, id)
following = get_following(api, id)
print("Followers: " + str(len(followers)))
print("Following: " + str(len(following)))
not_follow_back = get_not_follow_back(following, followers)
print("Not follow back: " + str(len(not_follow_back)))
list_recent_post = populate_list_recent_post(following)
write_to_file(list_recent_post)
