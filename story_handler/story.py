import json


class Story:
    def __init__(self, json_data):
        """
        Initialize the Story object by parsing the JSON data.
        :param json_data: Dictionary containing story details.
        """
        self.story_id = json_data.get("StoryID", "Unknown")
        self.title = json_data.get("Title", "Untitled")
        self.theme = json_data.get("Theme", "Unknown")
        self.complexity = json_data.get("StoryComplexity", "Unknown")
        self.word_count = json_data.get("WordCount", 0)
        self.target_age = json_data.get("TargetAgeGroup", "Unknown")
        self.narrative_arc = json_data.get("NarrativeArc", {})
        self.vocabulary = json_data.get("Vocabulary", {})
        self.sentences = {s["SentenceID"]
            : s for s in json_data.get("Sentences", [])}

        # Flattened list of sentence IDs
        self._all_sentence_ids = sum(self.narrative_arc.values(), [])
        # Track the current position
        self._current_index = 0 if self._all_sentence_ids else None

    def get_sentence(self, sentence_id):
        """
        Retrieve a sentence by its ID.
        :param sentence_id: The ID of the sentence to fetch.
        :return: Dictionary containing sentence details or None if not found.
        """
        return self.sentences.get(sentence_id)

    def start_story(self):
        """
        Start the story from the introduction.
        :return: First sentence dictionary or None if unavailable.
        """
        if self._all_sentence_ids:
            self._current_index = 0
            return self.get_sentence(self._all_sentence_ids[0])
        return None

    def get_next_sentence(self):
        """
        Get the next sentence in the story.
        :return: The next sentence dictionary or None if at the end.
        """
        if self._current_index is None:
            return self.start_story()

        if self._current_index + 1 < len(self._all_sentence_ids):
            self._current_index += 1
            return self.get_sentence(self._all_sentence_ids[self._current_index])

        return None  # End of story

    def reset_story(self):
        """
        Reset the story to the beginning.
        """
        self._current_index = 0 if self._all_sentence_ids else None

    def get_story_summary(self):
        """
        Get a summary of the story details.
        :return: A dictionary with key details of the story.
        """
        return {
            "StoryID": self.story_id,
            "Title": self.title,
            "Theme": self.theme,
            "Complexity": self.complexity,
            "WordCount": self.word_count,
            "TargetAgeGroup": self.target_age
        }

    def get_interaction_prompt(self):
        """
        Get the interaction prompt for the current sentence.
        """
        if self._current_index is not None:
            sentence = self.get_sentence(
                self._all_sentence_ids[self._current_index])
            return sentence.get("InteractionPrompt", "")
        return ""

    def get_fun_questions(self):
        """
        Get fun questions related to the current sentence.
        """
        if self._current_index is not None:
            sentence = self.get_sentence(
                self._all_sentence_ids[self._current_index])
            return sentence.get("FunQuestions", [])
        return []

    def get_vocabulary_definition(self, word):
        """
        Get the definition of a vocabulary word.
        :param word: The word to look up.
        :return: Definition string or None if not found.
        """
        return self.vocabulary.get(word)

    def get_story_progress(self):
        """
        Get the percentage of the story completed.
        :return: A float representing completion percentage.
        """
        if self._current_index is None or not self._all_sentence_ids:
            return 0.0
        return round((self._current_index + 1) / len(self._all_sentence_ids) * 100, 2)

    def get_current_image(self):
        """
        Get the related image for the current sentence.
        """
        if self._current_index is not None:
            sentence = self.get_sentence(
                self._all_sentence_ids[self._current_index])
            return sentence.get("RelatedImage", "")
        return ""

    def get_vocabulary_info(self):
        """
        Check if the current sentence contains a vocabulary word.
        :return: A tuple (bool, word, definition) if vocabulary is present, otherwise (False, None, None).
        """
        if self._current_index is not None:
            sentence = self.get_sentence(
                self._all_sentence_ids[self._current_index])
            if sentence.get("IsVocabularyPresent", False):
                for word in self.vocabulary.keys():
                    if word.lower() in sentence["Text"].lower():
                        return True, word, self.vocabulary[word]
        return False, None, None


# Example Usage:
if __name__ == "__main__":
    filename = 'dataset/story_corpus/stories/easy/story2.json'
    with open(filename, "r", encoding="utf-8") as file:
        story_data = json.load(file)

    story = Story(story_data)
    print("Story Summary:", story.get_story_summary())

    sentence = story.start_story()
    while sentence:
        print("\nNarration:", sentence["Text"])
        print("Prompt:", story.get_interaction_prompt())
        print("Fun Questions:", story.get_fun_questions())
        print("Image:", story.get_current_image())
        print("Progress:", story.get_story_progress(), "%")
        sentence = story.get_next_sentence()
