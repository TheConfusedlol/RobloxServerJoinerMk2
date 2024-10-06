import requests
from selenium import webdriver
import asyncio
import time
import aiohttp

robloxCookie = " "
ServerRegion = "US"
RegionCity = "Miami"
ServerRegionSymbol = "FL"

print("Roblox server finder by Exilon (Exilon24 on github).")
placeId = int(input("PlaceID: "))
print(f"Looking for game in {ServerRegion}, {RegionCity}...")

uri = f"https://games.roblox.com/v1/games/{str(placeId)}/servers/Public?excludeFullGames=true&limit=100"
response = requests.get(url=uri)
servers = response.json()["data"]

gameUniverseID = requests.get(f"https://apis.roblox.com/universes/v1/places/{str(placeId)}/universe").json()["universeId"]
gameInfo = requests.get(f"https://games.roblox.com/v1/games?universeIds={str(gameUniverseID)}").json()["data"][0]
print(gameUniverseID)
print("Found game!")
print("--------------------------------------------------------")
print(f"Now joining: {gameInfo['name']} by {gameInfo['creator']['name']}.\nThere are {gameInfo['playing']} players currently online.")
print("--------------------------------------------------------")
print("Attempting to find server information...")

authCookies = {
    ".ROBLOSECURITY": robloxCookie
}
authHeaders = {
    "Referer": f"https://www.roblox.com/games/{placeId}/",
    "Origin": "https://roblox.com",
    "User-Agent": "Roblox/WinInet",
}

taskList = []
global driver
driver = webdriver.Chrome()

async def getServerInfo(server, serverList):
    async with aiohttp.ClientSession(cookies=authCookies) as session:
        serverId = server["id"]
        res = await session.post("https://gamejoin.roblox.com/v1/join-game-instance",
                                 data={
                                     "placeId": placeId,
                                     "isTeleport": False,
                                     "gameId": serverId,
                                     "gameJoinAttemptId": serverId
                                 },
                                 headers=authHeaders)
        ip = await res.json()
        ip = ip.get("joinScript", None)

        if ip is None:
            return False

        try:
            ip = ip["UdmuxEndpoints"][0]["Address"]
        except:
            print("Error with Roblox server joins...")
            return False

        geolocation = await session.get(f"http://ip-api.com/json/{ip}")
        geolocation = await geolocation.json()

        if geolocation["status"] != "success":
            return False

        print(f"Server found at ({geolocation['countryCode']}) --> {geolocation['region']}, {geolocation['city']}")

        if geolocation["countryCode"] == ServerRegion and geolocation["city"] == RegionCity:
            print(f"Joining server in {RegionCity}, {ServerRegionSymbol}, {ServerRegion}...")
            driver.get(f"https://www.roblox.com/games/{str(placeId)}/")
            driver.add_cookie({"name": ".ROBLOSECURITY", "value": robloxCookie, "path": "/", "domain": ".roblox.com"})
            driver.refresh()
            driver.execute_script(f"Roblox.GameLauncher.joinGameInstance({placeId}, \"{serverId}\")")
            for t in taskList:
                t.cancel()
            return True

        serverList.append((ip, geolocation["city"], geolocation["region"]))
        return False

async def main():
    serverList = []
    for server in servers:
        taskList.append(asyncio.create_task(getServerInfo(server, serverList)))

    try:
        await asyncio.gather(*taskList)
    except:
        print("Done...")

    if serverList:
        with open('roblox_servers.txt', 'w') as file:
            file.write("IP Addresses and Locations of Found Servers:\n")
            for ip, city, region in serverList:
                file.write(f"IP: {ip}, Location: {city}, {region}\n")
        print("Server IPs and locations have been saved to 'roblox_servers.txt'.")
    else:
        print("No suitable servers found.")

asyncio.run(main())
time.sleep(20)
