import requests
from bs4 import BeautifulSoup
import csv
from itertools import zip_longest

# Initialize empty lists to store data
titles, companies, locations, skills, links, salaries, requirements = [], [], [], [], [], [], []

# Set the starting page number
page_num = 0

while True:
    try:
        # Send a GET request to the specified URL
        result = requests.get(f"https://wuzzuf.net/search/jobs/?a=hpb&q=python&start={page_num}")
        result.raise_for_status()  # Raise an exception for bad responses
        src = result.content

        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(src, "lxml")
        page_limit = int(soup.find("strong").text)

        if page_num > page_limit // 15:
            break

        # Extract relevant information using BeautifulSoup
        job_titles = soup.find_all("h2", {"class": "m604qf"})
        company_name = soup.find_all("a", {"class": "css-17s97q8"})
        locations_name = soup.find_all("span", {"class": "css-5wys0k"})
        job_skills = soup.find_all("div", {"class": "css-y4udm8"})

        # Loop through the extracted data and append it to the respective lists
        for title, company, location, skill in zip(job_titles, company_name, locations_name, job_skills):
            titles.append(title.text)
            companies.append(company.text)
            locations.append(location.text)
            skills.append(skill.text)
            links.append(title.find("a").attrs["href"])

        # Increment the page number for the next iteration
        page_num += 1

    except requests.RequestException as e:
        print(f"Error in processing page {page_num}: {e}")
        break

# Iterate through the job links to get additional information
for link in links:
    try:
        result = requests.get(link)
        result.raise_for_status()

        src = result.content
        soup = BeautifulSoup(src, "lxml")

        # Extract salary information
        salary = soup.find("div", {"class": "matching-requirement-icon-container", "data-toggle": "tooltip",
                                   "data-placement": "top"})
        salaries.append(salary.text.strip() if salary else 'N/A')

        # Extract job requirements
        requirement = soup.find("span", {"itemprop": "responsibilities"}).ul
        respon_text = "| ".join(li.text for li in requirement.find_all("li"))
        requirements.append(respon_text)

    except requests.RequestException as e:
        print(f"Error in processing job link {link}: {e}")

# Save data to CSV
data = [titles, companies, locations, skills, salaries, requirements]
export_data = zip_longest(*data, fillvalue='')

# Open the CSV file in write mode and write the data
with open('jobs_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Write header row
    writer.writerow(['Title', 'Company', 'Location', 'Skills', 'Salary', "Requirements"])

    # Write data rows
    writer.writerows(export_data)

# Print a success message
print("Data has been successfully saved to 'jobs_data.csv'")
