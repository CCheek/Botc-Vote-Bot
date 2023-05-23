# bot.py
import asyncio
import os
import discord
from discord.ext import commands
from discord.ui import Item
from dotenv import load_dotenv

load_dotenv()
token = str(os.getenv('DISCORD_TOKEN'))
server = int(os.getenv('DISCORD_GUILD'))
night_phase = True

bot = commands.Bot(command_prefix='---', intents=discord.Intents.all())
nominated_players = []
players_that_have_nominated = []


class Votes(discord.ui.View):
    def __init__(self, nominee: discord.User, *items: Item):
        super().__init__(*items, timeout=86400)
        self.nominee = nominee
        self.votes = 0
        self.playersWithVotes = []
        self.playersAgainst = []

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(content=f"The nomination on {self.nominee.mention} has ended", view=self)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, emoji="👍")
    async def first_button_callback(self, button, interaction):
        if night_phase:
            await interaction.response.send_message(f"It's currently night-time, please wait till morning.", ephemeral=True)
        else:
            if "Soulless Being" in interaction.user.roles:
                await interaction.response.send_message(f"You have already used your ghost vote, so cannot vote yes on this nomination.", ephemeral=True)
            else:
                if "Dead" in interaction.user.roles:
                    await interaction.response.send_message(f"This vote will use your ghost vote, you may not vote on any nominations besides this.", ephemeral=True)
                if not interaction.user in self.playersWithVotes:
                    await interaction.guild.get_channel(int(os.getenv('VOTING_CHANNEL'))).send(f"{interaction.user.mention} raised their hand on the nomination for {self.nominee.mention} 🖐")
                    self.playersWithVotes.append(interaction.user)
                    self.votes += 1
                    await interaction.response.defer()
                else:
                    await interaction.response.send_message(f"You've already voted yes for this nomination", ephemeral=True)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red, emoji="👎")
    async def second_button_callback(self, button, interaction):
        if night_phase:
            await interaction.response.send_message(f"It's currently night-time, please wait till morning.", ephemeral=True)
        else:
            if interaction.user in self.playersWithVotes:
                await voting_channel.send(f"{interaction.user.mention} lowered their hand their hand on the nomination for {self.nominee.mention}")
                self.playersWithVotes.remove(interaction.user)
                self.playersAgainst.append(interaction.user)
                self.votes -= 1
                await interaction.response.defer()
            elif not interaction.user in self.playersAgainst:
                await voting_channel.send(f"{interaction.user.mention} has stated that they vote against the nomination for {self.nominee.mention}")
                self.playersAgainst.append(interaction.user)
                await interaction.response.defer()
            else:
                await interaction.response.send_message(f"You've already voted no for this nomination", ephemeral=True)

    @discord.ui.button(label="Vote Count", style=discord.ButtonStyle.blurple, emoji="❓")
    async def third_button_callback(self, button, interaction):
        await interaction.guild.get_channel(int(os.getenv('VOTING_CHANNEL'))).send(f"{self.nominee.name} has {self.votes} votes")
        await interaction.response.defer()


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == server:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@bot.slash_command(name="whisper", description="Open a thread with a specific player and send a message stating as much.")
async def whisper(interaction: discord.Interaction, user: discord.User):
    if night_phase:
        await interaction.response.send(f"It's currently night-time, please wait till morning.", ephemeral=True)
    else:
        thread = await thread_channel.create_thread(name=f"{interaction.user.name} - {user.name}", type=discord.ChannelType.private_thread)
        await thread.send(f"{user.mention} {interaction.user.mention} {interaction.guild.get_role(int(os.getenv('SPECTATOR_ROLE'))).mention}")
        await thread_channel.send(f"{interaction.user.mention} opens a whisper with {user.mention}")
        await interaction.response.send_message(f"Whisper channel created successfully", ephemeral=True)


@bot.slash_command(name="nominate", description="Open a public nomination, cannot be retracted.")
async def nominate(interaction: discord.Interaction, user: discord.User):
    if night_phase:
        await interaction.response.send_message(f"It's currently night-time, please wait till morning.", ephemeral=True)
    else:
        if "Dead" in interaction.user.roles:
            await interaction.response.send_message(f"You are dead and cannot nominate, sorry.", ephemeral=True)
        else:
            if not interaction.user in players_that_have_nominated and not user in nominated_players:
                await interaction.response.send_message(f"Successful, remember you cannot nominate anymore today.", ephemeral=True)
                embed = discord.Embed(title="Nomination placed!", description=f"{interaction.user.mention} nominates {user.mention} for execution! Use the following buttons to show if you support this execution or not (not voting has the same effect as saying 'no')")
                await nominations_channel.send(content=None, embed=embed, view=Votes(user))
                players_that_have_nominated.append(interaction.user)
                nominated_players.append(user)
            elif interaction.user in players_that_have_nominated:
                await interaction.response.send_message(f"Sorry, you have already nominated today.", ephemeral=True)
            elif user in nominated_players:
                await interaction.response.send_message(f"Sorry, this player has already been nominated today.", ephemeral=True)


@bot.slash_command(name="end_day", description="Disable most commands and locks channels")
async def end_day(interaction: discord.Interaction):
    global night_phase
    night_phase = True
    await nominations_channel.set_permissions(interaction.guild.default_role, send_messages=False, create_private_threads=False, create_public_threads=False, send_messages_in_threads=False)
    await voting_channel.set_permissions(interaction.guild.default_role, send_messages=False, create_private_threads=False, create_public_threads=False, send_messages_in_threads=False)
    await thread_channel.set_permissions(interaction.guild.default_role, send_messages=False, create_private_threads=False, create_public_threads=False, send_messages_in_threads=False)
    await public_actions_channel.set_permissions(interaction.guild.default_role, send_messages=False, create_private_threads=False, create_public_threads=False, send_messages_in_threads=False)
    await interaction.response.send_message(f"Successfully ended day", ephemeral=True)


@bot.slash_command(name="start_day", description="Start day (make sure to turn off bot between days)")
async def start_day(interaction: discord.Interaction):
    global night_phase
    global nominations_channel
    global voting_channel
    global thread_channel
    global general_channel
    global public_actions_channel
    night_phase = False
    nominations_channel = interaction.guild.get_channel(int(os.getenv('NOMINATIONS_CHANNEL')))
    voting_channel = interaction.guild.get_channel(int(os.getenv('VOTING_CHANNEL')))
    thread_channel = interaction.channel
    general_channel = interaction.guild.get_channel(int(os.getenv('GENERAL_CHANNEL')))
    public_actions_channel = interaction.guild.get_channel(int(os.getenv('PUBLIC_ACTIONS_CHANNEL')))
    await nominations_channel.set_permissions(interaction.guild.default_role, send_messages=True, create_private_threads=True, create_public_threads=True, send_messages_in_threads=True)
    await voting_channel.set_permissions(interaction.guild.default_role, send_messages=True, create_private_threads=True, create_public_threads=True, send_messages_in_threads=True)
    await thread_channel.set_permissions(interaction.guild.default_role, send_messages=True, create_private_threads=True, create_public_threads=True, send_messages_in_threads=True)
    await general_channel.set_permissions(interaction.guild.default_role, send_messages=True, create_private_threads=True, create_public_threads=True, send_messages_in_threads=True)
    await public_actions_channel.set_permissions(interaction.guild.default_role, send_messages=True, create_private_threads=True, create_public_threads=True, send_messages_in_threads=True)
    await interaction.response.send_message(f"Successfully started day and set thread channel", ephemeral=True)


@bot.slash_command(name="midnight", description="Locks main channel")
async def midnight(interaction: discord.Interaction):
    await general_channel.set_permissions(interaction.guild.default_role, send_messages=False, create_private_threads=False, create_public_threads=False, send_messages_in_threads=False)
    await interaction.response.send_message(f"It is currently midnight", ephemeral=True)


bot.run(token)
