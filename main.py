# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from discord.ext import menus
import requests


class LG_Fiction:
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
            #print(row_info[2], row_info[0])
            self.fict_book_rows_dict[str(result_num)] = f"https://libgen.is{row_info[2].a['href']}"

            super_string = f"**ID**: *{result_num}*\n"
            super_string += f"***{row_info[2].a.contents[0]}***\n**Authors**: "

            try:
                #print(row_info[0])
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

            #print(super_string)
            embed_list.append(discord.Embed(description=super_string,
                                            colour=discord.Colour.random()))


            result_num += 1


        return self.fict_book_rows_dict, embed_list

    def fetch(self, book_id):
        book_id = book_id.strip()
        book_page = requests.get(self.fict_book_rows_dict[book_id]).content

        embed_list = []

        book_HTML = BeautifulSoup(book_page, 'html.parser')
        book_HTML_table = book_HTML.find("table", "record")

        self.book_title = book_HTML_table.find("td", "record_title").contents[0]
        image = book_HTML.find('div', 'record_side').img['src']
        self.book_image = f"https://libgen.is{image}"

        try:
            author_list = ''
            authors = book_HTML_table.find('ul', 'catalog_authors')
            for author in authors.find_all('li'):
                author_list += author.a.contents[0] + "\n"
            self.book_author = author_list
        except:
            self.book_author = "No author info available"

        download_list = book_HTML_table.find('ul', 'record_mirrors')
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
            #Checks if ISBN info available in table row
            try:
                if row_info[2].find(id=row_info[0].contents[0]).i.contents[0][0] == '[':
                    #Checks for editions
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

        self.book_year = table_info[13].contents[1].contents[0]
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
                           .set_footer(text=f"{self.book_fileType} ({self.book_fileSize})").set_author(name=f"ID: {book_id}"),
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

class MySource(menus.ListPageSource):
    async def format_page(self, menu, entries):
        return entries

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_dotenv()
    print("LibGen")

    intents = discord.Intents.default()
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    test = ''
    @bot.event
    async def on_ready():
        print(f"{bot.user} connected to {len(bot.guilds)} server(s)...")

    @bot.event
    async def on_command_completion(ctx):
        try:
            if ctx.command.name == 'bookid' and ctx.author == orig_requester:
                try:
                    results = request_instance.fetch(ctx.args[1])
                except:
                    results = fict_request_instance.fetch(ctx.args[1])

                formatter = MySource(results[1], per_page=1)
                menu = menus.MenuPages(formatter)
                await menu.start(ctx)
        except:
            print("bookid failed...")



    @bot.command()
    async def lg(ctx, *args):
        global request_instance, orig_requester, id_collection
        book_req = ' '.join(args[:])
        orig_requester = ctx.author
        request_instance = LG(book_req)
        search_results = request_instance.aggregate()
        id_collection = search_results[0]
        search_formatter = MySource(search_results[1], per_page=1)
        search_menu = menus.MenuPages(search_formatter)
        if len(search_results) > 0:
            mes = await ctx.author.send(embed=discord.Embed(description="Select a book: "
                                        "**!bookid ID**\neg. *!bookid 325*\n\nOnly IDs provided in"
                                        "\nthe search results will return a book.",
                                                            colour=discord.Colour.dark_red()))
            await search_menu.start(ctx, channel=mes.channel)
        else:
            await ctx.author.send(embed=discord.Embed(description="Your book request did not return any results."
                                                            "\nThis is caused by one of the following:"
                                                      "\n1) Improper spelling"
                            "\n2) Book/article not available on LibGen"
                            "\n3) Libgen temporarily unavailable\n\n"
                            "You can try searching by isbn, title, author, or publisher instead.\n\n"
                                                                  "If libgen is down, please wait at least 2 minutes"
                                                                  " and retry your request"))

    @bot.command()
    async def bookid(ctx, book_id):
        try:
            #print(id_collection.keys())
            if book_id not in list(id_collection.keys()):
                await ctx.send(embed=discord.Embed(description="Please select a valid book id.",
                                                   colour=discord.Colour.dark_red()))
        except NameError:
            await ctx.send(embed=discord.Embed(description="Please use the !lg command before. \nType **!lghelp** for the"
                                                     " directions.",
                                         colour=discord.Colour.dark_red()))

    @bot.command()
    async def lghelp(ctx):
        await ctx.send("LG_Books has sent you a DM...")
        await ctx.author.send(embed=discord.Embed(title="LG_Books Bot Guide",
                                                  description="__**Commands**__\n"
                                                              "Search by book/article: **!lg book title**\n"
                                                              "eg. *!lg excel for dummies*\n\n"
                                                              "Search by author: **!lg author**\n"
                                                              "eg. *!lg Greg harvey*\n\n"
                                                              "Search by ISBN: **!lg isbn**\n"
                                                              "eg. *!lg 9780470037379*\n\n"
                                                              "Search by publisher: **!lg publisher**\n"
                                                              "eg. *!lg Wiley*\n\n Select a book: **!bookid id**\neg. "
                                                              "*!bookid 25276*\n\n"
                                                              "See the guide/How to use/Directions: **!lghelp**\n\n"
                                                              "Requests/Inquiries/Complaints: **!lgrequest inquiry**\neg. "
                                                              "*!lgrequest why was james sitting in the giant peach tree?*"
                                                              "\nFYI: All inquiries will be sent with user info\n\n"
                                                              "__**Important Notes (Please read)**__\n"
                                                              "Searches that yield more than one result can be"
                                                              " navigated using the reaction buttons. [⏮, ◀, ▶, ⏭, ⏹]. "
                                                              "Do not worry"
                                                              " about the numbers next to the reaction buttons."
                                                              "\n⏮: *Shows top search result*\n◀: *Shows"
                                                              " previous search result (if possible)*\n▶: *Shows next "
                                                              "search result (if possible)*\n⏭: *Shows last search "
                                                              "result*\n⏹: *Freezes page, stops buttons from working*\n"
                                                              "\nSearching by title or ISBN will yield the most"
                                                              " accurate results. If your search did not work with one method, "
                                                              "try another.\n\nThe ***!bookid*** command will only"
                                                              " work if the ***!lg*** command was called before.\n\n**"
                                                              "ISBNs may vary based on the publisher, book edition, and "
                                                              "many other factors.**\n\n To reduce the number of get"
                                                              " requests sent to the site and prevent max_connection "
                                                              "errors, the bot only retrieves the first page of "
                                                              "results from the site.\n\n As of now, the bot only works for "
                                                              "__**non-fiction books**__. Functionality for fiction"
                                                              " books and scientific articles will be added later...\n\n"
                                                              "*Please remember this bot is a work in progress. Don't be afraid to "
                                                              "contact me with any suggestions, complaints, and/or questions*\n\n"
                                                              "The website used to "
                                                              "retrieve books is: *https://libgen.is*",
                                                  colour=discord.Colour.dark_red()))

    @bot.command()
    async def lgrequest(ctx, *args):
        bot_info = await bot.application_info()
        bot_owner = bot_info.owner
        await bot_owner.send(f"{ctx.author}\n\n**Inquiry**:\n{' '.join(args[:])}")
        #print(args[:] , "WHY WAS JAMES SITTING IN THE GIANT PEACH TREE?\nremember, discord has a limit for how many"
        #               "characters can be sent per message...")

    @bot.command()
    async def lgfiction(ctx, *args):
        global id_collection, fict_request_instance, orig_requester
        fict_book_req = ' '.join(args[:])
        fict_request_instance = LG_Fiction(fict_book_req)
        try:
            search_results = fict_request_instance.aggregate()
        except:
            search_results = 'null'
        if search_results != 'null':
            id_collection = search_results[0]
            fict_search_formatter = MySource(search_results[1], per_page=1)
            fict_search_menu = menus.MenuPages(fict_search_formatter)
            orig_requester = ctx.author
            await ctx.author.send(embed=discord.Embed(description="Select a bookid\n*eg. !bookid 2*",
                                                      colour=discord.Colour.dark_red()))

            await fict_search_menu.start(ctx)
        else:
            await ctx.author.send(embed=discord.Embed(description="Your book request did not return any results."
                                                            "\nThis is caused by one of the following:"
                                                      "\n1) Improper spelling"
                            "\n2) Book/article not available on LibGen"
                            "\n3) Libgen temporarily unavailable\n\n"
                            "You can try searching by isbn, title, author, or publisher instead.\n\n"
                                                                  "If libgen is down, please wait at least 2 minutes"
                                                                  " and retry your request",
                                                colour=discord.Colour.dark_red()))

    bot.run(os.getenv("TOKEN"))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
