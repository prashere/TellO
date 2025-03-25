import json
import numpy as np
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rl_framework.state import ResponseLength
from story_handler.story import Story


RESPONSE_LENGTH_SCORES = {
    ResponseLength.SHORT: 2,
    ResponseLength.MEDIUM: 4,
    ResponseLength.LONG: 6
}


class ResponseEvaluator:
    def __init__(self, story: Story):
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
        self.arc_vectors = self.vectorizer.fit_transform(
            self.arc_texts_list) if self.arc_texts_list else None

    def evaluate_vocabulary(self, response: str) -> float:
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
                # Threshold for a fuzzy match.
                if fuzz.ratio(keyword, word) > 80:
                    matched += 1
                    break
        if not keywords:
            return 1.0
        return matched / len(keywords)

    def evaluate_structure_similarity(self, response: str) -> float:
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
        return float(np.mean(similarities))

    def evaluate_response_length(self, response: str) -> float:
        """
        Evaluate the response length. Assumes an ideal response is between 10 and 50 words.
        If too short or too long, the score is reduced.
        :param response: The child's response as a string.
        :return: Score between 0 and 1.
        """
        words = response.split()
        count = len(words)
        if count < 10:
            return count / 10.0
        elif count > 50:
            return max(0, 1 - (count - 50) / 50.0)
        else:
            return 1.0

    def calculate_average_engagement(self, state_history: list) -> float:
        """
        Compute the average engagement level across all states in the session.
        :param state_history: List of State objects.
        :return: Average engagement score between 0 and 1.
        """
        mapping = {"High": 1.0, "Medium": 0.5, "Low": 0.0}
        engagement_scores = [mapping.get(
            state.engagement_level.value, 0.5) for state in state_history]
        return round(np.mean(engagement_scores), 2) if engagement_scores else 0.5

    def calculate_prompt_interaction_ratio(self, prompts_given: int, prompts_answered: int) -> float:
        if prompts_given == 0:
            return "N/A"
        return round((prompts_answered / prompts_given) * 100, 2)

    def state_summary(self, state_history: list) -> dict:
        """
        Generates a summary from the history of states.
        For example, count the frequency of each mode and compute average engagement.
        :param state_history: List of State objects.
        :return: Dictionary summarizing state statistics.
        """
        mode_counts = {}
        for state in state_history:
            mode_str = state.mode.value
            mode_counts[mode_str] = mode_counts.get(mode_str, 0) + 1
        avg_engagement = self.calculate_average_engagement(state_history)
        return {
            "mode_counts": mode_counts,
            "average_engagement": avg_engagement
        }

    def evaluate(self, response: str, state_history: list, prompts_given, prompts_answered) -> dict:
        """
        Combine all metrics into a final evaluation score.
        Weights:
          - Vocabulary: 40%
          - Structure and similarity: 30%
          - Response length: 20%
          - Engagement (averaged over session): 10%
        :param response: The child's response as a string.
        :param state_history: A list of State objects recorded during the session.
        :return: Dictionary with individual metric scores, final weighted score, and state summary.
        """
        vocab_score = self.evaluate_vocabulary(response)
        structure_score = self.evaluate_structure_similarity(response)
        length_score = self.evaluate_response_length(response)
        avg_engagement_score = self.calculate_average_engagement(state_history)

        final_score = (0.4 * vocab_score +
                       0.3 * structure_score +
                       0.2 * length_score +
                       0.1 * avg_engagement_score)

        eval_report = {
            "vocabulary": round(vocab_score, 2),
            "structure": round(structure_score, 2),
            "length": round(length_score, 2),
            "average_engagement": avg_engagement_score,
            "final_score": round(final_score * 100, 2)  # percentage
        }

        eval_report["prompt_interaction_ratio"] = self.calculate_prompt_interaction_ratio(
            prompts_given, prompts_answered)
        eval_report["state_summary"] = self.state_summary(state_history)

        return eval_report


# Example usage:
if __name__ == "__main__":
    # Dummy state for demonstration:
    class DummyState:
        def __init__(self, mode="INTERACTION", engagement_level="High", response_length=5):
            self.mode = type("Mode", (), {"value": mode})()
            self.engagement_level = type(
                "Dummy", (), {"value": engagement_level})
            self.response_length = response_length

    dummy_state_history = [
        DummyState("NARRATION", "Medium", 0),
        DummyState("INTERACTION", "High", 8),
        DummyState("INTERACTION", "Low", 0),
        DummyState("INTERACTION", "Medium", 10)
    ]

    child_response = "The Lion gathered all animals and promised peace."

    filename = 'dataset/story_corpus/stories/easy/story2.json'
    with open(filename, "r", encoding="utf-8") as file:
        story_data = json.load(file)

    from story_handler.story import Story
    story = Story(story_data)

    evaluator = ResponseEvaluator(story)
    scores = evaluator.evaluate(child_response, dummy_state_history)
    print("Evaluation Scores:", scores)
