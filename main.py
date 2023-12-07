import threading
import requests
from bs4 import BeautifulSoup
import json
from flask import Flask, request
from bot import TGBOT
import time

tgbot = TGBOT('6301244999:AAHme6jcAJ0bOhLUwl8IIr_AKlAWloz59fQ')

app = Flask(__name__)


@app.post('/getTgRes')
def index():
    ResMsg = ""
    data = request.get_json()
    # user data
    userFName = data['message']['from'].get(
        'first_name', '') + " " + data['message']['from'].get('last_name', '')
    userName = data['message']['from'].get('username', '')
    userID = data['message']['from'].get('id', '')
    # message data
    msg = data['message'].get('text', '')

    if msg == '/start':
        ResMsg = f"Hello {userFName},\nTo receive all impending notices from Ranaghat College, send <b>/GetNotified</b> to ensure that you are informed quickly about any upcoming official notices."

        params = {
            'chat_id': userID,
            'text': ResMsg,
            'parse_mode': 'HTML'
        }

        tgbot.sendMessage(params)
    elif msg == '/GetNotified':
        newUser = {
            "name": userFName,
            "username": userName,
            "userID": userID
        }
        add_new_user_to_json(newUser)
        ResMsg = f"This message is being sent to you because you have successfully joined the Ranaghat college notice community. From this point on, you will utilize this community to receive all future notices. Please refrain from responding on this unmonitored text channel."
        params = {
            'chat_id': userID,
            'text': ResMsg,
            'parse_mode': 'HTML'
        }

        tgbot.sendMessage(params)

    else:
        print(f"\n\nError : {msg}\n\n")

    print(type(data))
    return "Hello World!"


def fetch_notices(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    td_elements = soup.select('table td')
    num_columns = 5
    rows = []

    for i in range(0, len(td_elements), num_columns):
        row = {
            'Sl No': td_elements[i].text.strip(),
            'Subject': td_elements[i + 1].text.strip(),
            'Start Date': td_elements[i + 2].text.strip(),
            'End Date': td_elements[i + 3].text.strip(),
            'Url': "http://www.ranaghatcollege.org.in/"+td_elements[i + 4].select_one('a')['href'].strip() if td_elements[i + 4].select_one('a') else '',
        }
        rows.append(row)

    return rows[1:16]  # Exclude header


def add_and_update_notices(existing_notices, new_notices):
    existing_ids = {notice['Subject'] for notice in existing_notices}
    new_notice_found = False

    for new_notice in new_notices:
        if new_notice['Subject'] not in existing_ids:
            new_notice_found = True
            existing_notices.append(new_notice)
            print("New Notice Found:")
            send_notice_to_all_users(new_notice)
            print(new_notice)

    if new_notice_found:
        # Update the existing notices with new data
        with open('output.json', 'w') as json_file:
            json.dump(existing_notices, json_file, indent=2)
        print("Data has been updated.")
    else:
        print("No new notices found.")


def send_notice_to_all_users(new_notice):
    try:
        with open('users.json', 'r') as json_file:
            users = json.load(json_file)
    except FileNotFoundError:
        # If the file does not exist, there are no users to send messages to
        print("No users found.")
        return

    for user in users:
        user_id = user.get("userID")
        if user_id:
            ResMsg = f"<b>{new_notice['Subject']}</b>\nDate : {new_notice['Start Date']} to {new_notice['End Date']} \nPDF : {new_notice['Url']}\n"
            params = {
                'chat_id': user_id,
                'text': ResMsg,
                'parse_mode': 'HTML'
            }
            tgbot.sendMessage(params)


def main():
    while True:
        url = 'http://www.ranaghatcollege.org.in/notice.aspx'
        # Fetch new notices
        new_notices = fetch_notices(url)
        try:
            with open('output.json', 'r') as json_file:
                existing_notices = json.load(json_file)
            add_and_update_notices(existing_notices, new_notices)
        except FileNotFoundError:
            with open('output.json', 'w') as json_file:
                json.dump(new_notices, json_file, indent=2)
            print("Data has been saved for the first time.")
        time.sleep(600)


def check_and_update_user(users_list, new_user):
    user_exists = False

    for user in users_list:
        if user["userID"] == new_user["userID"]:
            user_exists = True
            # Update the existing user's information
            user.update(new_user)
    if not user_exists:
        # Add the new user to the list
        users_list.append(new_user)
    return users_list


def add_new_user_to_json(new_user):
    try:
        with open('users.json', 'r') as json_file:
            users = json.load(json_file)
    except FileNotFoundError:
        users = []
    # Check and update the user list
    updated_users = check_and_update_user(users, new_user)
    # Save the updated user list to the file
    with open('users.json', 'w') as json_file:
        json.dump(updated_users, json_file, indent=2)

    return "Successfully added new user."


if __name__ == "__main__":
    t = threading.Thread(main)
    t.daemon = True
    t.start()
    
    app.run(host='0.0.0.0', port=10000, debug=False)
