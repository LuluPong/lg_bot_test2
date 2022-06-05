from bs4 import BeautifulSoup
import requests
import discord


class LG:
    def __init__(self, book_request):
        self.book_request = book_request
        self.book_rows_dct = dict()
        self.downloads = dict()

    def aggregate(self):
        search_url = self.book_request.replace(' ', '+')
        results = requests.get(f"https://libgen.is/search.php?req={search_url}"
                               f"&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def").content

        results_parsed = BeautifulSoup(results, 'html.parser')
        books_table = results_parsed.find_all('table')[2]

        book_rows = books_table.find_all('tr')
        book_rows.pop(0)

        embed_lists = []
        for row in book_rows:
            row_info = row.find_all('td')
            super_string = f"**ID**: *{row_info[0].contents[0]}*\n"
            super_string += f"**{row_info[2].find(id=row_info[0].contents[0]).contents[0]}**\n"
            self.book_rows_dct[row_info[0].contents[0]] = \
                f"https://libgen.is/{row_info[2].find(id=row_info[0].contents[0])['href']}"

            try:
                super_string += "**Authors**:\n"
                for author in row_info[1].find_all('a'):
                    super_string += f"   {author.contents[0]}\n"
            except:
                super_string += "No author specified\n"
            # Checks if ISBN info available in table row
            try:
                if row_info[2].find(id=row_info[0].contents[0]).i.contents[0][0] == '[':
                    # Checks for editions
                    super_string += f"**Edition and ISBN**: \n" \
                                    f"{row_info[2].find(id=row_info[0].contents[0]).i.contents[0]} " \
                                    f"{row_info[2].find(id=row_info[0].contents[0]).contents[4].i.contents[0]}\n"
                else:
                    super_string += f"**ISBN**: {row_info[2].find(id=row_info[0].contents[0]).i.contents[0]}\n"
            except:
                "No ISBN or edition info available in row\n"
            try:
                super_string += f"**Publisher**: {row_info[3].contents[0]}\n"
            except:
                super_string += "No publisher specified\n"

            try:
                super_string += f"**Year**: {row_info[4].contents[0]}\n"
            except:
                super_string += "No year information available\n"

            try:
                super_string += f"**Pages**: {row_info[5].contents[0]}\n"
            except:
                super_string += "No page count information available\n"

            try:
                super_string += f"**Lang**: {row_info[6].contents[0]}\n"
            except:
                super_string += "No language information available\n"

            try:
                super_string += f"**File Size**: {row_info[7].contents[0]}\n"
            except:
                super_string += "No file size information available\n"

            try:
                super_string += f"**File Type**: {row_info[8].contents[0]}\n"
            except:
                super_string += "No file extension information available\n"
            embed_lists.append(discord.Embed(description=super_string,
                                             colour=discord.Colour.random()))
        return self.book_rows_dct, embed_lists

    def fetch(self, book_id):
        book_id = book_id.strip()
        book_page = requests.get(self.book_rows_dct[book_id]).content

        book_html = BeautifulSoup(book_page, 'html.parser')
        book_html_table = book_html.table

        table_info = book_html_table.find_all('tr')

        if table_info[1].a.img['src'][:2] != '..':
            self.book_image = f"https://libgen.is{table_info[1].a.img['src']}"
        else:
            self.book_image = f"https://libgen.is{table_info[1].a.img['src'][2:]}"
        self.book_title = table_info[1].find_all('td')[9].a.contents[0]
        try:
            self.book_volume = table_info[1].find_all('td')[10].contents[1]
        except:
            self.book_volume = "No volumes"

        try:
            self.book_author = table_info[10].b.contents[0]
        except:
            self.book_author = "No author specified"
        try:
            self.book_series = table_info[11].contents[1].contents[0]
        except:
            self.book_series = "No series"
        try:
            self.book_publisher = table_info[12].contents[1].contents[0]
        except:
            self.book_publisher = "No publisher information available"

        try:
            self.book_year = table_info[13].contents[1].contents[0]
        except:
            self.book_year = "No year info available"
        try:
            self.book_edition = table_info[13].contents[4].contents[0]

        except:
            self.book_edition = "No editions"
        try:
            self.book_lang = table_info[14].contents[1].contents[0]
        except:
            self.book_lang = "No language specified"
        try:
            self.book_isbn = table_info[15].contents[1].contents[0]
        except:
            self.book_isbn = "No isbn provided"
        try:
            self.book_fileSize = table_info[18].contents[1].contents[0]
        except:
            self.book_fileSize = "No file size provided"

        try:
            self.book_fileType = table_info[18].contents[4].contents[0]
        except:
            self.book_fileType = "No file type specified"
        try:
            self.book_pageApprox = table_info[14].contents[4].contents[0]
        except:
            self.book_pageApprox = "Number of pages not specified"
        try:
            self.book_desc = table_info[31].td.contents[0]
        except:
            self.book_desc = "No description available"

        fetch_book = requests.get(table_info[1].a['href']).content
        fetch_book_parsed = BeautifulSoup(fetch_book, 'html.parser')

        downloads_table = fetch_book_parsed.find(id='download')

        self.downloads['BASIC'] = downloads_table.h2.a['href']

        download_alts = downloads_table.find_all('li')

        embed_lists = [discord.Embed(title=self.book_title, description=f"{self.book_author}\n"
                                                                        f"***Year***: {self.book_year}\n"
                                                                        f"{self.book_series}\n"
                                                                        f"***Edition***: {self.book_edition}\n"
                                                                        f"{self.book_isbn}",
                                     colour=discord.Colour.random()).set_image(url=self.book_image)
                       .set_footer(text=f"{self.book_fileType} ({self.book_fileSize})").set_author(
            name=f"ID: {book_id}"),
            discord.Embed(description=self.book_desc,
                          colour=discord.Colour.random()),
            discord.Embed(description=f"***Basic***:\n{self.downloads['BASIC']}",
                          colour=discord.Colour.random())]

        for download in download_alts:
            self.downloads[download.a.contents[0]] = download.a['href']
            embed_lists.append(discord.Embed(description=f"***{download.a.contents[0]}"
                                                         f"***\n{download.a['href']}\n",
                                             colour=discord.Colour.random()))

        return self.downloads, embed_lists
