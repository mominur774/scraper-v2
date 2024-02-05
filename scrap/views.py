import re
import requests
import csv
import json
import random
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages

def fetch_url(request, session, url, headers, data, csv_writer, page_limit):
    try:
        template = json.loads(data)
        results = []

        for page in range(1, page_limit + 1):
            template['pagination']['page'] = page
            random_user_id = random.randint(5000, 20000)
            if not random_user_id == template['user_id']:
                template['user_id'] = random_user_id

            response = session.post(url, headers=headers, json=template)
            if response.status_code == 200:
                data = response.json()
                for item in data['data']:
                    data_dict = {}
                    for key, value in item.items():
                        data_dict[key] = value['value']
                    results.append(data_dict)
            else:
                print(f"Request failed with status code {response.status_code}")

        csv_writer.writerows(results)
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")

def index(request):
    if request.method == 'POST':
        page_limit = int(request.POST.get('page_limit'))
        curl_commands = request.POST.getlist('curl')

        # Initialize the CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="output.csv"'

        # Initialize the CSV writer
        csv_writer = csv.DictWriter(response, fieldnames=["id", "name", "lead_titles", "phone", "work_phone", "email", "email_score", "company_website",
                        "company_name", "company_phone_numbers", "lead_location", "company_size", "company_industry",
                        "company_profile_image_url", "linkedin_url", "company_id", "facebook_url", "twitter_url"])
        csv_writer.writeheader()

        with requests.Session() as session:
            for index, curl_command in enumerate(curl_commands):
                print("\n=========")
                print(f"Start task {index+1}")
                print("......")

                url_pattern = r"curl '(.*?)'"
                headers_pattern = r"-H '(.*?)'"
                data_pattern = r"--data-raw (?:\$)?'(.*?)'(?:\s|$)"

                url_match = re.search(url_pattern, curl_command, re.DOTALL)
                headers_matches = re.findall(headers_pattern, curl_command)
                data_match = re.search(data_pattern, curl_command, re.DOTALL)

                if url_match and headers_matches and data_match:
                    url = url_match.group(1)
                    headers = {key: value for header in headers_matches for key, value in [header.split(": ", 1)]}
                    data = data_match.group(1)

                    if r'[\U0001F600-\U0001F64F]':
                        data = re.sub(r'[\U0001F600-\U0001F64F]', ':[', data)
                    
                    if r"\'n\'":
                        data = data.replace(r"\'n\'", "'n'")
                    
                    if r"\'":
                        data = data.replace(r"\'", "'")

                    fetch_url(request, session, url, headers, data, csv_writer, page_limit)

                    # Add a delay if needed
                    # time.sleep(10)

                print(f"End task {index+1}")
                print("=========\n")

        print("\n=========")
        print(f"Completed")
        print("=========\n")
        return response

    return render(request, 'index.html')
