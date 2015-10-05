import json, time
from django.views import generic
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import nihongo.aes
from nihongo.api import *

def encrypt(data, key):
    return data
    return nihongo.aes.encryptString(data, key)

def decrypt(data, key):
    return data
    return nihongo.aes.decryptString(data, key)

def jsonResponse(object, key):
    startTime = time.time()
    encryptedData = encrypt(json.dumps(object), key)
    endTime = time.time()
    print('Data encrypted in: {0:04f}s'.format(endTime - startTime))

    content = json.dumps(encryptedData)
    response = HttpResponse(content, content_type = 'application/json')
    response['Content-Length'] = len(content)
    return response

def jsonFailureResponse(exceptionName, key):
    return jsonResponse({ 'success': False, 'exception': exceptionName}, key)

def jsonSuccessResponse(object, key):
    object['success'] = True
    return jsonResponse(object, key)

ActionHandler = {}

def actionHandler(actionName):
    def innerWrapper(function):
        ActionHandler[actionName] = function
        return function
    return innerWrapper

@csrf_exempt
def apiView(request):
    key = [42, 30, 185, 179, 32, 110, 213, 38, 65, 164, 62, 121, 61, 170, 161, 93, 109, 174, 164, 30, 64, 15, 73, 56, 73, 35, 183, 156, 149, 245, 13, 23, 187, 236, 141, 92, 213, 61, 218, 6, 138, 222, 115, 3, 127, 104, 110, 200, 249, 46, 5, 138, 181, 57, 198, 167, 175, 15, 191, 238, 156, 28, 214, 83, 219, 47, 193, 75, 68, 187, 160, 237, 111, 226, 213, 248, 126, 197, 136, 41, 249, 116, 137, 132, 145, 1, 250, 182, 3, 136, 245, 190, 29, 216, 61, 8, 246, 28, 195, 131, 235, 43, 78, 221, 95, 218, 14, 70, 178, 180, 28, 175, 187, 78, 140, 142, 113, 204, 126, 210, 130, 178, 19, 244, 250, 161, 198, 65, 229, 21, 130, 184, 213, 57, 10, 93, 91, 17, 89, 133, 187, 78, 86, 11, 237, 33, 234, 193, 183, 249, 26, 96, 99, 206, 244, 122, 171, 31, 189, 222, 136, 6, 100, 102, 94, 89, 231, 243, 236, 214, 82, 2, 126, 210, 36, 157, 193, 33, 122, 250, 165, 239, 198, 2, 54, 26, 61, 92, 18, 108, 161, 72, 215, 138, 86, 219, 123, 131, 152, 73, 98, 239, 61, 24, 251, 214, 85, 106, 86, 72, 84, 252, 28, 0, 172, 62, 95, 249, 72, 77, 53, 205, 222, 245, 157, 115, 232, 255, 142, 158, 68, 177, 203, 206, 198, 255, 201, 15, 231, 206, 33, 58, 212, 250, 144, 14, 90, 253, 78, 160, 254, 209, 33, 118, 143, 238]
    if request.method != 'POST':
        return jsonFailureResponse('Interface only accepts POST request.', key = key)
    if 'data' not in request.POST:
        return jsonFailureResponse('Data not provided.', key = key)

    try:
        data = json.loads(decrypt(request.POST['data'], key = key))
    except Exception as e:
        return jsonFailureResponse('Failed to decrypt your request.', key = key)

    sessionToken = data['sessionToken'] if 'sessionToken' in data else None

    if 'action' not in data:
        return jsonFailureResponse('Action is not specified.', key = key)
    action = data['action']
    
    if action not in ActionHandler:
        return jsonFailureResponse('Unrecognized action "{}".'.format(action), key)
    else:
        try:
            return jsonSuccessResponse(ActionHandler[action](data, sessionToken), key)
        except APIException as e:
            return jsonFailureResponse(type(e).__name__[3:-9], key)
        except Exception as e:
            print('Internal Exception: {}'.format(e))

@actionHandler('signIn')
def actionSignIn(data, sessionToken):
    session = apiSignIn(data['email'], data['password'])
    return { 'sessionToken': session.sessionToken, 'email': session.user.email, 'name': session.user.name }

@actionHandler('signOut')
def actionSignOut(data, sessionToken):
    apiSignOut(sessionToken = sessionToken)
    return {}

@actionHandler('searchWord')
def actionSearchWord(data, sessionToken):
    return { 'words': apiSearchWord(data['word'], sessionToken = sessionToken) }

@actionHandler('addWord')
def actionAddWord(data, sessionToken):
    return { 'word': apiAddWord(data['word'], sessionToken = sessionToken) }

# Create your views here.
class NihongoView(generic.TemplateView):
    template_name = 'nihongo/nihongo.html'
