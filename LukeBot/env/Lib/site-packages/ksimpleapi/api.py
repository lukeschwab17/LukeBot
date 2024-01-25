# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from abc import ABC, abstractmethod
from typing import Optional, List, Union, Dict
from requests import Response
import random

# Local
from .request import Request

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------------- class: Api -------------------------------------------------------------- #

class Api:

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        keep_cookies: bool = False,
        default_cookies: Optional[Dict[str, Dict[str, str]]] = None,
        cookies_file_path: Optional[str] = None,
        store_pickled_cookies: bool = False,
        max_request_try_count: int = 1,
        sleep_s_between_failed_requests: Optional[float] = 0.5,
        default_headers: Optional[Dict[str, any]] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        allow_redirects: bool = True,
        use_cloudscrape: bool = False,
        debug: bool = False,
        default_request_timeout: Optional[float] = None
    ):
        """init function

        Args:
            user_agent (Optional[Union[str, List[str]]], optional): User agent(s) to use for requests. If list is provided, one will be chosen randomly. Defaults to None.
            proxy (Optional[Union[str, List[str]]], optional): Proxy/Proxies to use for requests. If list is provided, one will be chosen randomly. Defaults to None.
            keep_cookies (bool, optional): Keep cookies for requests and reuse them at next one. Defaults to True.
            default_cookies (Optional[Dict[str, Dict[str, str]]], optional): Default cookies to start with. Defaults to None.
            cookies_file_path (str, optional): If provided, cookies will be saved to/loaded from it. Defaults to None.
            max_request_try_count (int, optional): How many times does a request can be tried (if fails). Defaults to 1.
            sleep_s_between_failed_requests (Optional[float], optional): How much to wait between requests when retrying. Defaults to 0.5.
            allow_redirects (bool, optional): Wether requests allow redirects or no. Defaults to True.
            use_cloudscrape (bool, optional): Wether to use CloudScrape library instead of requests. Defaults to False.
            debug (bool, optional): Show debug logs. Defaults to False.
        """
        self._request = Request(
            user_agent=user_agent,
            proxy=proxy,
            keep_cookies=keep_cookies,
            default_cookies=default_cookies,
            cookies_file_path=cookies_file_path,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            default_headers=default_headers or self.default_headers(),
            extra_headers=extra_headers or self.extra_headers(),
            allow_redirects=allow_redirects,
            use_cloudscrape=use_cloudscrape,
            debug=debug,
            default_request_timeout=default_request_timeout
        )


    # ------------------------------------------------------ Public properties ------------------------------------------------------- #

    # user_agent
    @property
    def debug(self) -> bool:
        return self._request.debug

    @debug.setter
    def debug(
        self,
        val: bool
    ) -> None:
        self._request.debug = val

    # user_agent
    @property
    def user_agent(self) -> Optional[str]:
        return self._request.user_agent

    @user_agent.setter
    def user_agent(
        self,
        val: Optional[Union[str, List[str]]] = None
    ) -> None:
        if type(val) == list:
            val = random.choice(val) if len(val) > 0 else None

        self._request.user_agent = val

    # proxy
    @property
    def proxy(self) -> Optional[str]:
        return self._request.proxy

    @proxy.setter
    def proxy(
        self,
        val: Optional[Union[str, List[str]]] = None
    ) -> None:
        if type(val) == list:
            val = random.choice(val) if len(val) > 0 else None

        self._request.proxy = val


    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    @classmethod
    def default_headers(cls) -> Optional[Dict[str, any]]:
        """ Default headers to use for every request.
            Overwrite this value as needed.
        """

        return {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers'
        }

    @classmethod
    def extra_headers(cls) -> Optional[Dict[str, any]]:
        """ Every entry from this adds/overwrites an entry from 'default_headers'
            Overwrite this value as needed.
        """

        return None


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    def _get(
        self,
        url: str,
        params: Optional[Dict] = None,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        use_cookies: bool = True,
        max_request_try_count: Optional[int] = None,
        sleep_s_between_failed_requests: Optional[float] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        extra_cookies: Optional[Dict[str, str]] = None,
        allow_redirects: Optional[bool] = None,
        debug: Optional[bool] = None,
        timeout_: Optional[float] = None
    ) -> Optional[Response]:
        return self._request.get(
            url,
            params=params,
            user_agent=user_agent,
            proxy=proxy,
            use_cookies=use_cookies,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            extra_cookies=extra_cookies,
            debug=debug,
            timeout_=timeout_
        )

    @classmethod
    def _get_cls(
        cls,
        url: str,
        params: Optional[Dict] = None,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        max_request_try_count: Optional[int] = None,
        sleep_s_between_failed_requests: Optional[float] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        extra_cookies: Optional[Dict[str, str]] = None,
        allow_redirects: Optional[bool] = None,
        debug: Optional[bool] = None,
        timeout_: Optional[float] = None
    ) -> Optional[Response]:
        return Api(default_headers=cls.default_headers(), extra_headers=cls.extra_headers())._get(
            url,
            params=params,
            user_agent=user_agent,
            proxy=proxy,
            use_cookies=False,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            extra_cookies=extra_cookies,
            allow_redirects=allow_redirects,
            debug=debug,
            timeout_=timeout_
        )

    def _post(
        self,
        url: str,
        body: dict,
        params: Optional[Dict] = None,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        use_cookies: bool = True,
        max_request_try_count: Optional[int] = None,
        sleep_s_between_failed_requests: Optional[float] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        extra_cookies: Optional[Dict[str, str]] = None,
        allow_redirects: Optional[bool] = None,
        debug: Optional[bool] = None,
        timeout_: Optional[float] = None
    ) -> Optional[Response]:
        return self._request.post(
            url,
            params=params,
            user_agent=user_agent,
            proxy=proxy,
            use_cookies=use_cookies,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            extra_cookies=extra_cookies,
            body=body,
            debug=debug,
            timeout_=timeout_
        )

    @classmethod
    def _post_cls(
        cls,
        url: str,
        body: dict,
        params: Optional[Dict] = None,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        max_request_try_count: Optional[int] = None,
        sleep_s_between_failed_requests: Optional[float] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        extra_cookies: Optional[Dict[str, str]] = None,
        allow_redirects: Optional[bool] = None,
        debug: Optional[bool] = None,
        timeout_: Optional[float] = None
    ) -> Optional[Response]:
        return Api(default_headers=cls.default_headers(), extra_headers=cls.extra_headers())._post(
            url,
            body,
            params=params,
            user_agent=user_agent,
            proxy=proxy,
            use_cookies=False,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            extra_cookies=extra_cookies,
            allow_redirects=allow_redirects,
            debug=debug,
            timeout_=timeout_
        )

    def _put(
        self,
        url: str,
        body: dict,
        params: Optional[Dict] = None,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        use_cookies: bool = True,
        max_request_try_count: Optional[int] = None,
        sleep_s_between_failed_requests: Optional[float] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        extra_cookies: Optional[Dict[str, str]] = None,
        allow_redirects: Optional[bool] = None,
        debug: Optional[bool] = None,
        timeout_: Optional[float] = None
    ) -> Optional[Response]:
        return self._request.put(
            url,
            params=params,
            user_agent=user_agent,
            proxy=proxy,
            use_cookies=use_cookies,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            extra_cookies=extra_cookies,
            body=body,
            debug=debug,
            timeout_=timeout_
        )

    @classmethod
    def _put_cls(
        cls,
        url: str,
        body: dict,
        params: Optional[Dict] = None,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        max_request_try_count: Optional[int] = None,
        sleep_s_between_failed_requests: Optional[float] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        extra_cookies: Optional[Dict[str, str]] = None,
        allow_redirects: Optional[bool] = None,
        debug: Optional[bool] = None,
        timeout_: Optional[float] = None
    ) -> Optional[Response]:
        return Api(default_headers=cls.default_headers(), extra_headers=cls.extra_headers())._put(
            url,
            body,
            params=params,
            user_agent=user_agent,
            proxy=proxy,
            use_cookies=False,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            extra_cookies=extra_cookies,
            allow_redirects=allow_redirects,
            debug=debug,
            timeout_=timeout_
        )

    def _download(
        self,
        url: str,
        path: str,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        use_cookies: bool = True,
        max_request_try_count: Optional[int] = None,
        sleep_s_between_failed_requests: Optional[float] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        extra_cookies: Optional[Dict[str, str]] = None,
        allow_redirects: Optional[bool] = None,
        debug: Optional[bool] = None,
        timeout: Optional[float] = None
    ) -> bool:
        return self._request.download(
            url,
            path,
            user_agent=user_agent,
            proxy=proxy,
            use_cookies=use_cookies,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            extra_cookies=extra_cookies,
            debug=debug,
            timeout=timeout
        )

    # kept for convenience
    download = _download


    @classmethod
    def _download_cls(
        cls,
        url: str,
        path: str,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        max_request_try_count: Optional[int] = None,
        sleep_s_between_failed_requests: Optional[float] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        extra_cookies: Optional[Dict[str, str]] = None,
        allow_redirects: Optional[bool] = None,
        debug: Optional[bool] = None,
        timeout: Optional[float] = None
    ) -> bool:
        return Api(default_headers=cls.default_headers(), extra_headers=cls.extra_headers()).download(
            url,
            path,
            user_agent=user_agent,
            proxy=proxy,
            use_cookies=False,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            extra_cookies=extra_cookies,
            allow_redirects=allow_redirects,
            debug=debug,
            timeout=timeout
        )

    # kept for convenience
    download_cls = _download_cls


    def _download_async(
        self,
        urls_paths: Optional[Dict[str, str]] = None,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        use_cookies: bool = True,
        max_request_try_count: Optional[int] = None,
        sleep_s_between_failed_requests: Optional[float] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        extra_cookies: Optional[Dict[str, str]] = None,
        allow_redirects: Optional[bool] = None,
        debug: Optional[bool] = None,
        max_concurent_processes: Optional[int] = None,
        request_timeout: Optional[float] = None
    ) -> List[bool]:
        return self._request.download_async(
            urls_paths,
            user_agent=user_agent,
            proxy=proxy,
            use_cookies=use_cookies,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            extra_cookies=extra_cookies,
            debug=debug,
            max_concurent_processes=max_concurent_processes,
            request_timeout=request_timeout
        )

    # kept for convenience
    download_async = _download_async


    @classmethod
    def _download_async_cls(
        cls,
        urls_paths: Optional[Dict[str, str]] = None,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        max_request_try_count: Optional[int] = None,
        sleep_s_between_failed_requests: Optional[float] = None,
        extra_headers: Optional[Dict[str, any]] = None,
        extra_cookies: Optional[Dict[str, str]] = None,
        allow_redirects: bool = True,
        debug: Optional[bool] = None,
        max_concurent_processes: Optional[int] = None,
        request_timeout: Optional[float] = None
    ) -> List[bool]:
        return Api(default_headers=cls.default_headers(), extra_headers=cls.extra_headers()).download_async(
            urls_paths,
            user_agent=user_agent,
            proxy=proxy,
            use_cookies=False,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            extra_cookies=extra_cookies,
            allow_redirects=allow_redirects,
            debug=debug,
            max_concurent_processes=max_concurent_processes,
            request_timeout=request_timeout
        )

    # kept for convenience
    download_async_cls = _download_async_cls


# ---------------------------------------------------------------------------------------------------------------------------------------- #