import json
import unittest
from ui_assets.evaluator import ResponseEvaluator

class DummyState:
    def __init__(self, mode="INTERACTION", engagement_level="High", response_length=5):
        self.mode = type("Mode", (), {"value": mode})()
        self.engagement_level = type("Engagement", (), {"value": engagement_level})()
        self.response_length = response_length

class TestResponseEvaluator(unittest.TestCase):

    def setUp(self):
        # Load a sample story
        filename = 'dataset/story_corpus/stories/easy/story2.json'
        with open(filename, "r", encoding="utf-8") as file:
            story_data = json.load(file)

        from story_handler.story import Story
        self.story = Story(story_data)
        self.evaluator = ResponseEvaluator(self.story)

        # Dummy session state
        self.state_history = [
            DummyState("NARRATION", "Medium"),
            DummyState("INTERACTION", "Low"),
            DummyState("INTERACTION", "Low"),
            DummyState("INTERACTION", "Low")
        ]

    def test_low_score_on_unrelated_response(self):
        # Completely off-topic response
        bad_response = "I like pizza and dinosaurs."
        result = self.evaluator.evaluate(
            bad_response,
            self.state_history,
            prompts_given=5,
            prompts_answered=1
        )
        print("Evaluation Result:", result)
        self.assertLess(result['final_score'], 20.0, "Expected final score to be < 20")


if __name__ == '__main__':
    unittest.main()

