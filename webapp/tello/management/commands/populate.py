import json
from django.core.management.base import BaseCommand
from tello.models import VocabularyCategory, VocabularyWord

MASTER_VOCAB_JSON = '''
{
    "KnownVocabularyList": [
      {
        "Category": "Nouns",
        "Words": [
          "apple", "ball", "bed", "bird", "book", "car", "cat", "chair", "dog", "door",
          "fish", "flower", "girl", "hat", "house", "milk", "moon", "pencil", "sun", "table",
          "tree", "water", "boy", "bread", "shoe", "school", "cloud", "clock", "grass", "shirt"
        ]
      },
      {
        "Category": "Verbs",
        "Words": [
          "eat", "drink", "jump", "run", "sit", "stand", "read", "write", "look", "open",
          "close", "sing", "dance", "play", "sleep", "swim", "walk", "cry", "laugh", "talk"
        ]
      },
      {
        "Category": "Adjectives",
        "Words": [
          "big", "small", "happy", "sad", "red", "blue", "yellow", "green", "black", "white",
          "good", "bad", "soft", "hard", "cold", "hot", "new", "old", "clean", "dirty"
        ]
      },
      {
        "Category": "Pronouns",
        "Words": [
          "I", "you", "he", "she", "it", "we", "they", "me", "him", "her"
        ]
      },
      {
        "Category": "Prepositions",
        "Words": [
          "in", "on", "under", "over", "behind", "next", "between", "near", "far", "inside"
        ]
      },
      {
        "Category": "Conjunctions",
        "Words": [
          "and", "or", "but", "because", "if"
        ]
      },
      {
        "Category": "Adverbs",
        "Words": [
          "now", "later", "soon", "always", "never", "here", "there", "up", "down", "fast"
        ]
      },
      {
        "Category": "Numbers",
        "Words": [
          "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"
        ]
      },
      {
        "Category": "Miscellaneous",
        "Words": [
          "yes", "no", "please", "thank you", "hello", "goodbye", "friend", "family", "happy", "love",
          "time", "day", "night", "morning", "evening", "food", "drink", "story", "game", "color"
        ]
      },
      {
        "Category": "Animal Names",
        "Words": [
          "cow", "sheep", "goat", "pig", "duck", "frog", "tiger", "lion", "elephant", "monkey"
        ]
      },
      {
        "Category": "Action Words",
        "Words": [
          "start", "stop", "ask", "answer", "listen"
        ]
      }
    ]
  }
'''


class Command(BaseCommand):
    help = "Populate the vocabulary master list"

    def handle(self, *args, **kwargs):
        vocab_data = json.loads(MASTER_VOCAB_JSON)

        for category_data in vocab_data["KnownVocabularyList"]:
            category_name = category_data["Category"]
            category, _ = VocabularyCategory.objects.get_or_create(
                name=category_name)

            for word in category_data["Words"]:
                # Check if word already exists before inserting
                if not VocabularyWord.objects.filter(word=word).exists():
                    VocabularyWord.objects.create(word=word, category=category)

        self.stdout.write(self.style.SUCCESS(
            "Vocabulary list successfully populated!"))
