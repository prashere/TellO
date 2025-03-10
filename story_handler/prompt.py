import json
import random

class PromptManager:
    def __init__(self, json_data):
        """
        Initialize the PromptManager by loading prompts from JSON data.
        :param json_data: Dictionary containing prompts.
        """
        self.prompts = json_data.get("prompts", [])
        self.prompts_by_category = self._organize_by_category()

    def _organize_by_category(self):
        """
        Organize prompts into a dictionary categorized by type.
        :return: Dictionary with categories as keys and lists of prompts as values.
        """
        categorized = {}
        for prompt in self.prompts:
            category = prompt["category"]
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(prompt)
        return categorized

    def get_prompt_by_id(self, prompt_id):
        """
        Retrieve a specific prompt by its ID.
        :param prompt_id: ID of the prompt to fetch.
        :return: Dictionary containing the prompt or None if not found.
        """
        for prompt in self.prompts:
            if prompt["id"] == prompt_id:
                return prompt
        return None

    def get_prompts_by_category(self, category):
        """
        Retrieve all prompts from a specific category.
        :param category: The category to filter prompts.
        :return: List of prompts in the category.
        """
        return self.prompts_by_category.get(category, [])

    def get_random_prompt(self, category=None):
        """
        Get a random prompt, optionally filtered by category.
        :param category: The category to filter by (optional).
        :return: A random prompt dictionary or None if no prompts are available.
        """
        if category:
            prompts = self.prompts_by_category.get(category, [])
        else:
            prompts = self.prompts
        
        if prompts:
            return random.choice(prompts)
        return None

# Example Usage:
if __name__ == "__main__":
    # Load JSON data (replace with actual file path if needed)
    filename = 'dataset/prompts.json'
    with open(filename, "r", encoding="utf-8") as file:
        prompt_data = json.load(file)

    prompt_manager = PromptManager(prompt_data)

    # Fetch and print examples
    print("Random Greeting Prompt:", prompt_manager.get_random_prompt("Greeting"))
    print("All Encouragement Prompts:", prompt_manager.get_prompts_by_category("Encouragement"))
    print("Specific Prompt by ID (E02):", prompt_manager.get_prompt_by_id("E02"))
