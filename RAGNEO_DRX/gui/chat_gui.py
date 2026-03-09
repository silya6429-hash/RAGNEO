import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading

from rag.rag_pipeline import RAGPipeline


class ChatGUI:

    def __init__(self):

        self.rag = RAGPipeline()

        self.root = tk.Tk()
        self.root.title("RAG Chat")

        self.root.geometry("800x600")

        # окно чата
        self.chat_area = ScrolledText(
            self.root,
            wrap=tk.WORD
        )

        self.chat_area.pack(
            padx=10,
            pady=10,
            fill=tk.BOTH,
            expand=True
        )

        # поле ввода
        self.input_field = tk.Entry(
            self.root,
            font=("Arial", 12)
        )

        self.input_field.pack(
            padx=10,
            pady=10,
            fill=tk.X
        )

        self.input_field.bind(
            "<Return>",
            self.send_message
        )

    # =============================
    # SEND MESSAGE
    # =============================

    def send_message(self, event=None):

        question = self.input_field.get()

        if not question.strip():
            return

        self.chat_area.insert(
            tk.END,
            f"\nВы: {question}\n"
        )

        self.input_field.delete(0, tk.END)

        threading.Thread(
            target=self.process_question,
            args=(question,)
        ).start()

    # =============================
    # PROCESS QUESTION
    # =============================

    def process_question(self, question):

        result = self.rag.ask(question)

        answer = result["answer"]

        self.chat_area.insert(
            tk.END,
            f"\nRAG: {answer}\n"
        )

        self.chat_area.see(tk.END)

    # =============================
    # RUN
    # =============================

    def run(self):

        self.root.mainloop()