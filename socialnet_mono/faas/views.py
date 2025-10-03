from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from faas.services import process_callback_data

@csrf_exempt
def faas_callback_view(request):
    print("FaaS Callback Received")
    print("Method:", request.method)
    print("Headers:", request.headers)
    print("GET Params:", request.GET)
    print("POST Data:", request.POST)
    print("Body:", request.body)

    process_callback_data(request)

    return JsonResponse({"status": "Callback received"}, status=200)
