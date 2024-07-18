import discord
from config import TOKEN
from discord import app_commands
from discord.ext import commands
from pymongo.collection import ReturnDocument
from dbClass import UserDbSetup, GetMainUser, Team, ServerDBSetup, addMemberTeamPanel, buildEmbed, detailCrosshairButton
from dbClass import deleteTeamConfirmation, createTeamView, SelectUserToReport, supprInviteMate, contentSetup, EnSavoirPlusGuideButton
import datetime
import os
from config import dbValorant
from imgDefaultEdit import crop_image, supperpose_image_preview
from imgEdit import supperpose_image
import asyncio

bot = commands.Bot(command_prefix="+", intents= discord.Intents.all())
embedsColor = "FF0000"

class Bot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.all()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('+'), intents=intents)

    async def setup_hook(self) -> None:
        self.add_view(addMemberTeamPanel())
        self.add_view(createTeamView())
        self.add_view(SelectUserToReport())
        self.add_view(EnSavoirPlusGuideButton())
        self.add_view(detailCrosshairButton())

    async def on_ready(self):

        # dbbot.botfiles.update_one({"botID":bot.user.id},{"$set":{"botname":bot.user.name}}, upsert=True)

        
        print("--------------------------------------------")
        print(f"{bot.user.name} est prêt à être utilisé!")
        print("--------------------------------------------")
        
        try:
            #SYNCRHONISATION DES COMMANDES SLASH / CONTEXT MENU
            # await syncGuilds(bot)
            synced= await bot.tree.sync()

            print(f"Synchronisé {len(synced)} commande(s)")
            print("--------------------------------------------")

        except Exception as e:
            print(e)

bot = Bot()



@bot.event
async def on_guild_join(guild:discord.Guild): #INITIALISATION DE LA DATABASE DU SERVEUR REJOINT 
    guildInstance = ServerDBSetup(server=guild)
    guildInstance.resolveDatabase()
    


@bot.event
async def on_member_join(member:discord.Member):
    userSetup = UserDbSetup(member)
    userSetup.setDefaultDB()


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Tu es en cooldown! Réessaie dans {error.retry_after:.0f} secondes", ephemeral=True)
    else:
        raise error

@bot.event
async def on_member_remove(member: discord.Member):

    userSetup = UserDbSetup(member)
    if userSetup.isInTeam():
        tag = userSetup.getTeamTag()
        teamInstance = Team(user=member, teamTag=tag, server=member.guild)
        teamInstance.memberLeaveTeam()
    
    userSetup.Update(field="isInServer", content=False)



@bot.event
async def on_message(message:discord.Message): #EVENEMENT POUR CATCH TOUS LES MESSAGES
    # print(message.content)
    return


@bot.event
async def on_voice_state_update(member:discord.Member, before, after):
    
    guild:discord.Guild= member.guild
    channel = before.channel if before.channel is not None else after.channel

    if channel.id != 1235553876136951878:
        return
    
    else:
        salonVocal = await guild.create_voice_channel(name=f'Salon de {member.global_name}', user_limit=5, category= guild.get_channel(1020311168167972944))
        await member.move_to(salonVocal)
            
        if before.channel is None and after.channel is not None:
            print(f'{member} a rejoint un salon vocal.')
            
        if before.channel is not None and after.channel is None:
            print(f'{member} a quitté un salon vocal.')




"""@bot.tree.command(name="setup", description="Setup la configuration du serveur")
@app_commands.checks.has_permissions(administrator=True)
async def setupServer(interaction: discord.Interaction, channelBienvenue: discord.TextChannel, roleBienvenue:discord.Role, channelGeneral: discord.TextChannel):
"""


@bot.tree.command(name="setrank", description="Met à jour ton rank Valorant") #modifier en "setrank"
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(rank =[
    discord.app_commands.Choice(name="Unranked", value="unranked"),
    discord.app_commands.Choice(name="Iron", value="iron"),
    discord.app_commands.Choice(name="Bronze", value="bronze"),
    discord.app_commands.Choice(name="Silver", value="silver"),
    discord.app_commands.Choice(name="Gold", value="gold"),
    discord.app_commands.Choice(name="Platinium", value="platinium"),
    discord.app_commands.Choice(name="Diamond", value="diamond"),
    discord.app_commands.Choice(name="Ascendant", value="ascendant"),
    discord.app_commands.Choice(name="Immortal", value="immortal"),
    discord.app_commands.Choice(name="Radiant", value="radiant")
])

@app_commands.choices(division =[
    discord.app_commands.Choice(name="1", value=1),
    discord.app_commands.Choice(name="2", value=2),
    discord.app_commands.Choice(name="3", value=3)
])
async def setRank(interaction: discord.Interaction, rank: discord.app_commands.Choice[str], division: discord.app_commands.Choice[int]):

    user = interaction.user
    choixRank = rank.value
    choixDivision = 0
    
    
    if division is not None:
        choixDivision = division.value
    
    if choixRank == "radiant" or choixRank =="unranked":
        await interaction.response.send_message(f"Ton rank a bien été mis à jour, tu es ``{choixRank.lower()}``", ephemeral=True)
        userDB = UserDbSetup(user=user)
        userDB.Update(field="rank", content=(choixRank,0))
        return
    

    userDB = UserDbSetup(user=user)
    userDB.Update(field="rank", content=(choixRank,choixDivision))
    await interaction.response.send_message(f"Ton rank a bien été mis a jour, tu es `{choixRank} {choixDivision}`", ephemeral=True)
    return


@bot.tree.command(name="findmate", description="Trouve un mate à travers les joueurs libres du serveur")
@app_commands.guild_only()
async def findmate(interaction: discord.Interaction):

    userDB = UserDbSetup(user=interaction.user)
    if userDB.getRank():
        embed = buildEmbed(title=f"Résultat de ta recherche ({userDB.getRank()})", content=userDB.findMate(guild=interaction.guild),
                           guild = interaction.guild, imageurl="https://media1.tenor.com/m/dG_tr_lmYHkAAAAC/looking-around.gif" if userDB.findMate(guild=interaction.guild) == "Aucun membre ne correspond à ta recherche, désolé!" else None)
    else:
        embed = buildEmbed(title=f"Rank non renseigné!", content="Communique ton rank en faisant la commande </setrank:1213576606162092052>",guild = interaction.guild)
        
    await interaction.response.send_message(embed=embed)
    return



@bot.tree.command(name="rank", description="Renvoie le rank d'un utilisateur")
@app_commands.guild_only()
async def rank(interaction: discord.Interaction, cible:discord.User= None):

    utilisateur = interaction.user
    
    if cible != None:
        utilisateur = cible

    userClass = UserDbSetup(user=utilisateur)
    if userClass.getRank():
        await interaction.response.send_message(userClass.getRank(), ephemeral=True)
    else:
        await interaction.response.send_message("`Rank non renseigné`", ephemeral=True)


@bot.tree.command(name="profile", description="Renvoie le profil d'un utilisateur")
@app_commands.guild_only()
async def profile(interaction: discord.Interaction, user:discord.User= None):

    utilisateur = interaction.user
    cible = False

    if user != None:
        utilisateur= user
        cible = True

    userClass = UserDbSetup(user=utilisateur)
    await interaction.response.send_message(userClass.getProfile(cible= cible), ephemeral=True)



@bot.tree.command(name="config", description="Config le serveur")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def config(interaction:discord.Interaction, teampanelchannel: discord.TextChannel, gamevccategorie:discord.CategoryChannel = None):

    guild= interaction.guild
    serverInstance = ServerDBSetup(server=guild)
    if gamevccategorie:
        serverInstance.updateServerDBList(listName="gamesVcCategories",elt=gamevccategorie.id, action="$addToSet") #$addToSet permet d'ajouter seulement si l'elt n'est pas dans la liste
    
    
    addMemberEmbed = buildEmbed(title="Ajouter un membre à ta team", content="Sélectionne un membre à ajouter dans ton incroyable team!",imageurl="https://i.pinimg.com/originals/10/be/fd/10befd3b64e1aafb192131771f236511.gif" ,guild=interaction.guild, displayFooter=True)
    await teampanelchannel.send(embed=addMemberEmbed, view=addMemberTeamPanel())
    await interaction.response.send_message("les données ont bien été prises en comptes.", ephemeral=True)



@bot.tree.command(name="setownerchannel", description="Définit le salon des notifications des owners des teams")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def setownerchannel(interaction: discord.Interaction, teamownerrole: discord.Role, teamownercategory: discord.CategoryChannel):

    guild = interaction.guild
    teamChannel = await interaction.guild.create_text_channel(name='👑・Team owners', category=teamownercategory)

    await teamChannel.set_permissions(teamownerrole,read_messages=True,send_messages=False, read_message_history =True)
    await teamChannel.set_permissions(guild.default_role, view_channel=False, read_messages=False, connect=False, send_messages=False)

    serverInstance = ServerDBSetup(server=interaction.guild)
    serverInstance.Update("salonTeamOwner", teamChannel.id)

    await interaction.response.send_message(f"Le salon `{teamChannel.name}` a bien été défini comme salon pour envoyer les notifications aux owners.")



@bot.tree.command(name="setteamcategory", description="Définit le salon des vocs des teams")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def setteamcategory(interaction: discord.Interaction, teamcategory: discord.CategoryChannel):

    guild = interaction.guild
    serverInstance = ServerDBSetup(server=guild)
    serverInstance.Update("teamCategory", teamcategory.id)

    await interaction.response.send_message(f"La catégorie `{teamcategory.name}` a bien été défini comme salon pour accueilir les vocs des teams.")



@bot.tree.command(name="setnotifchannel", description="Définit le salon des notifications des teams")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def setownerchannel(interaction: discord.Interaction, notifchannel : discord.TextChannel):

    serverInstance = ServerDBSetup(server=interaction.guild)
    serverInstance.Update("notifChannel", notifchannel.id)

    await interaction.response.send_message(f"Le salon `{notifchannel.name}` a bien été défini comme salon pour envoyer les notifications aux membres des teams!", ephemeral=True)


@bot.tree.command(name="ping", description="Renvoie la latence du bot")
async def ping(interaction:discord.Interaction):
    await interaction.response.send_message(f"Pong! Latence: {bot.latency*1000:.2f}ms", view=SelectUserToReport())


@bot.tree.command(name="sendreportmodal", description="Envoie le modal de report")
@app_commands.checks.has_permissions(administrator=True)
async def send(interaction:discord.Interaction, channel:discord.TextChannel = None):
    
    embed = buildEmbed(title="Report un joueur", content="Sélectionne le membre que tu veux reporter", guild=interaction.guild,
                    imageurl= "https://media3.giphy.com/media/bYaKuPHwBnrrgtiVxU/giphy.gif?cid=6c09b952lv3j6xq1qwgtr5ndfgt9i9w56yoygui1dmu1zkr4&ep=v1_internal_gif_by_id&rid=giphy.gif&ct=g")

    
    if not channel:
        await interaction.response.send_message(embed=embed, view=SelectUserToReport())
        return
    
    await interaction.channel.send(embed=embed, view=SelectUserToReport())



@bot.tree.command(name="help", description="Commande d'aide du bot")
async def help(interaction:discord.Interaction):

    embed = discord.Embed(title="Commandes du bot")
    listeCommands = bot.tree.get_commands()

    for command in listeCommands:
        commandName = command.name
        print(command.checks)
        if "has_permissions" in str(command.checks):
            commandName += " - Administrateur"

        embed.add_field(name=commandName, value=command.description, inline=False)

    embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="createteam", description="Crée ta propre team!")
@app_commands.guild_only()
async def createteam(interaction: discord.Interaction, teamname:str, teamtag:str):

    teamInstance = Team(user=interaction.user ,teamName=teamname,teamTag=teamtag, server=interaction.guild)
    userInstance = UserDbSetup(user=interaction.user)
    await interaction.response.send_message(await teamInstance.CreateTeam())


@bot.tree.command(name="setdisponible", description="Définis ta disponibilité")
@app_commands.guild_only()
async def setdispo(interaction: discord.Interaction):
    
    userInstance = UserDbSetup(user=interaction.user)
    await interaction.response.send_message(userInstance.SetDisponible(), ephemeral=True)


@bot.tree.command(name="setmain", description="Définis ton perso préféré!")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(main =[
    discord.app_commands.Choice(name="Astra", value="astra"),
    discord.app_commands.Choice(name="Breach", value="breach"),
    discord.app_commands.Choice(name="Brimstone", value="brimstone"),
    discord.app_commands.Choice(name="Chamber", value="chamber"),
    discord.app_commands.Choice(name="Cypher", value="cypher"),
    discord.app_commands.Choice(name="Fade", value="fade"),
    discord.app_commands.Choice(name="Gekko", value="gekko"),
    discord.app_commands.Choice(name="Harbor", value="harbor"),
    discord.app_commands.Choice(name="Iso", value="iso"),
    discord.app_commands.Choice(name="Jett", value="jett"),
    discord.app_commands.Choice(name="KAYO", value="kayo"),
    discord.app_commands.Choice(name="Killjoy", value="killjoy"),
    discord.app_commands.Choice(name="Neon", value="Neon"),
    discord.app_commands.Choice(name="Omen", value="omen"),
    discord.app_commands.Choice(name="Pheonix", value="pheonix"),
    discord.app_commands.Choice(name="Raze", value="raze"),
    discord.app_commands.Choice(name="Reyna", value="reyna"),
    discord.app_commands.Choice(name="Sage", value="sage"),
    discord.app_commands.Choice(name="Skye", value="skye"),
    discord.app_commands.Choice(name="Sova", value="sova"),
    discord.app_commands.Choice(name="Viper", value="viper"),
    discord.app_commands.Choice(name="Yoru", value="yoru")
])
async def setmain(interaction: discord.Interaction, main: discord.app_commands.Choice[str]):

    userInstance = UserDbSetup(user=interaction.user)
    userInstance.Update("main", main.value)
    await interaction.response.send_message(f"Ton main est maintenant `{main.name}`!", ephemeral=True)




@bot.tree.command(name="setupcontent", description="Setup les salons d'aide (maps et agents)")
@app_commands.guild_only()
@app_commands.choices(type = [
    discord.app_commands.Choice(name="Maps", value="maps"),
    discord.app_commands.Choice(name="Agents", value="agents")
])
@app_commands.checks.has_permissions(administrator=True)
async def setupcontent(interaction: discord.Interaction, type: discord.app_commands.Choice[str]):

    serverInstance = ServerDBSetup(server=interaction.guild)
    guideInstance  = contentSetup()
    await interaction.response.defer(thinking=True, ephemeral=True)    

    if type.value == "agents":
        
        await guideInstance.post_all_agents(guild=interaction.guild)
        await interaction.followup.send("Les guides des agents ont bien été créés", ephemeral=True)
        return

    await interaction.followup.send("Les guides des maps ne sont pas encore disponibles.", ephemeral=True)

@bot.tree.command(name="resolveserverdb", description="Résout les pbs de la base de donnée du serveur")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def resolvedb(interaction:discord.Interaction):

    serverClass = ServerDBSetup(server=interaction.guild)
    result = serverClass.resolveDatabase()
    await interaction.response.send_message(f"La db de `{interaction.guild.name}` a bien été résolue.", ephemeral=True)



@bot.tree.command(name="resolvememberdb", description="Résout les pbs de la base de donnée d'un utilisateur")
@app_commands.guild_only()  
@app_commands.checks.has_permissions(administrator=True)
async def resolvedb(interaction:discord.Interaction, cible: discord.Member = None):

    utilisateur = GetMainUser(interaction.user, cibleUser=cible)
    userClass = UserDbSetup(user=utilisateur)
    result = userClass.resolveDatabase()
    await interaction.response.send_message(f"La db de `{utilisateur.mention}` a bien été résolue.", ephemeral=True)
    



@bot.tree.command(name="teamlist", description="Affiche toutes les teams du serveur")
@app_commands.guild_only()
async def teamlist(interaction: discord.Interaction):

    guild = interaction.guild
    teamInstance =  await Team(user=None, teamTag=None, server=interaction.guild)
    
    teamListEmbed = discord.Embed(title=f"Liste des teams", description= teamInstance.TeamList())
    teamListEmbed.set_footer(text=guild.name, icon_url=guild.icon)
    await interaction.response.send_message(embed= teamListEmbed)



@bot.tree.command(name="myteam", description="Affiche les informations de ta team")
@app_commands.guild_only()
async def myteam(interaction: discord.Interaction):

    userInstance = UserDbSetup(user=interaction.user)
    
    team = await userInstance.MyTeam(server=interaction.guild)
    
    if team!= None:
        
        responseEmbed = discord.Embed(title=f"{team[2].capitalize()} - {team[0]}", description=team[1], timestamp=datetime.datetime.now())
        responseEmbed.set_footer(icon_url=interaction.guild.icon, text=interaction.guild.name)

        return await interaction.response.send_message(embed=responseEmbed)

    await interaction.response.send_message("Tu n'es dans aucune team! Fais </jointeam:1090990838131200091> pour en rejoindre une!", ephemeral=True)



@bot.tree.command(name="mate", description="Crée une invite dans ton salon vocal et paramètre-la")
@app_commands.guild_only()
@app_commands.checks.cooldown(1, 60, key=lambda i: (i.user.id))
@app_commands.choices(pénalitérank =[
    discord.app_commands.Choice(name="Oui (-25%)", value=1),
    discord.app_commands.Choice(name="Non", value=0)])
@app_commands.choices(nbjoueurs =[
    discord.app_commands.Choice(name="1", value=1),
    discord.app_commands.Choice(name="2", value=2),
    discord.app_commands.Choice(name="3", value=3),
    discord.app_commands.Choice(name="4", value=4),
    discord.app_commands.Choice(name="5", value=5)])

async def mate(interaction: discord.Interaction, nbjoueurs:discord.app_commands.Choice[int], codegroupe:str = None, 
               pénalitérank:discord.app_commands.Choice[int] = None):
    
    user = interaction.user
    guild = interaction.guild
    rankEmojiID = 0
    
    if interaction.channel.category.id != 1020311165705916467:
        await interaction.response.send_message(f"Rends toi dans la catégorie 'Recherche Mate' pour utiliser cette commande!", ephemeral=True)
        return
    if codegroupe:
        if len(codegroupe) != 6:
            await interaction.response.send_message("Le code de groupe doit être composé de 6 caractères! Si tu ne souhaites pas en mettre, enlève le champs 'codegroupe'.", ephemeral=True)
            return


    penalite = "Non"
    title = f"{interaction.user.name} a besoin de {nbjoueurs.value} mate{'s' if nbjoueurs.value > 1 else ''}!"
    if nbjoueurs.value == 4:
        title = f"Je suis last!"
        
    rank = "Non renseigné"
    vocalURL = "```Aucun salon vocal```"
    
    userInstance = UserDbSetup(user=interaction.user)
    rankFromInstance =  userInstance.getRank()
    
    if not rankFromInstance:
        rankEmojiID = userInstance.rankEmojiID

    if not codegroupe or len(codegroupe) != 6:
        codegroupe = "En DM"
    else:
        codegroupe = codegroupe.upper()

    if pénalitérank:
        if pénalitérank.value == 1:
            penalite = "Oui (-25%)"
            
    if rankFromInstance:
        rank = rankFromInstance.capitalize()

    try:
        vocalURL = user.voice.channel.jump_url
    
    except:
        pass
        

    rankName = rank.replace("`","")
    rankEmojiID = userInstance.rankEmojiID
    rankEmoji:discord.Emoji = bot.get_emoji(rankEmojiID)
    rankEmojiToUse = f"<:{rankEmoji.name}:{rankEmojiID}>"


    embed = discord.Embed(title=title,description= "Viens vite le rejoindre!", colour= discord.Colour.red(), timestamp=datetime.datetime.now())
    embed.add_field(name=f"{rankEmojiToUse} Rank", value=f"```{rankName.capitalize()}```", inline=True)
    embed.add_field(name=f"Nombre", value=f"```{nbjoueurs.value} joueur{'s' if nbjoueurs.value > 1 else ''}```", inline=True)
    embed.add_field(name="Pénalité", value=f"```{penalite}```", inline=True)
    embed.add_field(name="Code de groupe", value=f"```{codegroupe}```", inline=True)
    embed.add_field(name=f"Salon vocal", value=f"{vocalURL}", inline=True)
    embed.add_field(name="Contacter", value=f"{interaction.user.mention}", inline=True)
    embed.set_footer(text=guild.name, icon_url=guild.icon)
    
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    if vocalURL != "```Aucun salon vocal```":
        boutonVocal = discord.ui.Button(label="Rejoindre le salon vocal", style=discord.ButtonStyle.link, url=vocalURL)
        view = discord.ui.View()
        view.add_item(boutonVocal)
        await interaction.response.send_message(embed=embed, view=view)
        return
    
    
    else:
        viewSupprMessage = supprInviteMate(interactionBase=interaction)
        await interaction.response.send_message(embed=embed, view=viewSupprMessage)
        return
    

"""    if user.voice is None:
        await interaction.response.send_message("Tu n'es pas dans un salon vocal!", ephemeral=True)
        return
"""


@bot.tree.command(name="jointeam", description="Formule une demande pour rejoindre une team")
@app_commands.guild_only()
async def jointeam(interaction: discord.Interaction, teamtag:str):

    userInstance = UserDbSetup(user=interaction.user)
    teamInstance = Team(user=interaction.user, teamTag=teamtag.upper(), server=interaction.guild)

    msg= None
    teamOwnerID = 154

    if userInstance.isTeamOwner():
        msg = f"Tu es le propriétaire de {userInstance.getTeamTag()}. Pour rejoindre une team, il faut que tu quitte le serveur pour supprimer ton actuelle ge.."

    elif userInstance.isInTeam():
        msg = f"Tu ne peux pas rejoindre d'autre team tant que tu es dans la team {userInstance.getTeamTag()}. Fais </leaveteam:1091367598102417538> pour la quitter"

    elif not teamInstance.isValidTeamTag():
        msg = f"Désolé, la team {teamtag.upper()} n'existe pas"

    elif teamInstance.isFullTeam():
        msg = f"Cette team est déjà pleine (5/5)"

    else:
        teamName = teamInstance.getTeamName()
        teamOwnerID = await teamInstance.getTeamOwner()
        teamOwner = bot.get_user(teamOwnerID)
        team = teamName.capitalize()

        msg = f"La demande pour rejoindre la team {team} a bien été envoyée à son propriétaire."
        await teamInstance.invitationOwnerNewMember(guild=interaction.guild, teamOwner=teamOwner, teamTag=teamtag)

    await interaction.response.send_message(msg)




@bot.tree.command(name="leaveteam", description="Quitte ta team actuelle")
@app_commands.guild_only()
async def leaveteam(interaction: discord.Interaction):

    userInstance = UserDbSetup(user= interaction.user)
    if not userInstance.isInTeam():
        await interaction.response.send_message("Tu n'es pas dans une équipe!", ephemeral=True)
        return
    
    if userInstance.isTeamOwner():
        await interaction.response.send_message("Tu ne peux pas quitter une team que tu as créée!", ephemeral=True)
        return
    
    tag = userInstance.getTeamTag()

    teamInstance = Team(user=interaction.user, teamTag=tag, server=interaction.guild)
    
    await teamInstance.memberLeaveTeam()
    await interaction.response.send_message(f"Tu as bien quitté la team {tag}", ephemeral=True)



@bot.tree.command(name="deleteteam", description="Supprime la team si tu en es propriétaire")
@app_commands.guild_only()
async def deleteteam(interaction: discord.Interaction):

    userInstance =UserDbSetup(user=interaction.user)

    if userInstance.isTeamOwner():
        teamTag= userInstance.getTeamTag()
        await interaction.response.send_message(view=deleteTeamConfirmation(teamTag=teamTag, server=interaction.guild, teamOwner=interaction.user))
        return
    else:
        await interaction.response.send_message("Tu ne possèdes aucune team.", ephemeral=True)


@bot.tree.command(name="setnewowner", description="Donne les commandes de ta team à quelqu'un d'autre (si tu es propriétaire)")
@app_commands.guild_only()
async def setnewowner(interaction: discord.Interaction, newowner: discord.Member):
    
    userInstance =UserDbSetup(user=interaction.user)

    if userInstance.isTeamOwner():
        teamTag= userInstance.getTeamTag()
        teamInstance = Team(user=interaction.user, teamTag=teamTag, server=interaction.guild)
        #teamInstance.changeTeamOwner(newOwner=new)
        await interaction.response.send_message(view=deleteTeamConfirmation(teamTag=teamTag, server=interaction.guild, teamOwner=interaction.user))
        

    else:
        await interaction.response.send_message("Tu n'es pas owner d'une quelconque team, tu ne peux donc pas en supprimer une!", ephemeral=True)




@bot.tree.command(name="setcreateteammodal", description="Envoie le modal de création de team")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def setcreateteammodal(interaction:discord.Interaction, createteamchannel: discord.TextChannel):

    creationTeamEmbed = buildEmbed(title="Création de team", content="Clique sur le bouton pour créer ta team!", imageurl="https://media1.tenor.com/images/7")

    await createteamchannel.send(view=createTeamView())
    await interaction.response.send_message(f"Le salon {createteamchannel.name} a bien été défini comme salon de création de teams!", ephemeral=True)





@bot.tree.command(name="setupcrosshairs", description="Upload tous les crosshairs") 
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(type =[
    discord.app_commands.Choice(name="Top", value="top"),
    discord.app_commands.Choice(name="User", value="user")
])
async def setup_crosshairs(interaction: discord.Interaction, type: discord.app_commands.Choice[str], rolemembre: discord.Role, forum: discord.ForumChannel = None):
    await interaction.response.defer(thinking=True, ephemeral=True)
    
    guild = interaction.guild
    isFade = False
    dictLinksFiles = {}
    attachment = ""
    # reactEmoji = bot.get_emoji("<:utilityValider:1086310104917352559>")
    
    if not forum:
        forum = await guild.create_forum(name=f"🎯・{type.value.capitalize()}", topic="Les crosshairs les plus utilisés", default_layout=discord.ForumLayoutType.gallery_view,
                                         default_sort_order=discord.ForumOrderType.creation_date)

    await forum.set_permissions(rolemembre, read_messages=True, send_messages=False, read_message_history=True)
    await forum.set_permissions(guild.default_role, view_channel=False, read_messages=False, connect=False, send_messages=False)
    tagPro = await forum.create_tag(name="Pro",emoji="🤖")
    

    try:
        crosshairs = dbValorant.crosshairs.find({"type": type.value})
        listeCrosshairs = list(crosshairs)
        [print(crosshair["name"]) for crosshair in listeCrosshairs]
        
        listeALenvers = []
        
        for i in listeCrosshairs:
            listeALenvers.insert(0,i)

        for crosshair in listeALenvers:
            path = f"crosshairs/{type.value}/{crosshair['id']}"
            listeFiles = []
            dictLinksFiles.clear()

            try:
                for entry in os.listdir(path):
                    if entry == "preview.png":
                        previewPath = f"{path}/{entry}"
                        attachment = discord.File(previewPath, filename="preview.png")

            except FileNotFoundError:
                print(f"Fichier non trouvé dans {path}.")
                continue

            if crosshair["fade"] == True:
                isFade = True

            embed = discord.Embed(title=f"{crosshair['name']}", color=discord.Color.red())
            embed.set_image(url="attachment://preview.png")
            embed.add_field(name="📋 Copier le code", value=f"```{crosshair['code']}```", inline=True)
            embed.set_footer(text=f"{crosshair['id']}")

            # Crée le thread sur le forum avec les fichiers et l'embed
            thread = await forum.create_thread(name=crosshair["name"], file=attachment, embed=embed,view=detailCrosshairButton(isFade=isFade),
                                               applied_tags=[tagPro])
            
            previewImage = thread.message.embeds[0].image.url


            # Met à jour la base de données avec les IDs des messages et les liens des fichiers
            dbValorant.crosshairs.update_one(
                {"id": crosshair["id"]},
                {"$set": {"threadID": thread.message.id,
                          "preview": thread.message.embeds[0].image.url,
                          "uploaded": True,
                          "jump_url": thread.message.jump_url,
                          "image_url": previewImage}},
                upsert=True
            )

            await asyncio.sleep(4.5)  

        await interaction.followup.send("Les crosshairs ont bien été uploadés", ephemeral=True)

    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        await interaction.followup.send("Une erreur est survenue lors de l'upload des crosshairs", ephemeral=True)
    


@bot.tree.command(name="uploadcrosshairs", description="Upload tous les crosshairs") 
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(type =[
    discord.app_commands.Choice(name="Top", value="top"),   
    discord.app_commands.Choice(name="User", value="user")
])
@app_commands.choices(special =[
    discord.app_commands.Choice(name="True", value="true"),
    discord.app_commands.Choice(name="False", value="false")
])
async def upload_crosshairs(interaction: discord.Interaction, type: discord.app_commands.Choice[str], special:str = "false" ):
    
    channel  = None
    
    if type.value == "top":
        channel =  bot.get_channel(1261324138551967866)
        
    if type.value == "user":
        channel =  bot.get_channel(1261276743122292846)
        
    if special == "true":
        channel = bot.get_channel(1261353131405742202)
    
    crosshairs_count = dbValorant.crosshairs.count_documents({"isSpecialUploaded": {"$exists": True}})
    print(f"Number of crosshairs with isSpecialUploaded field: {crosshairs_count}")
    
    dossier = f"crosshairs/{type.value}"
    
    if special == "true":
            
        # Iterate over all folders in the specified directory
        
        for root, dirs, files in os.walk(dossier):
            crosshair_id = root.split("\\")[-1]
            
            crosshair_data = dbValorant.crosshairs.find_one({"id": crosshair_id})
            
            try:
                try:
                    if crosshair_data["isSpecialUploaded"]:
                        print("Already uploaded")
                        continue
                except KeyError:
                    pass
                
                if crosshair_data["blank"].startswith("https://cdn."):
                    print("Already uploaded")
                    dbValorant.crosshairs.update_one({"id": crosshair_id}, {"$set":{"isSpecialUploaded":True}}, upsert=True)
                    continue
                else:
                    pass
            except:
                print("Not uploaded")
                
            listeFiles = []
            
            for file_name in files:
                if file_name in ["blank.png" ,"fade.png", "fadebg.png"]:

                    file_path = os.path.join(root, file_name)
                    name = file_name.replace(".png", "")
                    listeFiles.append(discord.File(file_path, filename=f"{name}.png"))

                    print(f"Image {file_name} uploaded")
                
                
            if listeFiles:
                
                dictAttachments = {}
                messageStock = await channel.send(files=listeFiles)
                            
                for attachment in messageStock.attachments:
                    dictAttachments[attachment.filename.replace(".png","")] = attachment.url
                    
                print(dictAttachments)
                
                dbValorant.crosshairs.update_one({"id": crosshair_id}, {"$set": dictAttachments}, upsert=True)     
            await asyncio.sleep(0.5)
            
    
    if special == "false":
        
        # Iterate over all folders in the specified directory
        for root, dirs, files in os.walk(dossier):
            
            
            crosshair_id = root.split("\\")[-1]
            print(crosshair_id)
            crosshair_data = dbValorant.crosshairs.find_one({"id": crosshair_id})
            
            try:
                if crosshair_data["preview"].startswith("https://cdn."):
                    print("Already uploaded")
                    continue
                else:
                    pass
            except:
                print("Not uploaded")
                
            

            listeFiles = []
            
            for file_name in files:
                
                if file_name not in ["blank.png","metall.png" ,"fade.png" ,"grass.png"]:

                    file_path = os.path.join(root, file_name)
                    name = file_name.replace(".png", "")

                    if file_name != "preview.png":
                        listeFiles.append(discord.File(file_path, filename=f"{name}.png"))
                    
                    else:
                        listeFiles.insert(0,discord.File(file_path, filename=f"{name}.png"))

                    print(f"Image {file_name} uploaded")
                
            if listeFiles:
                
                dictAttachments = {}
                messageStock = await channel.send(files=listeFiles)
                            
                for attachment in messageStock.attachments:
                    dictAttachments[attachment.filename.replace(".png","")] = attachment.url
                    
                print(dictAttachments)
                dbValorant.crosshairs.update_one({"id": crosshair_id}, {"$set": dictAttachments}, upsert=True)        
            await asyncio.sleep(0.5)

    return


    
 

# upload_image("user", "crosshairs/")


bot.run(TOKEN)