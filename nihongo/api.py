from datetime import datetime, timedelta
from hashlib import sha1

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from nihongo.models import User, Session, Privellege
from nihongo.models import Word, WordType, Meaning, Example, Occurence
from nihongo.exceptions import *
from nihongo.dictionary import search

""" API that handles user sign in/out """

def apiSignIn(email, password):
    userFilter = User.objects.filter(email = email, password = sha1(password.encode('utf8')).hexdigest())
    if len(userFilter) != 1:
        raise APIInvalidCombinationException()
    user = userFilter[0]
    newSession = Session(user_id = user.id)
    newSession.save()
    newSession.sessionToken = sha1((user.email + str(newSession.creationDate)).encode('utf8')).hexdigest()
    newSession.expiryDate += timedelta(days = 7)
    newSession.save()
    return newSession

def sessionRequired(privellege = None, addActionCounter = True):
    def innerWrapper(apiFunction):
        def verified(*args, **kwargs):
            sessionFilter = Session.objects.filter(sessionToken = kwargs['sessionToken'])
            if len(sessionFilter) != 1:
                raise APINotSignedInException()
            session = kwargs['session'] = sessionFilter[0]

            if timezone.now() >= session.expiryDate:
                session.expired = True
                session.save()

            if session.expired:
                raise APISessionExpiredException()   

            if privellege != None and \
               len(Privellege.objects.filter(user_id = session.user.id, privellege = Privellege.PrivellegeDict[privellege])) == 0:
                raise APINoPrivellegeException()

            if addActionCounter:
                session.actionCount += 1
                session.save()
            return apiFunction(*args, **kwargs)
        return verified
    return innerWrapper

@sessionRequired()
def apiSignOut(*args, **kwargs):
    session = kwargs['session']
    session.expired = True
    session.save()

#TO-DO: Verify User Privellege
@sessionRequired()
def apiSearchWord(keyword, **kwargs):
    words = []
    for word in Word.objects.filter(Q(word__contains = keyword) | Q(kana__contains = keyword)):
        words.append(word.toObject())

    for word in words:
        word['indict'] = True
    
    if len(words) == 0:
        try:
            words = search(keyword)
        except Exception as e:
            raise APIDictionarySearchException()

        for i in range(len(words)):
            word = words[i]
            wordFilter = Word.objects.filter(word = word['word'], kana = word['kana'])
            if len(wordFilter) > 0:
                words[i] = wordFilter[0].toObject()
                words[i]['indict'] = True
            else:
                word['indict'] = False

    return sorted(words, key = lambda word: (len(word['word']), word['word']))

#TO-DO: Verify User Privellege
#TO-DO: Accounting
@sessionRequired()
def apiAddWord(word, **kwargs):
    if len(Word.objects.filter(word = word['word'], kana = word['kana'])) > 0:
        raise APIWordAlreadyExistsException()

    try:
        with transaction.atomic():
            newWord = Word(word = word['word'], kana = word['kana'])
            newWord.save()
            for wordType in word['wordTypes']:
                WordType(word_id = newWord.id, wordType = WordType.TypeDict[wordType]).save()
            for meaning in word['meanings']:
                newMeaning = Meaning(word_id = newWord.id, meaning = meaning['meaning'], explanation = meaning['explanation'])
                newMeaning.save()
                for example in meaning['examples']:
                    newExample = Example(meaning_id = newMeaning.id, example = example['example'], translation = example['translation'])
                    newExample.save()
                    for i in range(len(example['occurences'])):
                        Occurence(example_id = newExample.id, occurence = example['occurences'][i], index = i).save()
    except IntegrityError as e:
        raise APITransactionErrorException()

    newWord = newWord.toObject()
    newWord['indict'] = True
    return newWord
