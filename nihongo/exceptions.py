class APIException(BaseException):
    """docstring for APIException"""
    def __init__(self):
        pass

ExceptionList = [
    'InvalidCombination',
    'NotSignedIn',
    'SessionExpired',
    'NoPrivellege',
    'DictionarySearch',
    'WordAlreadyExists',
    'TransactionError',
]

for exceptionName in ExceptionList:
    exceptionName = 'API{}Exception'.format(exceptionName)
    globals()[exceptionName] = type(exceptionName, (APIException,), {})
