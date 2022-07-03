# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from discord.ext import menus
import lgNonfiction
import lgFiction
import lgScientific


class MySource(menus.ListPageSource):
    async def format_page(self, menu, entries):
        return entries


if __name__ == '__main__':
    load_dotenv()
    print("LibGen")

    intents = discord.Intents.default()
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    no_results_msg = "Your book request did not return any results.\nThis is caused by one of the following:\n1) " \
                     "Improper spelling\n2) Book/article not available on LibGen\n3) Libgen temporarily unavailable\n" \
                     "\nYou can try searching by isbn, title, author, or publisher instead.\n\nIf libgen is down, " \
                     "please wait at least 2 minutes and retry your request"

    help_msg = "__**Commands**__\nSearch by book/article: **!lg book title**\neg. *!lg excel for dummies*\n\nSearch " \
               "by author: **!lg author**\neg. *!lg Greg harvey*\n\nSearch by ISBN: **!lg isbn**\neg. " \
               "*!lg 9780470037379*\n\nSearch by publisher: **!lg publisher**\neg. *!lg Wiley*\n\nFor fiction books, " \
               "replace *!lg* with ***!lgfiction***. For scientific articles, replace *!lg* with ***!lgsci***. ISBN searches do not " \
               "work for fiction or scientific articles; **HOWEVER**, scientific articles can be searched for by DOIs" \
               "\n\n Select a book: **!bookid id**\neg. *!bookid 25276*\nFor **scientific articles**, replace !bookid" \
               " with *!aid*\n\nSee the guide/How to use/Directions: **!lghelp**\n\nRequests/Inquiries/Complaints: " \
               "**!lgrequest inquiry**\neg. *!lgrequest why was james sitting in the giant peach tree?*\nFYI: All " \
               "inquiries will be sent with user info\n\n__**Important Notes (Please read)**__\nSearches that yield " \
               "more than one result can be navigated using the reaction buttons. [⏮, ◀, ▶, ⏭, ⏹]. Do not worry " \
               "about the numbers next to the reaction buttons.\n⏮: *Shows top search result*\n◀: *Shows previous " \
               "search result (if possible)*\n▶: *Shows next search result (if possible)*\n⏭: *Shows last search " \
               "result*\n⏹: *Freezes page, stops buttons from working*\n\nSearching by title or ISBN will yield the " \
               "most accurate results. If your search did not work with one method, try another.\n\nThe fiction " \
               "search is VERY limited. ISBN searches will not work with it.\n\nThe ***!bookid*** command will only " \
               "work if the ***!lg*** command was called before.\nSame applies for the ***!aid*** command and the " \
               "!lgsci command\n\n**ISBNs may vary based on the publisher, book edition, and many other factors.**\n" \
               "\n To reduce the number of get requests sent to the site and prevent max_connection errors, the bot " \
               "only retrieves the first page of results from the site.\n\nDon't be afraid to contact me with any " \
               "suggestions, complaints, and/or questions*\n\nThe website used to retrieve books is: " \
               "*https://libgen.is*. There are other mirrors available."


    @bot.event
    async def on_ready():
        print(f"{bot.user} connected to {len(bot.guilds)} server(s)...")


    @bot.event
    async def on_command_completion(ctx):
        try:
            if ctx.command.name == 'bookid' and ctx.author == orig_requester:
                results = ''
                try:
                    results = request_instance.fetch(ctx.args[1])
                    success_mes = 1
                except Exception:
                    results = fict_request_instance.fetch(ctx.args[1])
                    success_mes = 2

                formatter = MySource(results[1], per_page=1)
                menu = menus.MenuPages(formatter)
                await menu.start(ctx)
                if success_mes == 1:
                    print(f"{ctx.author} successfully requested {request_instance.book_title}")
                elif success_mes  == 2:
                    print(f"{ctx.author} successfully requested {fict_request_instance.book_title}")
            elif ctx.command.name == 'aid' and ctx.author == orig_requester:
                results = sci_request_instance.fetch(ctx.args[1])
                formatter = MySource(results[1], per_page=1)
                menu = menus.MenuPages(formatter)
                await menu.start(ctx)
                print(f"{ctx.author} successfully requested {sci_request_instance.article_title}")

        except Exception as e:
            print("bookid and aid failed...", e)
            id_collection = {'':''}


    @bot.command()
    async def lg(ctx, *args):
        global request_instance, orig_requester, id_collection
        book_req = ' '.join(args[:])
        orig_requester = ctx.author
        request_instance = lgNonfiction.LG(book_req)
        search_results = request_instance.aggregate()
        id_collection = search_results[0]
        search_formatter = MySource(search_results[1], per_page=1)
        search_menu = menus.MenuPages(search_formatter)
        if len(search_results) > 0:
            mes = await ctx.author.send(embed=discord.Embed(description="Select a book: **!bookid ID**\neg. "
                                                                        "*!bookid 325*\n\nOnly IDs provided in"
                                                                        "\nthe search results will return a book.",
                                                            colour=discord.Colour.dark_red()))
            await search_menu.start(ctx, channel=mes.channel)
        else:
            await ctx.author.send(embed=discord.Embed(description=no_results_msg,
                                                      colour=discord.Colour.dark_red()))


    @bot.command()
    async def lgsci(ctx, *args):
        global sci_request_instance, id_collection, orig_requester
        article_req = ' '.join(args[:])
        sci_request_instance = lgScientific.LgScience(article_req)
        search_results = sci_request_instance.aggregate()
        id_collection = search_results[0]
        orig_requester = ctx.author
        sci_search_formatter = MySource(search_results[1], per_page=1)
        sci_menu = menus.MenuPages(sci_search_formatter)

        mes = await ctx.author.send(embed=discord.Embed(description="Select an article id.\n*e.g. !aid 12*",
                                                        colour=discord.Colour.dark_red()))
        await sci_menu.start(ctx, channel=mes.channel)


    @bot.command()
    async def bookid(ctx, book_id):
        try:
            if book_id not in list(id_collection.keys()):
                await ctx.send(embed=discord.Embed(description="Please select a valid book id.",
                                                   colour=discord.Colour.dark_red()))
                print(f"{ctx.author} unsuccessful book request. Invalid book id (!aid)...")
        except NameError:
            await ctx.send(
                embed=discord.Embed(description="Please use the !lg or !lgfiction command before. \nType **!lghelp** "
                                                "for the directions.",
                                    colour=discord.Colour.dark_red()))
            print(f"{ctx.author} unsuccessful book request. Invalid command...")

    @bot.command()
    async def aid(ctx, article_id):
        try:
            if article_id not in list(id_collection.keys()):
                await ctx.author.send(embed=discord.Embed(description="Please select a valid article id.",
                                                          colour=discord.Colour.dark_red()))
                print(f"{ctx.author} unsuccessful article request. Invalid article id (!aid)...")
        except NameError:
            await ctx.author.send(embed=discord.Embed(description="Please use the !lgsci command before.\nType "
                                                                  "**!lghelp** for directions.",
                                                      colour=discord.Colour.dark_red()))
            print(f"{ctx.author} unsuccessful article request. Invalid command...")

    @bot.command()
    async def lghelp(ctx):
        await ctx.send("LG_Books has sent you a DM...")
        await ctx.author.send(embed=discord.Embed(title="LG_Books Bot Guide",
                                                  description=help_msg,
                                                  colour=discord.Colour.dark_red()))

    @bot.command()
    async def lgrequest(ctx, *args):
        bot_info = await bot.application_info()
        bot_owner = bot_info.owner
        await bot_owner.send(f"{ctx.author}\n\n**Inquiry**:\n{' '.join(args[:])}")
        # print(args[:] , "WHY WAS JAMES SITTING IN THE GIANT PEACH TREE?")


    @bot.command()
    async def lgfiction(ctx, *args):
        global id_collection, fict_request_instance, orig_requester
        fict_book_req = ' '.join(args[:])
        fict_request_instance = lgFiction.LGFiction(fict_book_req)
        try:
            search_results = fict_request_instance.aggregate()
        except Exception as e:
            print('no fiction search results aggregated')
            search_results = 'null'
        if search_results != 'null':
            id_collection = search_results[0]
            fict_search_formatter = MySource(search_results[1], per_page=1)
            fict_search_menu = menus.MenuPages(fict_search_formatter)
            orig_requester = ctx.author
            mes = await ctx.author.send(embed=discord.Embed(description="Select a bookid\n*eg. !bookid 2*",
                                                            colour=discord.Colour.dark_red()))

            await fict_search_menu.start(ctx, channel=mes.channel)
        else:
            await ctx.author.send(embed=discord.Embed(description=no_results_msg,
                                                      colour=discord.Colour.dark_red()))


    bot.run(os.getenv("TOKEN"))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
