import requests
import json
from requests import Response
from django.conf import settings
from django.core.cache import cache


class FaasService:
    sync_function_path = '/function/{}'
    async_funtcion_path = '/async-function/{}'

    function_generate_report = 'activity-report'  # action-based
    function_categorize_post_text ='categorize-text'  # always
    function_extract_keywords = 'extract-keywords'  # always
    function_image_thumbnail = 'image-thumbnail'  # always
    function_offensive_word_detection = 'offensive-word-detection'  # always
    function_video_thumbnail = 'video-thumbnail'  # always

    # function_image_encoding = 'image_encoding'
    # function_video_encoding = 'video_encoding'

    function_sentiment_analysis = 'sentimentanalysis'  # always
    function_image_inception = 'inception'  # action-based
    function_nsfw_recognition = 'openfaas-opennsfw'  # action-based
    function_text_to_speech = 'my-text-to-speech'  # action-based (or never - simple API call)
    function_text_to_qrcode = 'qrcode-go'  # action-based

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.FAAS_URL
    
    def get_headers(self, extra_headers: dict | None = None) -> dict:
        headers = {
            'Content-Type': 'application/json',
        }
        headers.update(extra_headers or {})
        return headers

    def call_function(
        self,
        function_name: str,
        payload: dict,
        is_async: bool = False,
        callback_hook: str | None = None,
        metadata: dict | None = None,
        **request_kwargs
    ) -> Response:
        """
            Call a FaaS function, either synchronously or asynchronously.

            :param function_name: Name of the FaaS function to call
            :param payload: Payload to send to the function (request body, json)
            :param is_async: Whether to call the function asynchronously
            :param callback_hook: URL to send the callback to (only for async calls)
            :param metadata Extra info to save in cache for async calls
            :param request_kwargs: Additional arguments to pass to the requests.post method (like data, timeout, etc.)

            :return: Response from the FaaS function as a dictionary
        """
        if is_async:
            if callback_hook:
                headers = self.get_headers({'X-Callback-Url': callback_hook})
            else:
                headers = self.get_headers()
            return self._call_async_function(function_name, payload, headers=headers, metadata=metadata, **request_kwargs)
        else:
            return self._call_sync_function(function_name, payload, headers=self.get_headers(), **request_kwargs)
    
    def _call_sync_function(self, function_name: str, payload: dict, headers: dict, **request_kwargs) -> Response:
        url = self.base_url + self.sync_function_path.format(function_name)
        response = requests.post(url, json=payload, headers=headers, **request_kwargs)
        response.raise_for_status()
        return response
    
    def _call_async_function(
            self,
            function_name: str,
            payload: dict,
            headers: dict,
            metadata: dict | None = None,
            **request_kwargs,
    ) -> Response:
        url = self.base_url + self.async_funtcion_path.format(function_name)
        if isinstance(payload, dict):
            request_kwargs['json'] = payload
        else:
            request_kwargs['data'] = payload
        response = requests.post(url, headers=headers, **request_kwargs)
        response.raise_for_status()
        self._process_call_id(response, metadata)
        return response
    
    def _process_call_id(self, response: Response, metadata: dict | None):
        call_id = response.headers.get("X-Call-Id", None)
        set_metadata_in_cache(call_id, metadata)
        


def cache_key(call_id):
    return f"faas:async-call:metadata:{call_id}"

def set_metadata_in_cache(call_id: str, metadata: dict | None):
    if metadata and call_id:
        print("Settings metadata {} for {} in cahce".format(metadata, call_id))
        cache.set(
            cache_key(call_id),
            json.dumps(metadata),
            60 * 60  # one hour
        )
    else:
        print("No metadata or bad call_id", metadata, call_id)

def get_metadata_from_cache(call_id: str) -> dict | str:
    data = cache.get(cache_key(call_id))
    try:
        return json.loads(data)
    except Exception as e:
        return data
    