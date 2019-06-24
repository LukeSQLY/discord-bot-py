import difflib

import discord
import samp_client.client
import yaml

from discord.ext import commands

#-----------------------------------------------------------------
# VAR
#-----------------------------------------------------------------

# Odczytywanie ustawień
settings = yaml.safe_load(open("settings.yml"))
# Zmienne stałe
BOT_VER = "0.4"
# Definicja bot
bot = commands.Bot(command_prefix=settings['prefix'])

# -----------------------------------------------------------------
# FUNC
# -----------------------------------------------------------------

async def send_notification(ctx, description):
    user = bot.get_user(592316084540145673)
    embed=discord.Embed(title='**Powiadomienie**', description=description, color=0xe91616)
    embed.set_author(name=user.name,icon_url=user.avatar_url)
    await ctx.send(embed=embed)

#-----------------------------------------------------------------
# CMD
#-----------------------------------------------------------------

@commands.command()
async def sampinfo(ctx, server_address: str = 'gra.ls-rp.net:7777'):
    if ':' in server_address:
        address = server_address.split(':')
    else:
        address = (server_address, "7777")
    try:
        with samp_client.client.SampClient(address=address[0], port=address[1]) as handler:
            info = handler.get_server_info()

            embed = discord.Embed(title=f"{info.hostname}", color=0x00ff00)
            embed.add_field(name='Informacje o serwerze:', value=f'\nGraczy: **{info.players}\\{info.max_players}** \nGamemode: **{info.gamemode}**', inline=False)
            await ctx.send(embed=embed)
    except:
            embed = discord.Embed(title=f"Nie znaleziono serwera o adresie **{server_address}** bądź jest on wyłączony.", color=0xff0000)
            await ctx.send(embed=embed)
            return

@commands.command()
async def isonline(ctx, server_address: str, nickname: str):
    nickname.replace(' ', '_')
    if ':' in server_address: address = server_address.split(':')
    else: address = (server_address, "7777")

    try:
        with samp_client.client.SampClient(address=address[0], port=address[1]) as handler:
            clients = handler.get_server_clients()
            users = []

            for entity in clients:
                users.append(entity[0])

            if nickname in users:
                embed = discord.Embed(title=f"Wyniki wyszukiwania", color=0x00ff00)
                embed.add_field(name='Gracz jest na serwerze.', value=f'\nZnaleziono gracza **{nickname}** na serwerze **{server_address}**.', inline=False)
                await ctx.send(embed=embed)
            else:
                similar_nicknames = difflib.get_close_matches(nickname, users)

                if len(similar_nicknames) == 0:
                    embed = discord.Embed(title="Wyniki wyszukiwania", description="Nie znalazłem gracza o podanym nicku na serwerze, nie ma na nim również graczy o podobnych nickach.", color=0xff0000)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="Wyniki wyszukiwania", description="Nie znalazłem gracza o podanym nicku na serwerze, ale te wyniki mogą Cię zainteresować:", color=0x004c00)
                    for result in similar_nicknames:
                        embed.add_field(name="Wynik", value=f'\n**{result}**', inline=False)
                    await ctx.send(embed=embed)
    except:
        embed = discord.Embed(title=f"Nie znaleziono serwera o adresie **{server_address}** bądź jest on wyłączony!", color=0xff0000)
        await ctx.send(embed=embed)
        return

@commands.command()
async def givepermissions(ctx, id: int = 0):
    if id == 0:
        await send_notification(ctx, 'moze bys kurwa napisal komu dac uprawnienia dzbanie pierdolony')
        return
    if ctx.message.author.id in settings['owners']:
        if id in settings['owners']:
            await send_notification(ctx, 'Ten użytkownik ma już uprawnienia.')
        settings['owners'].append(id)
        with open('settings.yml', 'w') as stream:
            yaml.safe_dump(settings, stream)
        user = bot.get_user(id)
        await send_notification(ctx, f'Nadano użytkownikowi {user.name} uprawnienia do kontrolowania bota.')
    else:
        await send_notification(ctx, 'na huj sie pchasz tam gdzie nie masz uprawnien kurwo jebana')

@commands.command()
async def updatepresence(ctx, presence_type: int = 0, presence_text: str = ""):
    if ctx.message.author.id in settings['owners']:
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name=presence_text, type=presence_type))
        settings['default_activity']['name'] = presence_text
        settings['default_activity']['type'] = presence_type
        with open('settings.yml', 'w') as stream:
            yaml.safe_dump(settings, stream)

#-----------------------------------------------------------------
# BOT EVENTS
#-----------------------------------------------------------------

@bot.event
async def on_ready():
    print(f' > Uruchomiłem bota: {bot.user.name} w wersji {BOT_VER}')
    print(f' > UID bota to: {bot.user.id}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name=settings['default_activity']['name'], type=settings['default_activity']['type']))

@bot.event
async def on_message(message):
    # Pomija wiadomości wysłane przez siebie albo inne boty
    if(message.author.bot):
        return

    # Loguje wiadomość do konsoli i pliku
    print(f'[SVR: {message.guild.name} #{message.channel}] @{message.author}: {message.content}')
    with open('logs/message.log', mode='a', encoding="utf-8") as file:
        file.write(f'SVR: {message.guild.name} #{message.channel}] @{message.author}: {message.content}\n')

    await bot.process_commands(message) # Przetwarza komendy, bez tego nie działają

@bot.event
async def on_message_delete(message):
    # Pomija wiadomości wysłane przez siebie albo inne boty
    if(message.author.bot):
        return

    print(f'[DELETED][SVR: {message.guild.name} #{message.channel}] @{message.author}: {message.content}')
    with open('logs/deleted_message.log', mode='a', encoding="utf-8") as file:
        file.write(f'SVR: {message.guild.name} #{message.channel}] @{message.author}: {message.content}\n')

@bot.event
async def on_command_error(error, ctx):
    print("-------------------------------------------------\nError:", error, "\nContext:", ctx, "\n-------------------------------------------------")

#-----------------------------------------------------------------
# NAME GUARD
#-----------------------------------------------------------------

if __name__ == '__main__':
    # Komendy od SAMP -----------------------------------------------------
    bot.add_command(sampinfo)
    bot.add_command(isonline)
    # Komendy developerskie -----------------------------------------------
    bot.add_command(givepermissions)
    bot.add_command(updatepresence)
    # Uruchomienie bota
    bot.run(settings['token'])
