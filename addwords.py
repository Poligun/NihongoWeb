from django.db import IntegrityError, transaction
from django.db.models import Q
from nihongo.models import *

def addWords(words):
    counter = 0
    for word in words:
        if len(Word.objects.filter(Q(word = word['word']) | Q(kana = word['kana']))) > 0:
            print('Skipped: "{} - {}" already exists.'.format(word['word'], word['kana']))
            continue
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
            print('Failed: "{} - {}" {}'.format(word['word'], word['kana'], str(e)))
        print('Added: "{} - {}"'.format(word['word'], word['kana']))

