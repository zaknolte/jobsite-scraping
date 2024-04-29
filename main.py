from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import re
import json
from typing import List


class Job_Scraper():
    def __init__(self):
        self.jobs_df = pd.DataFrame()

    def append_df(self, data):
        if self.jobs_df.empty:
            self.jobs_df = pd.DataFrame(data)
        else:
            self.jobs_df = pd.concat([self.jobs_df, pd.DataFrame(data)], ignore_index=True)

    def build_url(self, site, job, location):
        site_params = {
            "linkedin": {
                "url": "https://www.linkedin.com/jobs/search/?",
                "job": "keywords=",
                "location": "location=",
                "headers": {
                    "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64; rv: 125.0) Gecko / 20100101 Firefox / 125.0",
                    "Accept": "text / html, application / xhtml + xml, application / xml;q = 0.9, image / avif, image / webp, * / *;q = 0.8",
                    "Accept-Language": "en-US, en;q = 0.5",
                    # "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Sec-GPC": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-User": "?1",
                    "TE": "trailers",
                },
            },
            "indeed": {
                "url": "https://www.indeed.com/jobs?",
                "job": "q=",
                "location": "l=",
                "headers": {
                    "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64; rv: 125.0) Gecko / 20100101 Firefox / 125.0",
                    "Accept": "text / html, application / xhtml + xml, application / xml;q = 0.9, image / avif, image / webp, * / *;q = 0.8",
                    "Accept-Language": "en-US, en;q = 0.5",
                    # "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Sec-GPC": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-User": "?1",
                    "TE": "trailers",
                }
            }
        }

        url = f"{site_params[site]['url']}{site_params[site]['job']}{job}"

        if location is not None:
            url += f"&{site_params[site]['location']}{location}"

        return url, site_params[site]["headers"]

    def get_html(self, url, **kwargs):
        r = requests.get(url, **kwargs)
        return r.text

    def parse_html(self, html):
        soup = bs(html, 'html.parser')
        return (soup)

    def scrape_linkedin(self, results):
        data = {
            "title": [],
            "company": [],
            "location": [],
            "posted": [],
            "link": []
        }

        def append_data(field, value, strip=True):
            try:
                if strip:
                    value = value.text.strip()
                data[field].append(value)
            except AttributeError:
                data[field].append("")

        for job in results.find_all("div", class_="job-search-card"):
            append_data("title", job.find("span", "sr-only"))
            append_data("company", job.find("a", "hidden-nested-link"))
            append_data("location", job.find("span", "job-search-card__location"))
            append_data("posted", job.find("time", "job-search-card__listdate")["datetime"], strip=False)
            append_data("link", job.find("a", "base-card__full-link")["href"], strip=False)

        return data

    def scrape_indeed(self, results):
        data = {
            "title": [],
            "company": [],
            "location": [],
            "posted": [],
            "link": []
        }

        for job in results["metaData"]["mosaicProviderJobCardsModel"]["results"]:
            data["title"].append(job.get("title", ""))
            data["company"].append(job.get("company", ""))
            data["location"].append(job.get("formattedLocation", ""))
            data["posted"].append(job.get("formattedRelativeTime", ""))
            data["link"].append(f'https://www.indeed.com/{job.get("viewJobLink")}' if job.get("viewJobLink") else "")

        return data

    def scrape_jobs(self, sites: List, job: str, location: str = None):
        for site in sites:
            url, headers = self.build_url(site, job, location)
            html = self.get_html(url, headers=headers)

            if site == "linkedin":
                results = self.parse_html(html)
                data = self.scrape_linkedin(results)
                self.append_df(data)

            if site == "indeed":
                results = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', html)
                if results:
                    results = json.loads(results[0])
                    data = self.scrape_indeed(results)
                    self.append_df(data)

    def write_data(self, filename):
        self.jobs_df.to_csv(filename, index=False)
