import json
import numpy as np
from fuzzywuzzy import fuzz  # Alternatively, you can use rapidfuzz for better performance.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from story_handler.story import Story

class ResponseEvaluator:
    def __init__(self, story):
        """
        Initialize the evaluator with a Story object.
        Precompute narrative arc texts and TF-IDF vectors for lightweight similarity evaluation.
        :param story: An instance of the Story class.
        """
        self.story = story
        
        # Build a text representation for each narrative arc by concatenating its sentences.
        self.arc_texts = {}
        for arc, sentence_ids in self.story.narrative_arc.items():
            texts = []
            for sid in sentence_ids:
                sentence = self.story.get_sentence(sid)
                if sentence and "Text" in sentence:
                    texts.append(sentence["Text"])
            self.arc_texts[arc] = " ".join(texts)
        
        # Precompute TF-IDF vectors for all narrative arc texts.
        self.arc_names = list(self.arc_texts.keys())
        self.arc_texts_list = [self.arc_texts[arc] for arc in self.arc_names]
        self.vectorizer = TfidfVectorizer()
        self.arc_vectors = self.vectorizer.fit_transform(self.arc_texts_list) if self.arc_texts_list else None
        # if self.arc_texts_list:
        #     self.arc_vectors = self.vectorizer.fit_transform(self.arc_texts_list)
        # else:
        #     self.arc_vectors = None
        
    def evaluate_vocabulary(self, response):
        """
        Evaluate vocabulary usage by checking if key vocabulary words appear in the response.
        Uses fuzzy matching to account for minor spelling differences.
        :param response: The child's response as a string.
        :return: Score between 0 and 1.
        """
        keywords = {word.lower() for word in self.story.vocabulary.keys()}
        response_words = set(response.lower().split())
        matched = 0
        for keyword in keywords:
            for word in response_words:
                if fuzz.ratio(keyword, word) > 80:  # Threshold for a fuzzy match.
                    matched += 1
                    break
        if not keywords:
            return 1.0  # If no vocabulary is defined, assume full score.
        return matched / len(keywords)

    def evaluate_structure_similarity(self, response):
        """
        Evaluate how well the response covers the story structure using cosine similarity.
        The response is compared against precomputed TF-IDF vectors of each narrative arc.
        :param response: The child's response as a string.
        :return: Averaged similarity score between 0 and 1.
        """
        if self.arc_vectors is None or self.arc_vectors.shape[0] == 0 or not response.strip():
            return 0.0
        response_vector = self.vectorizer.transform([response])
        similarities = cosine_similarity(response_vector, self.arc_vectors)[0]
        # Average the similarity scores across all narrative arcs.
        return float(np.mean(similarities))

    def evaluate_response_length(self, response):
        """
        Evaluate the response length. Assumes an ideal response is between 10 and 50 words.
        If too short or too long, the score is reduced.
        :param response: The child's response as a string.
        :return: Score between 0 and 1.
        """
        words = response.split()
        count = len(words)
        if count < 10:
            return count / 10.0  # Linear scaling for very short responses.
        elif count > 50:
            # If more than 50 words, deduct score linearly (e.g., 100 words yields 0 score).
            return max(0, 1 - (count - 50) / 50.0)
        else:
            return 1.0

    def evaluate_engagement(self, state):
        """
        Evaluate engagement using the state representation.
        This function assumes that the state object has an attribute 'engagement'
        with a value between 0 and 1.
        :param state: The state object.
        :return: Engagement score between 0 and 1.
        """
        # Fallback to 0.5 if state doesn't have an engagement attribute.
        return getattr(state, "engagement", 0.5)

    def evaluate(self, response, state):
        """
        Combine all the metrics into a final evaluation score.
        Weights:
          - Vocabulary: 40%
          - Structure and similarity: 30%
          - Response length: 20%
          - Engagement: 10%
        :param response: The child's response as a string.
        :param state: The current state (should include engagement info).
        :return: Dictionary with individual metric scores and final weighted score (percentage).
        """
        vocab_score = self.evaluate_vocabulary(response)
        structure_score = self.evaluate_structure_similarity(response)
        length_score = self.evaluate_response_length(response)
        engagement_score = self.evaluate_engagement(state)
        
        # Compute weighted sum of scores.
        final_score = (0.4 * vocab_score +
                       0.3 * structure_score +
                       0.2 * length_score +
                       0.1 * engagement_score)
        
        # Return detailed scores and final percentage.
        return {
            "vocabulary": vocab_score,
            "structure": structure_score,
            "length": length_score,
            "engagement": engagement_score,
            "final_score": round(final_score * 100, 2)  # percentage
        }

# Example usage:
if __name__ == "__main__":
    # Assuming you have a Story object already instantiated as 'story'
    # and a state object with an 'engagement' attribute.
    #
    # For this example, we'll define a dummy state:
    class DummyState:
        def __init__(self, engagement=0.7):
            self.engagement = engagement

    # Dummy state instance.
    state = DummyState(engagement=0.7)
    
    # Example response from the child.
    child_response = ("The Lion was a kind king who gathered all the animals for a meeting. "
                      "He promised they would live in peace and be friends. "
                      "Everyone listened carefully.")
    
    # Here you would instantiate your Story object from your story JSON.
    # For demonstration, let's assume 'story' is already created.
    # response_evaluator = ResponseEvaluator(story)
    
    filename = 'dataset/story_corpus/stories/easy/story2.json'
    with open(filename, "r", encoding="utf-8") as file:
        story_data = json.load(file)

    story = Story(story_data)
    # Assuming 'story' is available:
    evaluator = ResponseEvaluator(story)
    scores = evaluator.evaluate(child_response, state)
    print("Evaluation Scores:", scores)
    
    