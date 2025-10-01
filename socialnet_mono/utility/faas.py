import requests

class FassService:
    sync_function_path = '/function/{}'
    async_funtcion_path = '/async-function/{}'

    function_generate_report = 'activity_report'
    function_categorize_post_text ='categorize_post'
    function_extract_keywords = 'extract_keywords'
    function_image_thumbnail = 'image_thumbnail'
    function_offensive_word_detection = 'offensive_word_detection'
    function_video_thumbnail = 'video_thumbnail'

    # function_image_encoding = 'image_encoding'
    # function_video_encoding = 'video_encoding'

    function_sentiment_analysis = 'sentimentanalysis'
    function_image_inception = 'inception'
    function_nsfw_recognition = 'openfaas-opennsfw'
    function_text_to_speech = 'text-to-speech'
    function_text_to_qrcode = 'qrcode-go'

    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def get_headers(self, extra_headers: dict | None = None) -> dict:
        headers = {
            'Content-Type': 'application/json',
        }
        headers.update(extra_headers or {})
        return headers

    def call_function(self, function_name: str, payload: dict, is_async: bool = False, callback_hook: str | None = None, **request_kwargs) -> dict:
        """
            Call a FaaS function, either synchronously or asynchronously.

            :param function_name: Name of the FaaS function to call
            :param payload: Payload to send to the function (request body, json)
            :param is_async: Whether to call the function asynchronously
            :param callback_hook: URL to send the callback to (only for async calls)
            :param request_kwargs: Additional arguments to pass to the requests.post method (like data, timeout, etc.)

            :return: Response from the FaaS function as a dictionary
        """
        if is_async:
            if callback_hook:
                headers = self.get_headers({'X-Callback-Url': callback_hook})
            else:
                headers = self.get_headers()
            return self._call_async_function(function_name, payload, callback_hook, headers=headers, **request_kwargs)
        else:
            return self._call_sync_function(function_name, payload, headers=self.get_headers(), **request_kwargs)
    
    def _call_sync_function(self, function_name: str, payload: dict, headers: dict, **request_kwargs) -> dict:
        url = self.base_url + self.sync_function_path.format(function_name)
        response = requests.post(url, json=payload, headers=headers, **request_kwargs)
        response.raise_for_status()
        return response.json()
    
    def _call_async_function(
            self,
            function_name: str,
            payload: dict,
            headers: dict,
            **request_kwargs,
    ) -> dict:
        url = self.base_url + self.async_funtcion_path.format(function_name)
        response = requests.post(url, json=payload, headers=headers, **request_kwargs)
        response.raise_for_status()
        return response.json()
    