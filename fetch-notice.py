import requests
from bs4 import BeautifulSoup
import json


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
            'View': td_elements[i + 4].select_one('a')['href'].strip() if td_elements[i + 4].select_one('a') else '',
        }
        rows.append(row)

    return rows[1:16]  # Exclude header


def add_and_update_notices(existing_notices, new_notices):
    existing_ids = {notice['Sl No'] for notice in existing_notices}
    new_notice_found = False

    for new_notice in new_notices:
        if new_notice['Sl No'] not in existing_ids:
            new_notice_found = True
            existing_notices.append(new_notice)
            print("New Notice Found:")
            print(new_notice)

    if new_notice_found:
        # Update the existing notices with new data
        with open('output.json', 'w') as json_file:
            json.dump(existing_notices, json_file, indent=2)
        print("Data has been updated.")
    else:
        print("No new notices found.")


def main():
    url = 'http://www.ranaghatcollege.org.in/notice.aspx'

    # Fetch new notices
    new_notices = fetch_notices(url)

    try:
        # Load existing notices from the JSON file
        with open('output.json', 'r') as json_file:
            existing_notices = json.load(json_file)

        # Check and update notices
        add_and_update_notices(existing_notices, new_notices)
    except FileNotFoundError:
        # If the JSON file doesn't exist, create it with the new notices
        with open('output.json', 'w') as json_file:
            json.dump(new_notices, json_file, indent=2)
        print("Data has been saved for the first time.")


if __name__ == "__main__":
    main()
