import random
import tkinter as tk
from tkinter import messagebox, simpledialog

class QuizApp:
    def __init__(self, master, questions_file, top_players_file, num_questions=10):
        self.master = master
        self.questions_file = questions_file
        self.top_players_file = top_players_file
        self.num_questions = num_questions
        self.questions = self.get_content(self.questions_file)
        self.quest = self.select_questions(self.questions, self.num_questions)
        self.questions_dict = self.define_questions(self.quest)
        self.score = 0
        self.current_question_index = 0

        self.help_5050_used = False
        self.help_audience_used = False
        self.help_flip_used = False
        self.used_help = False

        self.player_name = self.get_player_name()
        self.setup_ui()
        self.ask_question()

    def setup_ui(self):
        self.master.title("Quiz Game")
        self.question_label = tk.Label(self.master, text="")
        self.question_label.pack()
        
        self.answer_buttons = []
        for i in range(4):
            button = tk.Button(self.master, text="", command=lambda idx=i: self.check_answer(idx))
            self.answer_buttons.append(button)
            button.pack(fill=tk.BOTH, expand=True)
        
        self.help_5050_button = tk.Button(self.master, text="50/50", command=self.use_5050)
        self.help_5050_button.pack(fill=tk.BOTH, expand=True)
        
        self.help_audience_button = tk.Button(self.master, text="Ask the Audience", command=self.use_audience)
        self.help_audience_button.pack(fill=tk.BOTH, expand=True)
        
        self.help_flip_button = tk.Button(self.master, text="Switch the Question", command=self.use_flip)
        self.help_flip_button.pack(fill=tk.BOTH, expand=True)

    def get_player_name(self):
        name = simpledialog.askstring("Player Name", "Enter your name:")
        if name:
            return name
        else:
            return "Player"

    def get_content(self, fname):
        with open(fname) as f:
            return f.readlines()

    def select_questions(self, questions, num_questions):
        ind = random.sample(range(len(questions)), num_questions)
        quest = [questions[i].strip() for i in ind]
        return quest

    def define_questions(self, quest):
        questions_dict = {}
        for question in quest:
            q, a = question.split("?")
            answers = [answer.strip() for answer in a.split(",")]
            questions_dict[q.strip()] = {"correct": answers[0], "all_answers": answers}
        return questions_dict

    def ask_question(self):
        self.used_help = False
        if self.current_question_index < self.num_questions:
            question = list(self.questions_dict.keys())[self.current_question_index]
            answers = self.questions_dict[question]["all_answers"]
            self.question_label.config(text=question)
            random.shuffle(answers)
            for i in range(len(answers)):
                self.answer_buttons[i].config(text=answers[i], command=lambda idx=i: self.check_answer(idx), state=tk.NORMAL)
        else:
            self.save_score()
            self.show_top_players()
            messagebox.showinfo("Quiz Complete", f"{self.player_name}, your score: {self.score}/{self.num_questions}")
            self.master.destroy()

    def check_answer(self, selected_index):
        question = list(self.questions_dict.keys())[self.current_question_index]
        correct_answer = self.questions_dict[question]["correct"]
        selected_answer = self.answer_buttons[selected_index].cget("text")
        if selected_answer == correct_answer:
            self.score += 1
        self.next_question()

    def next_question(self):
        self.current_question_index += 1
        self.ask_question()

    def use_5050(self):
        if self.used_help:
            messagebox.showinfo("Help Used", "You have already used help for this question.")
            return
        
        if not self.help_5050_used:
            self.help_5050_used = True
            self.used_help = True
            question = list(self.questions_dict.keys())[self.current_question_index]
            correct_answer = self.questions_dict[question]["correct"]
            all_answers = self.questions_dict[question]["all_answers"]
            wrong_answers = [ans for ans in all_answers if ans != correct_answer]
            if len(wrong_answers) >= 2:
                answers_to_remove = random.sample(wrong_answers, 2)
                for button in self.answer_buttons:
                    if button.cget("text") in answers_to_remove:
                        button.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("No Help Left", "You have already used 50/50 help.")

    def use_audience(self):
        if self.used_help:
            messagebox.showinfo("Help Used", "You have already used help for this question.")
            return
        
        if not self.help_audience_used:
            self.help_audience_used = True
            self.used_help = True
            question = list(self.questions_dict.keys())[self.current_question_index]
            all_answers = self.questions_dict[question]["all_answers"]
            
            # Generate random percentages for the answers
            percentages = [random.randint(1, 100) for _ in all_answers]
            total = sum(percentages)
            percentages = [int(p / total * 100) for p in percentages]
            
            # Adjust percentages to ensure they sum to 100
            difference = 100 - sum(percentages)
            percentages[0] += difference
            
            audience_poll = "\n".join([f"{all_answers[i]}: {percentages[i]}%" for i in range(len(all_answers))])
            messagebox.showinfo("Audience Poll", f"Audience Poll:\n{audience_poll}")
        else:
            messagebox.showinfo("No Help Left", "You have already used Ask the Audience help.")

    def use_flip(self):
        if self.used_help:
            messagebox.showinfo("Help Used", "You have already used help for this question.")
            return
        
        if not self.help_flip_used:
            self.help_flip_used = True
            self.used_help = True
            self.current_question_index += 1
            self.ask_question()
        else:
            messagebox.showinfo("No Help Left", "You have already used Switch the Question help.")

    def save_score(self):
        with open(self.top_players_file, "a") as f:
            f.write(f"{self.player_name}: {self.score}/{self.num_questions}\n")

    def show_top_players(self):
        with open(self.top_players_file, "r") as f:
            scores = f.readlines()
        valid_scores = []
        for score in scores:
            try:
                name, result = score.split(": ")
                points, total = result.split("/")
                valid_scores.append((name, int(points), int(total)))
            except ValueError:
                continue
        top_scores = sorted(valid_scores, key=lambda x: x[1], reverse=True)[:5]
        top_scores_str = "\n".join([f"{name}: {points}/{total}" for name, points, total in top_scores])
        messagebox.showinfo("Top Players", f"Top Players:\n{top_scores_str}")

def main():
    root = tk.Tk()
    app = QuizApp(root, "questions.txt", "top.txt")
    root.mainloop()

if __name__ == "__main__":
    main()

