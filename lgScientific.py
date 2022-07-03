
from bs4 import BeautifulSoup
import discord
import requests


class LgScience:
    def __init__(self, article_request):
        self.article_request = article_request
        self.article_row_dict = dict()

        self.labels = ['Title:', 'Year:', 'DOI:', 'Journal:', 'Volume:', 'Publisher:', 'Issue:', 'File size:', 'Pages:']

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
            self.article_row_dict[str(article_count)] = row_info[1].p.a['href']
            super_string = f"**ID**: {article_count}\n"

            super_string += f"**{row_info[1].p.a.contents[0]}**\n**Authors**:\n"
            try:
                super_string += row_info[0].contents[0].replace(';', '\n')
            except Exception:
                super_string += "No author info available\n"

            try:
                super_string += f"\n**Journal**: {row_info[2].p.a.contents[0]}\n"
            except Exception:
                super_string += "\nNo journal info available]\n"

            try:
                super_string += f"**File Size** {row_info[3].contents[0]}\n"
            except Exception:
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
        self.download = dict()
        self.article_title = article_HTML_table[0].find('td', 'record_title').contents[0]
        desc = ''
        for row in article_HTML_table:
            if row.contents[1].contents[0] in self.labels:
                try:
                    desc += f"**{row.contents[1].contents[0]}** {row.contents[3].a.contents[0]}\n"
                except:
                    desc += f"**{row.contents[1].contents[0]}** {row.contents[3].contents[0]}\n"
            elif row.contents[1].contents[0] == 'Download:':
                links = row.find_all('a')
                i = 0
                while i < 3:
                    self.download[links[i].contents[0]] = links[i]['href']
                    i += 1

        embed_list.append(discord.Embed(description=desc,
                                        colour=discord.Colour.random()))

        for link in self.download:
            embed_list.append(discord.Embed(description=f"**{link}**\n{self.download[link]}",
                                            colour=discord.Colour.random()))

        return self.download, embed_list
