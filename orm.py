from functools import partial
from peewee import *
import datetime
import os

db = SqliteDatabase('data/uo-words.db')

class BaseModel(Model):
    class Meta:
        database = db

class wordTable(BaseModel):
	wordList = list()

	word_id = AutoField(primary_key=True)
	word_text = TextField()
	word_type_id = IntegerField()
	created_at = TextField()
	
	class Meta:
		table_name = 'word'

	def all(self):
		return(self
			.select(wordTable.word_text, wordTable.word_id)
			.dicts())


class wordCount(BaseModel):
	wordCountList = list()

	word_count_id = IntegerField(primary_key=True)
	word_id = IntegerField()
	count = IntegerField()
	created_at = TextField()

	class Meta:
		table_name = 'word_count'

class word_type(BaseModel):
	word_type_id = IntegerField(primary_key=True)
	type = TextField()
	created_at = TextField()

	class Meta:
		table_name = 'word_type'

class phrase(BaseModel):
	phrase_id = IntegerField()
	phrase_text = TextField()
	created_at = TextField()

	class Meta:
		table_name = 'phrase'

class phraseWord(BaseModel):
	phrase_word_id = IntegerField(primary_key=True)
	phrase_id = IntegerField()
	word_id = IntegerField()

	class Meta:
		table_name = 'phrase_word'

class ignore_list(BaseModel):
	ignored_words = {}
	
	word_text = TextField()
	disabled = IntegerField()
	ignore_phrase = IntegerField(primary_key=True)

	class Meta:
		table_name = 'ignore_list'

	def all(self):
		return (self
			.select(ignore_list.word_text, ignore_list.ignore_phrase)
			.where(ignore_list.disabled == 0)
			.dicts())