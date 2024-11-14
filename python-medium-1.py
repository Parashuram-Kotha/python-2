import json
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

class Flashcard:
    def __init__(self, question, answer, category):
        self.question = question
        self.answer = answer
        self.category = category
        self.status = 'unreviewed'  # Tracks whether the card has been reviewed

    def check_answer(self, user_answer):
        if user_answer.lower() == self.answer.lower():
            self.status = 'correct'
            return True
        else:
            self.status = 'incorrect'
            return False

class FlashcardApp(App):
    def build(self):
        self.flashcards = []
        self.current_card = None
        self.points = 0
        self.level = 1
        self.streak = 0
        self.achievements = {
            "50_questions": False,
            "200_points": False,
            "10_streak": False,
            "questions_answered": 0
        }
        
        self.load_progress()

        self.layout = BoxLayout(orientation='vertical')
        self.points_label = Label(text=f"Points: {self.points}")
        self.level_label = Label(text=f"Level: {self.level}")
        self.streak_label = Label(text=f"Streak: {self.streak}")
        self.achievements_label = Label(text="Achievements: None")
        
        self.layout.add_widget(self.points_label)
        self.layout.add_widget(self.level_label)
        self.layout.add_widget(self.streak_label)
        self.layout.add_widget(self.achievements_label)

        self.question_label = Label(text="Press 'Next' to start reviewing")
        self.answer_input = TextInput(hint_text="Enter your answer", multiline=False)

        self.submit_btn = Button(text="Submit Answer")
        self.submit_btn.bind(on_press=self.check_answer)

        self.next_btn = Button(text="Next Flashcard")
        self.next_btn.bind(on_press=self.show_next_card)

        self.save_btn = Button(text="Save Progress")
        self.save_btn.bind(on_press=self.save_progress)

        self.add_flashcard_btn = Button(text="Add Flashcard")
        self.add_flashcard_btn.bind(on_press=self.show_add_flashcard_popup)

        self.layout.add_widget(self.question_label)
        self.layout.add_widget(self.answer_input)
        self.layout.add_widget(self.submit_btn)
        self.layout.add_widget(self.next_btn)
        self.layout.add_widget(self.save_btn)
        self.layout.add_widget(self.add_flashcard_btn)

        return self.layout

    def show_next_card(self, instance):
        if self.flashcards:
            self.current_card = self.flashcards[0]
            self.question_label.text = self.current_card.question
            self.answer_input.text = ""
        else:
            self.question_label.text = "No more flashcards to review."

    def check_answer(self, instance):
        if self.current_card:
            user_answer = self.answer_input.text
            self.achievements["questions_answered"] += 1
            if self.current_card.check_answer(user_answer):
                self.points += 10
                self.streak += 1
                if self.streak % 5 == 0:
                    self.points += 20
                self.points_label.text = f"Points: {self.points}"
                self.streak_label.text = f"Streak: {self.streak}"
                self.question_label.text = "Correct!"
                self.check_level()
                self.check_achievements()
            else:
                self.streak = 0
                self.streak_label.text = f"Streak: {self.streak}"
                self.question_label.text = f"Incorrect! The correct answer is {self.current_card.answer}"

    def check_level(self):
        if self.points >= 100:
            self.level = 3
        elif self.points >= 50:
            self.level = 2
        else:
            self.level = 1
        self.level_label.text = f"Level: {self.level}"

    def check_achievements(self):
        if self.achievements["questions_answered"] >= 50 and not self.achievements["50_questions"]:
            self.achievements["50_questions"] = True
            self.achievements_label.text = "Unlocked Achievement: Answered 50 Questions!"
        if self.points >= 200 and not self.achievements["200_points"]:
            self.achievements["200_points"] = True
            self.achievements_label.text = "Unlocked Achievement: 200 Points!"
        if self.streak >= 10 and not self.achievements["10_streak"]:
            self.achievements["10_streak"] = True
            self.achievements_label.text = "Unlocked Achievement: 10 Answer Streak!"

    def save_progress(self):
        data = {
            "flashcards": [(card.question, card.answer, card.category) for card in self.flashcards],
            "points": self.points,
            "streak": self.streak,
            "achievements": self.achievements
        }
        with open('progress.json', 'w') as file:
            json.dump(data, file)
        print("Progress saved!")

    def load_progress(self):
        try:
            with open('progress.json', 'r') as file:
                data = json.load(file)
                self.flashcards = [Flashcard(q, a, c) for q, a, c in data["flashcards"]]
                self.points = data["points"]
                self.streak = data["streak"]
                self.achievements = data["achievements"]
                print("Progress loaded successfully!")
        except FileNotFoundError:
            print("No saved progress found.")

    def show_add_flashcard_popup(self, instance):
        layout = BoxLayout(orientation='vertical')
        question_input = TextInput(hint_text="Enter Question")
        answer_input = TextInput(hint_text="Enter Answer")
        category_input = TextInput(hint_text="Enter Category")

        add_button = Button(text="Add Flashcard")
        add_button.bind(on_press=lambda x: self.add_flashcard(question_input.text, answer_input.text, category_input.text))

        layout.add_widget(question_input)
        layout.add_widget(answer_input)
        layout.add_widget(category_input)
        layout.add_widget(add_button)

        popup = Popup(title="Add Flashcard", content=layout, size_hint=(0.8, 0.5))
        popup.open()

    def add_flashcard(self, question, answer, category):
        if question and answer and category:  # Ensure fields are filled
            new_flashcard = Flashcard(question, answer, category)
            self.flashcards.append(new_flashcard)
            print(f"Added Flashcard: {question} - {answer} (Category: {category})")
        else:
            print("Please fill in all fields.")

if __name__ == "__main__":
    FlashcardApp().run()
