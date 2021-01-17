import httpx

from fastapi import Path, Query, APIRouter
from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer


router = APIRouter()

async def fetch_table(path):
    async with httpx.AsyncClient() as client:
        data = await client.get(f"https://ark-data.baka.icu/gamedata/{path}")
        return data.json()

async def fetch_shop_skins():
    async with httpx.AsyncClient() as client:
        data = await client.get("https://weedy.baka.icu/shop/skin")
        return data.json()

async def get_skin_info():
    skin_table = await fetch_table("excel@skin_table.json")
    brand_list = await get_brand_list()
    
    skin_info = {}
    for skin_id, skin in skin_table['charSkins'].items():
        if brand_list.get(skin['displaySkin']['skinGroupId'], False):
            if skin_info.get(skin['charId'], False) == False:
                skin_info[skin['charId']] = {}
            if skin_info[skin['charId']].get(skin['skinId'], False) == False:
                skin_info[skin['charId']][skin['skinId']] = {}
            skin_info[skin['charId']][skin['skinId']]['brand'] = brand_list[skin['displaySkin']['skinGroupId']]
            skin_info[skin['charId']][skin['skinId']]['get_time'] = skin['displaySkin']['getTime']
            skin_info[skin['charId']][skin['skinId']]['approach'] = skin['displaySkin']['obtainApproach']
            
    return skin_info

async def get_brand_list():
    skin_table = await fetch_table("excel@skin_table.json")
    
    brand_list = {}
    for brand in skin_table['brandList']:
        for group in skin_table['brandList'][brand]['groupList']:
            brand_list[group] = skin_table['brandList'][brand]['brandName'].replace('/', '-').rstrip()
    return brand_list
    
async def get_char_name():
    char_table = await fetch_table("excel@character_table.json")
    
    dict_char_name = {}
    for char_id, char in char_table.items():
        dict_char_name[char_id] = {'zh':char["name"],'en':char["appellation"]}
        
    return dict_char_name

@cached(
    ttl=10, cache=Cache.REDIS, key="shop_skins", serializer=PickleSerializer(), port=6379, namespace="prts-apis")
async def parse_data():
    shop_skins = await fetch_shop_skins()
    char_name = await get_char_name()
    skin_info = await get_skin_info()
    
    for skin in shop_skins["goodList"]:
        skin_id = skin["skinId"]
        char_id = skin_id.split("@")[0]
        if skin['startDateTime'] == -1 or skin['endDateTime'] == -1:
            shop_skins['goodList'].remove(skin)
            continue
        skin['charName'] = char_name[char_id]
        skin['brand'] = skin_info[char_id][skin_id]['brand']
        skin['approach'] = skin_info[char_id][skin_id]['approach']
        
        ordered = {}
        if len(skin_info[char_id].items()) > 1:
            temp = {}
            for skin_id, info in skin_info[char_id].items():
                temp[skin_id] = info["get_time"]
            ordered = dict(sorted(temp.items(), key = lambda x:x[1]))
            
            i = 0
            for k,v in ordered.items():
                i += 1
                ordered[k] = i
                
        else:
            ordered[skin_id] = 1
            
        skin["index"] = ordered[skin_id]
         
        
    return shop_skins

@router.get("/shop/skin")
async def get_shop_skin():
    return await parse_data()