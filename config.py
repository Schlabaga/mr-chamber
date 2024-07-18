import pymongo
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv



load_dotenv()


MONGO_CLIENT_KEY = os.getenv('MONGO_CLIENT_KEY')
TOKEN = os.getenv('TOKEN')

MongoClient = pymongo.MongoClient(MONGO_CLIENT_KEY)
dbUser = MongoClient.userconfig
dbBot = MongoClient.botconfig
dbServer = MongoClient.serverconfig
dbValorant = MongoClient.valorantconfig
cloudinary_secret = os.getenv('API_SECRET')
cloudinary_key = os.getenv('API_KEY')
cloudinary_name = os.getenv('CLOUD_NAME')

bot = commands.Bot(command_prefix="+", intents= discord.Intents.all())


rankDict = {
    "unranked": 1214631559139958825,
    "iron_1": 1214624515183869953,
    "iron_2": 1214625323795357698,
    "iron_3": 1214624519902470215,
    "bronze_1": 1214624494732189696,
    "bronze_2": 1214624496074489907,
    "bronze_3": 1214624497533980713,
    "silver_1": 1214624530249555989,
    "silver_2": 1214625328086126602,
    "silver_3": 1214624533928083517,
    "gold_1": 1214624899084324864,
    "gold_2": 1214624505671196692,
    "gold_3": 1214625321333297222,
    "platinum_1": 1214624522884489316,
    "platinum_2": 1214625325582123058,
    "platinum_3": 1214624526395244554,
    "diamond_1": 1214624499824070716,
    "diamond_2": 1214624501044871168,
    "diamond_3": 1214624502294781982,
    "ascendant_1": 1214624490483613776,
    "ascendant_2": 1214624491980718100,
    "ascendant_3": 1214624493574688768,
    "immortal_1": 1214624509873881228,
    "immortal_2": 1214624511899467807,
    "immortal_3": 1214625322717159474,
    "radiant": 1214625326668324895
}