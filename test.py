from orm import *
import datetime
import os
import time
from collections import Counter
import config
import logging

logging.basicConfig(level=logging.DEBUG, filename='./logs/' + config.CHARACTER_JOURNAL_FILE_NAME + '.log')
#logging.basicConfig(level=logging.INFO, filename='./logs/info.log')
##todo
######
##ad try catch. if there is a fail, rewrite a copy with datetime so we can re-use
###find the start time and delete everything after that point?

###have phrase count. no need to keep duplicating phrases
### get first 1000 top phrases and then do a copy of word_count
### need to make each data model into it's own class. specific functionality should go in there
### add multiple user definitions, would require some sort of config file
### add docker container option
### check out auto starting the saving script when uo is launched
### separate the phrase save from the word save and word count

for existingWord in wordTable.all(wordTable):
	try:
		wordTable.wordList.append(existingWord)
	except Exception:
		logging.exception("Unable to append %s to wordlist", existingWord)

wordCountList = list()

logging.info('Starting...')

#work through ignored words
count = 1

for x in ignore_list.all(ignore_list):
	ignore_list.ignored_words[count] = {}
	ignore_list.ignored_words[count]['word'] = x
	count = count + 1

ignoreWordList = list()

for x in ignore_list.ignored_words:
	print('ignored word:', ignore_list.ignored_words[x]['word']['word_text'])
	ignoreWordList.append(ignore_list.ignored_words[x]['word']['word_text'])

ignoreWordlist = tuple(ignoreWordList)

end = time.time() + config.UO_WORDS_RUN_TIME_SECONDS

#the advantage to  setting this to true is that it can be run while uo client is running
#and pick up log files while playing
while(True):

	try:
		time.sleep(config.TIME_BETWEEN_BATCHES)

		if(time.time() > end):
			logging.info('Done!')
			exit()

		lines = open(config.UO_LOGS_PATH + '/' + config.CHARACTER_JOURNAL_FILE_NAME, 'rt')

		outfile = open(config.UO_LOGS_PATH + '/' + config.CHARACTER_JOURNAL_FILE_NAME_COPY, 'wt')

		for line in lines:

			wordLine = tuple(filter(None, line.split(' ')))

			ignore = False

			for word in wordLine:
				if word in ignoreWordlist:
					logging.info( str(word) + 'is in' + str(ignoreWordList))
					ignore = True
					break

				if ignore == True:
					logging.info('line ' + str(line) + ' has been ignored!')
					continue
			
				#todo - have a better way to clean this up
				print(line.strip('.').rstrip(), file=outfile)
				print('.', end='', flush=True)

		outfile.close()

		lines = open(config.UO_LOGS_PATH + '/' + config.CHARACTER_JOURNAL_FILE_NAME, 'rt').readlines()

		num_lines = sum(1 for line in open(config.UO_LOGS_PATH + '/' + config.CHARACTER_JOURNAL_FILE_NAME_COPY))

		logging.info('number of lines : ' + str(num_lines))
		
		#writelines is to remove all of the lines
		#this needs to be improved. there was an issue where lines were remaning at end of file
		# 	even though they were being added to the copy
		open(config.UO_LOGS_PATH + '/' + config.CHARACTER_JOURNAL_FILE_NAME, 'w').writelines(lines[num_lines:1000000])

		with open(config.UO_LOGS_PATH + '/' + config.CHARACTER_JOURNAL_FILE_NAME_COPY) as f:
		    fileCopy = f.readlines()

		content = [x.strip() for x in fileCopy]

		for x in content:

			newPhrase = phrase()
			newPhrase.phrase_text = x
			newPhrase.created_at = datetime.datetime.now()
			newPhrase.save()

			logging.info('New phrase saved. ID is ' + str(newPhrase.id))

			phrase_word = tuple(filter(None, newPhrase.phrase_text.split(' ')))

			for w in phrase_word:

				logging.info('searching for ' + str(w))
				existingWord = {}
				for value in wordTable.wordList:
					if value['word_text'] == w:
						existingWord = value
						logging.info('found the word!' + value['word_text'])
						break

				if(len(existingWord) != False):
					
					wordCount.wordCountList.append(existingWord['word_id'])

					newWordPhrase = phraseWord()
					newWordPhrase.word_id = existingWord['word_id']
					newWordPhrase.phrase_id = newPhrase.id
					newWordPhrase.created_at = datetime.datetime.now()
					newWordPhrase.save()

				else:

					logging.info('saving new word: ' + str(w))
					newWord = wordTable()
					newWord.word_text = w
					newWord.created_at = datetime.datetime.now()
					newWord.save()

					wordCount.wordCountList.append(newWord.word_id)

					wordTable.wordList.append({'word_text' : newWord.word_text, 'word_id' : newWord.word_id})

					newWordPhrase = phraseWord()
					newWordPhrase.word_id = newWord.word_id
					newWordPhrase.phrase_id = newPhrase.id
					newWordPhrase.created_at = datetime.datetime.now()
					newWordPhrase.save()

		wordCounts = [{"word_id": key, "count": value} for key, value in Counter(wordCount.wordCountList).items()]

		##deal with word counts
		for wor in wordCounts:
			try:
				wordC = wordCount.select().where(wordCount.word_id == wor['word_id']).first()

				if(wordC != None):
					query = wordCount.update(count=wordCount.count + wor['count']).where(wordCount.word_id == wor['word_id'])
					query.execute()
				else:
					newWordCount = wordCount()
					newWordCount.word_id = wor['word_id']
					newWordCount.count = wor['count']
					newWordCount.created_at = datetime.datetime.now()
					newWordCount.save()
			except Exception:
				logging.exception("Unable to process word count for %s", wor['word_id'])

	except Exception:
		logging.exception("While loop failed")
