################################################################################################
# Author Name   : Pankaj Kumar                                                                 #
# Email Id      : pankaj.chouhan7@gmail.com                                                     #
# File Name     : solution.py                                                                  #
# Description   : Web scrapper                                                                 #
# Creation Date : 15-04-2023                                                                   #
################################################################################################
import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import ConnectionError
import sys


# This function returns the list of all the internal individual jobs url
def getUrls():
    url = 'https://www.cermati.com/karir'
    req = requests.get(url)
    if req.status_code != 200:
        print("Connection Unsuccessful status_code :" + str(req.status_code))
        sys.exit(1)
    cermatiSoup = BeautifulSoup(req.content, 'html.parser')
    tagContent = cermatiSoup.find('script', attrs={'id': 'initials'}).text.strip()
    data = json.loads(tagContent)
    contentDetails = data['smartRecruiterResult']['all']['content']
    all_links = []

    for id in range(len(contentDetails)):
        job_url = contentDetails[id]['ref']
        all_links.append(job_url)

    return all_links


# Function to return the parsed data grouped by the department in json format
def fetchJobDetails(link):
    line_items = []
    job_descriptionlist = []
    job_qualificationlist = []
    job_response = requests.get(link)
    response_data = json.loads(job_response.content)
    job_title = response_data['name']
    job_location = response_data['location']['city'] + " , " + response_data['customField'][2]['valueLabel']
    job_department = response_data['department']['label']
    job_description = response_data['jobAd']['sections']['jobDescription']['text']
    descsoup = BeautifulSoup(job_description, "html.parser")
    desc_listdata = descsoup.find_all("li")
    for data in desc_listdata:
        job_descriptionlist.append(data.text.replace(u"\u00A0", " ").replace(u"\u2019", "'"))

    job_qualifications = response_data['jobAd']['sections']['qualifications']['text']
    qualificationcsoup = BeautifulSoup(job_qualifications, "html.parser")
    qual_listdata = qualificationcsoup.find_all("li")
    for data in qual_listdata:
        job_qualificationlist.append(data.text.replace(u"\u00A0", " ").replace(u"\u2019", "'"))

    internal_json = {
        'Title': job_title,
        'Location': job_location,
        'desription': job_descriptionlist,
        'qualifications': job_qualificationlist
    }

    line_items.append(internal_json)
    if jobDetailval.get(job_department, 'NO_KEY') == 'NO_KEY':
        jobDetailval[job_department] = line_items
    else:
        jobDetailval[job_department].extend(line_items)


if __name__ == "__main__":
    links = getUrls()
    jobDetailval = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(fetchJobDetails, links)
    # Final scrapped json data
    with open("solution.json", "w") as outfile:
        json.dump(jobDetailval, outfile)
