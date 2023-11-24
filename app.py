import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

def scrape_jobs(position, location, miles, template, pages=5):
    driver = webdriver.Chrome()

    titles = []
    companies = []
    locations = []
    links = []
    miles_list = []
    cos = []
    closing_dates = []
    direct_links = []
    jobdescription = []

    for page in range(1, pages):
        url = template.format(position, location, miles, page)
        driver.get(url)

        for i in range(1, 10):
            my_div = driver.find_elements(By.XPATH, f"/html/body/div[2]/main/div[2]/div[2]/ul/li[{str(i)}]")

            for elements in my_div:
                location_elem = elements.find_elements(By.XPATH, "./div[2]/h3/div")
                for loc in location_elem:
                    locations.append(loc.text)

                mile_elem = elements.find_elements(By.XPATH, "./div[3]/div[1]/ul/li[2]/strong")
                for mil in mile_elem:
                    miles_list.append(mil.text)
                
                closing_date = elements.find_elements(By.XPATH, "./div[3]/div[1]/ul/li[3]/strong")
                for date in closing_date:
                    closing_dates.append(date.text)

                linker = elements.find_elements(By.XPATH, "./div[1]/div[1]/h3/a")
                for lin in linker:
                    links.append(lin.get_attribute("href"))

        for link in links:
            driver.get(link)
            title = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/div[1]/h1").text
            titles.append(title)
            company = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/div[1]/h2[1]").text
            companies.append(company)
            jobdescrip = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/div[3]/div[2]").text
            jobdescription.append(jobdescrip)
            direct_linker = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/div[2]/div/a").get_attribute("href")
            direct_links.append(direct_linker)

            try:
                COS = driver.find_element(By.ID, "tier-two-sponsorship")
                cos.append("Yes")
            except NoSuchElementException:
                cos.append("No")

    driver.quit()

    return titles, companies, cos, direct_links, closing_dates, jobdescription

def main():
    st.title("NHS Job Scraper App")

    position = st.sidebar.text_input("Enter the position:")
    location = st.sidebar.text_input("Enter the location:")
    miles = st.sidebar.text_input("Enter the miles:")

    # Add multi-select box for template selection
    templates = {
        "Newest Jobs": "https://www.jobs.nhs.uk/candidate/search/results?keyword={}&location={}&distance={}&payBand=BAND_3%2CBAND_4%2CBAND_5&workingPattern=full-time%2Cpart-time&skipPhraseSuggester=true&sort=publicationDateDesc&language=en&page={}",
        "Best match": "https://www.jobs.nhs.uk/candidate/search/results?keyword={}&location={}&distance={}&payBand=BAND_3%2CBAND_4%2CBAND_5&workingPattern=full-time%2Cpart-time&skipPhraseSuggester=true&language=en&page={}"

        # Add more templates as needed
    }
    selected_templates = st.sidebar.multiselect("Select Templates", list(templates.keys()), default=["Newest Jobs"])

    if st.sidebar.button("Scrape Jobs"):
        st.text("Scraping jobs... Please wait.")

        titles, companies,cos, direct_links, closing_dates, jobdescription = [], [], [], [], [], []

        for template_key in selected_templates:
            template = templates[template_key]
            template_titles, template_companies, template_cos, template_direct_links, template_closing_dates, template_jobdescription = scrape_jobs(
                position, location, miles, template
            )
            
            titles.extend(template_titles)
            companies.extend(template_companies)
            cos.extend(template_cos)
            direct_links.extend(template_direct_links)
            closing_dates.extend(template_closing_dates)
            jobdescription.extend(template_jobdescription)

        data = {
            'Title': titles,
            'Company': companies,
            'COS': cos,
            'Direct Link': direct_links,
            'Closing Date': closing_dates,
            # 'Job Description': jobdescription
        }

        df = pd.DataFrame.from_dict(data, orient="index")
        df = df.transpose()
        # df = df.sort_values("Closing Date",ascending=False)
        st.table(df)

if __name__ == "__main__":
    main()
