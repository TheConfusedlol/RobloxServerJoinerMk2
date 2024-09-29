import requests
from selenium import webdriver
import asyncio
import time
import aiohttp

# Enter your roblox cookie here
robloxCookie = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_832CF6B0889EDBCC3F4464A312D5D193C0F3DD07F7C2944A2F0B03A609C7BE8BECF1DABD527BED861FD126D77968123C9A485EF389A8281A7E61AEAC00E6D94D61A8ED7077749F6EE51AE96560A133DAC47B88AE86577A9F198F219DBCE79CAAC63A57BCDDC2D0B790B8AF36F1FCE79CE7604F2341E6A8166396B2CC018458787D730252845B90CA4EE0A7236DC66B87074A3FB9898024756C8D7328763B08EB1BD486394874A350447DCA9D8F6C3D8E0B6AFFA8CF291CA8E277E319C783137D945453069CE36A0A773286E92F23181C0004081C2807A0FD7BB8C013E23BDB7274A99D6A379147EE4A25A437123B5466DA6EF8F766237D6123F1D491EA8B584B3A037CFDEB95378A25727ACB023B7FA0EC95843EDDA8B6F4151AC9052E0581E05A5F78C4827B6CB0C9C1E5FD9FDC4EE70597EF4CEA79F1EC085E0CA97A100F3E2CFA6D4233CCFB4E78B1C7379BE3291B18775485D6F93EC67BE918377B70779C285DCD784F42501039FC1F91EDB6987F94AE09CE4B4DA3957C456111ECDB929DF7BAFB2A6F336DB11BCC607A5FD5A19E277070D3155382CF427234BE6F844E8F3C909020B033F1313FD7E8FC9BEA4783D801B079E65B929C60B7D8F20AB19153995520C1F27AC945AF774CB34D3BA561AB4DF1F1101FF837BDFAB75595859B95DCEECE34031C107666CCD4AD95B93BB8B2A9FA1B24A21A7D795B8C0C5C2442B12F1442113822BB7CA026627D9202543F0D9DA2E1B2378A43CB3825E1DC0CB75312F0A84F10214D83D8581A53330C5D57A4487F07E7E7A4221C3B3BEA257D4B556EE4DCE39BFFBC27855C80E98369325ECCDE63AFBFA605431A5DF545CC8C8D464B4DD4C8A83B4B3A7B6F5BAC41B4326259CD3E66750E9DD87EB121C0B0BF4E3FE506379D2056C6B8F6E71B1965D8CB824E61DF49742D10FC6A0A113B40B6698CCBC520679FBDF1EE79834CBE4C862FC09C0D58F7A6042C3914A406FF8B14B800609967F3"

# Enter desired city and region here (Miami, FL)
targetCity = "miami"
targetRegion = "florida"
targetCountryCode = "US"

print("Roblox Server Finder by Exilon (Exilon24 on GitHub).")
placeId = int(input("PlaceID: "))
print("Looking for game...")

# Get game server details from Roblox API
uri = f"https://games.roblox.com/v1/games/{str(placeId)}/servers/Public?excludeFullGames=true&limit=100"
response = requests.get(url=uri)
servers = response.json()["data"]

gameUniverseID = requests.get(f"https://apis.roblox.com/universes/v1/places/{str(placeId)}/universe").json()["universeId"]
gameInfo = requests.get(f"https://games.roblox.com/v1/games?universeIds={str(gameUniverseID)}").json()["data"][0]

print("--------------------------------------------------------")
print(f"Now joining: {gameInfo['name']} by {gameInfo['creator']['name']}.\nThere are {gameInfo['playing']} players currently online.")
print("--------------------------------------------------------")
print("Attempting to find server information...")

authCookies = {
    ".ROBLOSECURITY": robloxCookie,
}
authHeaders = {
    "Referer": f"https://www.roblox.com/games/{placeId}/",
    "Origin": "https://roblox.com",
    "User-Agent": "Roblox/WinInet",
}

taskList = []
global driver
driver = webdriver.Chrome()

async def getServerInfo(server):
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
        ip = ip["joinScript"]

        if ip == None:
            return False

        try:
            ip = ip["UdmuxEndpoints"][0]["Address"]
        except:
            print("Error with roblox server joins...")
            return False

        # Geolocation request for the IP address
        geolocation = await session.get(f"http://ip-api.com/json/{ip}")
        geolocation = await geolocation.json()

        if geolocation["status"] != "success":
            return False

        # Print out the geolocation details
        print(f"Server found at ({geolocation['countryCode']}) --> {geolocation['region']}, {geolocation['city']}")

        # Check if the server is located in Miami, Florida
        if geolocation["countryCode"] == targetCountryCode and geolocation["city"].lower() == targetCity and geolocation["regionName"].lower() == targetRegion:
            driver.get(f"https://www.roblox.com/games/{str(placeId)}/")
            driver.add_cookie({
                "name": ".ROBLOSECURITY",
                "value": robloxCookie,
                "path": "/",
                "domain": ".roblox.com"
            })
            driver.refresh()
            driver.execute_script(f"Roblox.GameLauncher.joinGameInstance({placeId}, \"{serverId}\")")
            for t in taskList:
                t.cancel()
            return True
        return False

# Main async loop to find servers
async def main():
    for server in servers:
        taskList.append(asyncio.create_task(getServerInfo(server)))

    try:
        await asyncio.gather(*taskList)
    except:
        print("Done...")  # Ignore the cancelled exception.

asyncio.run(main())
time.sleep(20)  # Keep the webdriver open to ensure Roblox loads
