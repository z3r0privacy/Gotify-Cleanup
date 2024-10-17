import argparse, requests as r, json, os
from dateutil import parser
from datetime import datetime,timedelta,timezone

def clean_messages(config, days):
    cmp_date = datetime.now(timezone.utc) - timedelta(days=days)
    url = f"{config['gotify_url']}/message"
    while True:
        res = r.get(url, headers={"X-Gotify-Key": config['gotify_client_key']})
        if not res.ok:
            raise Exception(f"request failed: {res}")
        data = res.json()

        for msg in data['messages']:
            msg_date = parser.isoparse(msg['date']).astimezone(timezone.utc)
            if msg_date < cmp_date:
                r.delete(f"{config['gotify_url']}/message/{msg['id']}", headers={"X-Gotify-Key": config['gotify_client_key']})
            
        if data['paging']['size'] < data['paging']['limit']:
            # print("size < limit")
            break
        if "next" not in data['paging'].keys():
            break
        url = data['paging']['next']
        

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Deletes all Gotify messages older than number of days specified")
    argparser.add_argument("config_file", help="Path to the config.json containing the gotify url and apikey")
    argparser.add_argument("-d", "--number-of-days", default=30, help="Messages older than the given number of days will be deleted")

    args = argparser.parse_args()

    if not os.path.exists(args.config_file):
        print(f"Could not find {args.config_file}")
        exit(1)

    config = json.load(open(args.config_file))

    clean_messages(config, args.number_of_days)
