# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, Tuple, Union, List, Dict
from urllib.parse import quote
import json

# Pip
from ksimpleapi import Api
from kcu import strings

# Local
from ._utils import extract_number
from .channel_about_data import ChannelAboutData

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------------- Defines ---------------------------------------------------------------- #

YT_BASE_URL           = 'https://www.youtube.com'
YT_SEARCH_URL         = '{}/results?search_query={{}}'.format(YT_BASE_URL)
YT_SEARCH_CHANNEL_URL = '{}&sp=EgIQAg%253D%253D'.format(YT_SEARCH_URL)

YT_BASE_CHANNEL_URL         = '{}/{{}}/{{{{}}}}'.format(YT_BASE_URL)

YT_CHANNEL_URL_USER_NAME    = YT_BASE_CHANNEL_URL.format('user')
YT_CHANNEL_URL_CHANNEL_ID   = YT_BASE_CHANNEL_URL.format('channel')
YT_CHANNEL_URL_CHANNEL_NAME = YT_BASE_CHANNEL_URL.format('c')


# ---------------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- class: YoutubeScraper --------------------------------------------------------- #

class YoutubeScraper(Api):

    # ----------------------------------------------------------- Overrides ---------------------------------------------------------- #

    @classmethod
    def extra_headers(cls) -> Optional[Dict[str, any]]:
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.youtube.com'
        }


    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    def get_sub_and_video_count(self, channel_id: str) -> Optional[Tuple[int, int]]:
        try:
            base_json = self.__get_yt_json(
                YT_SEARCH_CHANNEL_URL.format(channel_id),
                path=['contents', 'twoColumnSearchResultsRenderer', 'primaryContents', 'sectionListRenderer', 'contents', 0, 'itemSectionRenderer', 'contents', 0, 'channelRenderer']
            )

            found_channel_id = base_json['channelId']

            if found_channel_id != channel_id:
                print('Did noto find \'{}\', but \'{}\''.format(channel_id, found_channel_id))

            return extract_number(base_json['subscriberCountText']['simpleText'], debug=self.debug), extract_number(base_json['videoCountText']['runs'][0]['text'], debug=self.debug)
        except Exception as e:
            if self.debug:
                print('ERROR - YoutubeScraper - get_sub_and_video_count({})'.format(channel_id), e)

            return None

    def get_channel_about_data(
        self,
        user_name: Optional[str] = None,
        channel_id: Optional[str] = None,
        channel_url_name: Optional[str] = None
    ) -> Optional[ChannelAboutData]:
        url = None

        if user_name:
            url = YT_CHANNEL_URL_USER_NAME.format(user_name)
        elif channel_id:
            url = YT_CHANNEL_URL_CHANNEL_ID.format(channel_id)
        elif channel_url_name:
            url = YT_CHANNEL_URL_CHANNEL_NAME.format(channel_url_name)

        if not url:
            if self.debug:
                print('No input data passed')

            return None

        try:
            return ChannelAboutData(
                [
                    tab_json for tab_json in self.__get_yt_json(
                        '{}/about'.format(url),
                        path=['contents', 'twoColumnBrowseResultsRenderer', 'tabs']
                    ) if 'tabRenderer' in tab_json and 'content' in tab_json['tabRenderer']
                ][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['channelAboutFullMetadataRenderer']
            )
        except Exception as e:
            if self.debug:
                print('ERROR - YoutubeScraper - get_channel_about_data() : \'{}\''.format(url), e)

            return None


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    def __get_yt_json(
        self,
        url: str,
        path: Optional[Union[List[Union[str, int]], Union[str, int]]] = None
    ) -> Optional[dict]:
        try:
            j = json.loads(
                '{' +
                strings.between(
                    self._get(url).text,
                    'var ytInitialData = {',
                    '</script>'
                ).rstrip().rstrip(';')
            )

            if path:
                if isinstance(path, str) or isinstance(path, int):
                    path = [path]

                for path_component in path:
                    j = j[path_component]

            return j
        except Exception as e:
            if self.debug:
                print('ERROR - YoutubeScraper - __get_yt_json({})'.format(url), e)

            return None


# ---------------------------------------------------------------------------------------------------------------------------------------- #