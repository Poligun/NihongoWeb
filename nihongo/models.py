from django.db import models

# Create your models here.
class Word(models.Model):
    word = models.CharField(max_length = 100)
    kana = models.CharField(max_length = 100)

    def __str__(self):
        return '{}({})'.format(self.word, self.kana)

    def toObject(self):
        word = {
            'word': self.word,
            'kana': self.kana,
            'wordTypes': [t.get_wordType_display() for t in self.wordtype_set.all()],
            'meanings': []
        }
        for meaningObject in self.meaning_set.all():
            meaning = {
                'meaning': meaningObject.meaning,
                'explanation': meaningObject.explanation,
                'examples': []
            }
            for exampleObject in meaningObject.example_set.all():
                meaning['examples'].append({
                    'example': exampleObject.example,
                    'translation': exampleObject.translation,
                    'occurences': [o.occurence for o in sorted(exampleObject.occurence_set.all(), key = lambda o: o.index)]
                })
            word['meanings'].append(meaning)
        return word

class WordType(models.Model):
    Types = [
        (0, 'サ变动词'),
        (1, '一段动词'),
        (2, '一类形容词'),
        (3, '二类形容词'),
        (4, '五段动词'),
        (5, '他动词'),
        (6, '代词'),
        (7, '副词'),
        (8, '助词'),
        (9, '名词'),
        (10, '常用语'),
        (11, '接尾词'),
        (12, '接续助词'),
        (13, '接续词'),
        (14, '自动词'),
        (15, '语气词'),
        (16, '连体词'),
        (17, '连语'),
        (18, '量词')
    ]
    TypeDict = dict((v2, v1) for v1, v2 in Types)

    word     = models.ForeignKey(Word)
    wordType = models.IntegerField(default = TypeDict['名词'], choices = Types)

    def __str__(self):
        return '{} - {}'.format(self.word, self.get_wordType_display())

    @property
    def typeName(self):
        return Types[self.wordType][1]


class Meaning(models.Model):
    word        = models.ForeignKey(Word)
    meaning     = models.CharField(max_length = 300)
    explanation = models.CharField(max_length = 300)

    def __str__(self):
        return '{}: {} - {}'.format(self.word, self.meaning, self.explanation)

class Example(models.Model):
    meaning     = models.ForeignKey(Meaning)
    example     = models.CharField(max_length = 300)
    translation = models.CharField(max_length = 300)

    def __str__(self):
        return '{}: {} - {}'.format(self.meaning.word, self.example, self.translation)

class Occurence(models.Model):
    example = models.ForeignKey(Example)
    occurence = models.CharField(max_length = 100)
    index   = models.IntegerField()

class User(models.Model):
    email     = models.CharField(max_length = 100, unique = True)
    password  = models.CharField(max_length = 100)
    name      = models.CharField(max_length = 100)

class Privellege(models.Model):

    Privelleges = [
        (101, 'AddUser'),
    ]
    PrivellegeDict = dict((v2, v1) for v1, v2 in Privelleges)
    
    user = models.ForeignKey(User)
    privellege = models.IntegerField(choices = Privelleges)
    

class PendingUser(models.Model):
    email     = models.CharField(max_length = 100)
    name      = models.CharField(max_length = 100)
    message   = models.CharField(max_length = 300)
    activated = models.BooleanField(default = False)

class Session(models.Model):
    user         = models.ForeignKey(User)
    sessionToken = models.CharField(max_length = 100)
    actionCount  = models.IntegerField(default = 0)
    expired      = models.BooleanField(default = False)
    creationDate = models.DateTimeField(auto_now_add = True)
    expiryDate   = models.DateTimeField(auto_now_add = True)

"""
class Log(models.Model):
    user   = models.ForeignKey(User)
    action = models.
"""


class SingleChoiceQuestion(models.Model):
    user          = models.ForeignKey(User)
    word          = models.ForeignKey(Word)
    correctChoice = models.IntegerField()
    answered      = models.BooleanField(default = False)

class Option(models.Model):
    question = models.ForeignKey(SingleChoiceQuestion)
    index    = models.IntegerField()
    option   = models.CharField(max_length = 100)
