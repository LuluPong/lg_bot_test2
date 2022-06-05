from bs4 import BeautifulSoup
import discord
import requests

class lgScience:
    def __init__(self, article_request):
        self.article_request = article_request
        self.article_row_dict = dict()

    def aggregate(self):
        search_url = self.article_request.replace(' ', '+')
        results = requests.get(f"https://libgen.is/scimag/?q={search_url}").content

        results_parsed = BeautifulSoup(results, 'html.parser')
        article_table = results_parsed.find('table', 'catalog')

        article_rows = article_table.tbody.find_all('tr')
        embed_list = []
        article_count = 1
        for row in article_rows:
            row_info = row.find_all('td')
            #print(row_info)
            self.article_row_dict[str(article_count)] = row_info[1].p.a['href']
            super_string = f"**ID**: {article_count}\n"

            super_string += f"**{row_info[1].p.a.contents[0]}**\n**Authors**:\n"
            try:
                super_string += row_info[0].contents[0].replace(';', '\n')
            except:
                super_string += "No author info available\n"

            try:
                super_string += f"\n**Journal**: {row_info[2].p.a.contents[0]}\n"
            except:
                super_string += "\nNo journal info available]\n"

            try:
                super_string += f"**File Size** {row_info[3].contents[0]}\n"
            except:
                super_string += "No file size info available"

            embed_list.append(discord.Embed(description=super_string,
                                            colour=discord.Colour.random()))
            article_count += 1
        return self.article_row_dict, embed_list

    def fetch(self, article_id):
        article_id = article_id.strip()
        embed_list = []
        article_page = requests.get(f"https://libgen.is{self.article_row_dict[article_id]}").content

        article_HTML = BeautifulSoup(article_page, 'html.parser')

        article_HTML_table = article_HTML.table.find_all('tr')

        self.article_title = article_HTML_table[0].find('td', 'record_title').contents[0]

        try:
            self.article_authors = article_HTML_table[1].find_all('td')[1].contents[0].replace(';', '\n')
        except:
            self.article_authors = "No author info available\n"

        try:
            self.article_DOI = article_HTML_table[2].find_all('td')[1].a.contents[0]
        except:
            self.article_DOI = "No DOI info available\n"

        try:
            self.article_journal = article_HTML_table[3].find_all('td')[1].a.contents[0]
        except:
            self.article_journal = "No journal info available\n"

        try:
            self.article_publisher = article_HTML_table[4].find_all('td')[1].contents[0]
        except:
            self.article_publisher = "No publisher info available\n"

        try:
            self.article_year = article_HTML_table[5].find_all('td')[1].contents[0]
        except:
            self.article_year = "No year info available\n"

        try:
            self.article_volume = article_HTML_table[6].find_all('td')[1].contents[0]
        except:
            self.article_volume = "No volume info available\n"

        try:
            self.article_issue = article_HTML_table[7].find_all('td')[1].contents[0]
        except:
            self.article_issue = "No issue info available\n"

        try:
            self.article_pages = article_HTML_table[8].find_all('td')[1].contents[0]
        except:
            self.article_pages = "No page info available\n"

        try:
            self.article_fileSize = article_HTML_table[10].find_all('td')[1].contents[0]
        except:
            self.article_fileSize = "No size info available\n"

        desc = f"**{self.article_title}**\n**Authors**:\n{self.article_authors}\n**Journal**: {self.article_journal}\n" \
               f"(Volume {self.article_volume} Issue {self.article_issue})\n**Publisher**: {self.article_publisher}" \
               f"**DOI**: {self.article_DOI}"

        embed_list.append(discord.Embed(description=desc,
                                        colour=discord.Colour.random())
                          .set_footer(text=f"{self.article_fileSize}"))

        downloads = article_HTML_table[14].find('ul', 'record_mirrors').find_all('a')

        self.download = dict()

        i = 0
        while i < 3:
            self.download[downloads[i].contents[0]] = downloads[i]['href']
            embed_list.append(discord.Embed(description=f"**{downloads[i].contents[0]}**\n{downloads[i]['href']}"))
            i += 1

        return self.download, embed_list