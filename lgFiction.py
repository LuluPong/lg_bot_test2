
from bs4 import BeautifulSoup
import requests
import discord


class LGFiction:
    def __init__(self, book_request):
        self.book_request = book_request
        self.fict_book_rows_dict = dict()

    def aggregate(self):
        search_url = self.book_request.replace(' ', '+')
        results = requests.get(f"https://libgen.is/fiction/?q={search_url}&criteria=&language=&format=").content

        results_parsed = BeautifulSoup(results, 'html.parser')
        books_table = results_parsed.table

        book_rows = books_table.find_all('tr')
        book_rows.pop(0)

        embed_list = []

        result_num = 1
        for row in book_rows:
            row_info = row.find_all('td')
            self.fict_book_rows_dict[str(result_num)] = f"https://libgen.is{row_info[2].a['href']}"

            super_string = f"**ID**: *{result_num}*\n"
            super_string += f"***{row_info[2].a.contents[0]}***\n**Authors**: "

            try:
                for authors in row_info[0].find_all('li'):
                    super_string += f"{authors.a.contents[0]}\n"
            except:
                super_string += "No author info available\n"

            try:
                super_string += f"**Series**: {row_info[1].contents[0]}\n"
                self.book_series = row_info[1].contents[0]
            except:
                super_string += "No series info available\n"
                self.book_series = "No series info available"

            try:
                super_string += f"**Language**: {row_info[3].contents[0]}\n"
            except:
                super_string += "Language info not available\n"

            try:
                super_string += f"**File Type**: {row_info[4].contents[0].split('/')[0]}\n"
                self.book_fileType = row_info[4].contents[0].split('/')[0]
                super_string += f"**File Size**: {row_info[4].contents[0].split('/')[1]}\n"
                self.book_fileSize = row_info[4].contents[0].split('/')[1] + "\n"
            except:
                super_string += "No file type or size info available"
                self.book_fileSize = "No file size info available"
                self.book_fileType = "No file type info available"

            embed_list.append(discord.Embed(description=super_string,
                                            colour=discord.Colour.random()))

            result_num += 1
        return self.fict_book_rows_dict, embed_list

    def fetch(self, book_id):
        book_id = book_id.strip()
        book_page = requests.get(self.fict_book_rows_dict[book_id]).content

        embed_list = []

        book_html = BeautifulSoup(book_page, 'html.parser')
        book_html_table = book_html.find("table", "record")

        self.book_title = book_html_table.find("td", "record_title").contents[0]
        image = book_html.find('div', 'record_side').img['src']
        self.book_image = f"https://libgen.is{image}"

        try:
            author_list = ''
            authors = book_html_table.find('ul', 'catalog_authors')
            for author in authors.find_all('li'):
                author_list += author.a.contents[0] + "\n"
            self.book_author = author_list
        except:
            self.book_author = "No author info available"

        download_list = book_html_table.find('ul', 'record_mirrors')
        download_links = download_list.find_all('a')

        embed_list.append(discord.Embed(title=self.book_title,
                                        description=f"**Author**: {self.book_author} **Series**: {self.book_series}",
                                        colour=discord.Colour.random()).set_footer(text=f"{self.book_fileType} "
                                                                                        f"{self.book_fileSize}").
                          set_image(url=self.book_image))

        downloads = dict()
        i = 0
        while i < 2:
            downloads[download_links[i].contents[0]] = download_links[i]['href']
            embed_list.append(discord.Embed(title=download_links[i].contents[0],
                                            description=download_links[i]['href'],
                                            colour=discord.Colour.random()))
            i += 1

        return downloads, embed_list
