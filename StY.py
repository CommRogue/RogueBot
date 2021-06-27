from async_spotify import SpotifyApiClient
from async_spotify.authentification import SpotifyAuthorisationToken
from async_spotify.authentification.authorization_flows import ClientCredentialsFlow, AuthorizationCodeFlow
import async_spotify
import youtubesearchpython as yt
import asyncio
from urllib.parse import urlparse

class TokenRenewClass:
    async def __call__(self, spotify_api_client: SpotifyApiClient) -> SpotifyAuthorisationToken:
        auth_flow = ClientCredentialsFlow(application_id="APPID", application_secret="APPSECRET")
        api = SpotifyApiClient(auth_flow, hold_authentication=True)
        auth = await api.get_auth_token_with_client_credentials()
        return auth

class PYTClient():
    @classmethod
    async def create_client(cls, spotifyID: str, spotifySecret: str):
        renew_token = TokenRenewClass()
        self = PYTClient()
        auth_flow = ClientCredentialsFlow(application_id=spotifyID, application_secret=spotifySecret)
        renew_class = TokenRenewClass()
        api = SpotifyApiClient(auth_flow, hold_authentication=True, token_renew_instance=renew_class)
        self.auth = await api.get_auth_token_with_client_credentials()
        await api.create_new_client()
        self.client = api
        return self

    async def getYtSearchQuery(self, sTrack):
        query = f"ytsearch:{sTrack['name']} "
        for artist in sTrack['artists']:
            query += f"{artist['name']} "
        query += "audio"
        return query

    async def getSong(self, url:str, wvClient):
        sTrack = await self.client.track.get_one(url, auth_token=self.auth)
        track = await wvClient.wavelink.get_tracks(await self.getYtSearchQuery(sTrack))
        track = track[0]
        return track, sTrack['external_urls']['spotify'], sTrack

    async def getPlaylist(self, url:str):
        playlist = await self.client.playlists.get_one(url, auth_token=self.auth)
        songs = []
        for track in playlist['tracks']['items']:
            songs.append({"spTrack": track['track'], "wlTrack": None})
        return songs, playlist

    async def getAlbum(self, url: str, wvClient):
        album = await self.client.albums.get_one(url, auth_token=self.auth)
        if album['album_type'] == 'single':
            track = await wvClient.wavelink.get_tracks(self.getYtSearchQuery(album))
            track = track[0]
            return "single", track, album
        else:
            songs = []
            for track in album['tracks']['items']:
                songs.append({"spTrack": track, "wlTrack": None})
            return "album", songs, album

    async def __ytSearch(self, name):
        return yt.VideosSearch(name, limit=1).resultComponents[0]

    @staticmethod
    def resolveSpotifyUrl(link):
        parsedUrl = urlparse(link)
        urlPath = parsedUrl.path
        parts = urlPath.split(r"/")
        return parts[1], parts[2]

# async with aiohttp.ClientSession() as session:
        # 	async with session.get(f"https://www.youtube.com/results?search_query={name.replace(' ', '+')}") as response:
        # 		text = await response.text()
        # 		scraper = BeautifulSoup(text, 'html.parser')
        # 		result = scraper.find_all(class_='style-scope ytd-item-section-renderer')
        # 		print(result)