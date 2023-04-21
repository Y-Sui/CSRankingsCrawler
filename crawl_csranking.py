import os
import re
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CrawlCSRankings:
    def __init__(self, user_choice_research_interest: str = 'None', user_choice_location: str = 'None') -> None:
        config = json.load(open('config.json'))
        self.base_url = config['URL']
        self.research_areas = config['RESEARCH_AREAS']
        self.research_areas_abb = config['RESEARCH_AREAS_ABB']
        self.location_areas = config['LOCATION']
        self.location_areas_abb = config['LOCATION_ABB']

        # Set up the query parameters
        if user_choice_research_interest == 'None' or user_choice_location == 'None':
            self.get_user_choices()
        else:
            self.user_choice_research_interest = user_choice_research_interest
            self.user_choice_location = user_choice_location
    
    def get_user_choices(self):
        """Get the user's choices for research interests and location areas."""
        research_choice_map = {self.research_areas.strip().split('\n')[i]:self.research_areas_abb.split('&')[i] for i in range(len(self.research_areas_abb))}
        print('Research Interests Areas are:\n\n, ''\n'.join([ item[0].strip()+'\t\t\t\t'+item[1] for item in research_choice_map.items()]))
        self.user_choice_research_interest=input('Input your choices(e.g. nlp&arch&sec): ').lower()
        location_choice_map = {self.location_areas.strip().split('\n')[i]:self.location_areas_abb.split('&')[i] for i in range(len(self.location_areas_abb))}
        print('Location Areas are:\n\n, ''\n'.join([ item[0].strip()+'\t\t\t\t'+item[1] for item in location_choice_map.items()]))
        self.user_choice_location=input('Input your choices(e.g. us&uk&cn): ').lower()

    def crawl_cs_rankings(self, num_top_profs: int = 100):
        """Crawl the CSRankings website and extract the top professors based on the given number."""
        driver = webdriver.Chrome()
        params_url = self.user_choice_research_interest.split('&') + (self.user_choice_location.split('&'))
        url = self.base_url + '&'.join(params_url)
        driver.get(url)
        professors_data = []
        main = WebDriverWait(driver, 600).until(
            EC.presence_of_element_located((By.ID,"ranking")))
        valid_data = main.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
        print("valid_data length: {}".format(len(valid_data)))

        for i in range(0, len(valid_data), 3):
            try:
                affiliation = valid_data[i].find_elements(By.TAG_NAME, 'td')[1].find_elements(By.TAG_NAME,'span')[1].text # the first tr is the affiliation name
            except Exception as e:
                print("Error: {}, Error Index: {}".format(e, i))
            professors = valid_data[i+2].find_element(By.TAG_NAME, 'td').find_element(By.TAG_NAME,'tbody').find_elements(By.TAG_NAME, "tr") # professors list

            print("professor length of {}: {}".format(affiliation, len(professors)))

            for j in range(0, len(professors), 2):
                professor = professors[j].find_elements(By.TAG_NAME, 'td')[1]
                professor_inner_html = professor.find_element(By.XPATH, "./small | ./a[0]").get_attribute("innerHTML");
                if re.search(r'>\s*(.*?)\s*</a>', professor_inner_html):
                    professor_name = re.search(r'>\s*(.*?)\s*</a>', professor_inner_html).group(1)
                else:
                    professor_name = ""
                if re.search(r'<span class=".+?-area">(.*?)</span>', professor_inner_html):
                    professor_research_area = re.search(r'<span class=".+?-area">(.*?)</span>',professor_inner_html).group(1)
                else:
                    professor_research_area = ""
                professor_homepage = professor.find_elements(By.TAG_NAME, 'a')[1].get_attribute('href')
                professor_google_scholar = professor.find_elements(By.TAG_NAME, 'a')[2].get_attribute('href')
                professors_data.append({
                    'affiliation': affiliation,
                    'name': professor_name,
                    'research_area': professor_research_area,
                    'homepage': professor_homepage,
                    'google_scholar': professor_google_scholar
                })

                if len(professors_data)//2+1 >= num_top_profs:
                    break
        driver.quit()
        return professors_data
    
    def save_xlsx_file(self, file_path: str):
        """Save the professors data to an Excel file."""
        df = pd.DataFrame(self.crawl_cs_rankings())
        df.to_excel(file_path, index=False)
        return df
    
if __name__ == '__main__':
    cs_rankings = CrawlCSRankings("mlming&bio", "us")
    professors_data = cs_rankings.save_xlsx_file('data.xlsx')
