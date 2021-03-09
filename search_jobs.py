import requests, colorama, csv
from bs4 import BeautifulSoup as soup


class Scraper:

    def __init__(self, location):
        self.location = location


    def web_parsing(self):    
        try:
            req = requests.get(
                f'https://www.linkedin.com/jobs/jobs-in-{self.location}?trk=homepage-basic_intent-module-jobs&position=1&pageNum=0')
            req.raise_for_status()

            # create beautifulsoup
            page_soup = soup(req.text, 'html.parser')
            return extract_jobs(page_soup)
        except requests.HTTPError as err:
            print(colorama.Fore.RED,
                f'[!!] Something went wrong! {err}', colorama.Style.RESET_ALL)            


def scrape_write(links):
    try:
        print(colorama.Fore.YELLOW,
            f'[!] There are {len(links)} available jobs.\n',
            colorama.Style.RESET_ALL)

        with open(f'jobs_in_{place}.csv', 'w', encoding='utf-8') as f:
            headers = ['Source', 'Organization', 'Job Title', 'Location', 'Posted', 'Seniority Level',
                       'Employment Type', 'Job Function', 'Industries']
            write = csv.writer(f, dialect='excel')
            write.writerow(headers)
            
            for job_link in links:
                page_req = requests.get(job_link)
                page_req.raise_for_status()

                # Parse HTML
                job_soup = soup(page_req.text, 'html.parser')
                my_data = [job_link]

                # Topcard scraping
                for content in job_soup.findAll('div', {'class':'topcard__content-left'})[0:]:
                    # TODO: work in progress
                    #orgs = {'Default-Org' : [org.text for org in content.findAll('a', {'class':'topcard__org-name-link topcard__flavor--black-link'})],
                    #        'Flavor-Org' : [org.text for org in content.findAll('span', {'class':'topcard__flavor'})]}
                    #        
                    #if orgs['Default-Org'] == []:
                    #    my_data.append(orgs['Flavor-Org'][0])
                    #elif len(orgs['Flavor-Org']) == 2:
                    #    for org in orgs['Flavor-Org']:
                    #        my_data.append(orgs['Flavor-Org'][0])
                    #else:
                    #    for org in orgs['Default-Org']:
                    #        my_data.append(org)

                    for org in content.findAll('a', {'class':'topcard__org-name-link topcard__flavor--black-link'})[0:]:
                        my_data.append(org.text)
                    for title in content.findAll('h1', {'class':'topcard__title'})[0:]:
                        print(colorama.Fore.GREEN,
                            f'[*] {title.text}', colorama.Style.RESET_ALL)
                        my_data.append(title.text.replace(',','.'))

                    for location in content.findAll('span', {'class':'topcard__flavor topcard__flavor--bullet'})[0:]:
                        my_data.append(location.text.replace(',','.'))
                    
                    posts = {'Old': [posted.text for posted in content.findAll('span', {'class':'topcard__flavor--metadata posted-time-ago__text'})],
                             'New' : [posted.text for posted in content.findAll('span', {'class':'topcard__flavor--metadata posted-time-ago__text posted-time-ago__text--new'})]}
                    
                    if posts['New'] == []:
                        for text in posts['Old']:
                            my_data.append(text)
                    else:
                        for text in posts['New']:
                            my_data.append(text)

                    for applicant in content.findAll('span', {'class':'topcard__flavor--metadata topcard__flavor--bullet num-applicants__caption'})[0:]:
                        print(applicant.text)

                # Criteria scraping
                for criteria in job_soup.findAll('span', {'class':'job-criteria__text job-criteria__text--criteria'})[:4]:
                    my_data.append(criteria.text)    
                
                write.writerows([my_data])
    except requests.HTTPError as err:
        print(colorama.Fore.RED,
            f'[!!] Something went wrong! {err}', colorama.Style.RESET_ALL)


def extract_jobs(cursor):
    job_links = []
    for res_card in cursor.findAll("li", {"class":"result-card"})[0:]:
        for links in res_card.findAll('a', {'class':'result-card__full-card-link'})[0:]:
            job_links.append(links['href'])
    
    return scrape_write(job_links)


if __name__ == '__main__':
    colorama.init()

    place = str(input('Enter country/city/state: '))
    Scraper(place).web_parsing()