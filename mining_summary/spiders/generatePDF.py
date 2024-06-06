from enum import Enum, auto

import scrapy
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import splitLines
from scrapy.crawler import CrawlerProcess
import os
import html
import re
import nltk
from model import client  # Import klienta Azure OpenAI z model.py
from model import generate_openai_completion
import mysql.connector
from mysql.connector import Error

nltk.download('punkt')

host_name = 'localhost'
user_name = 'newsletter'
user_password = 'newsletter'
db_name = 'newsletter'


class WhatToSave(Enum):
    LINK = auto()
    ARTICLE = auto()
    SUMMARY = auto()
    SCRAPY = auto()


class Database:

    def connect_to_db(self, host_name, user_name, user_password, db_name):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
            print("Połączenie z bazą danych MySQL udane")
        except Error as e:
            print(f"Błąd '{e}' podczas połączenia z bazą danych")

        return connection


    def fetch_summaries_by_category(self, connection, category):
        cursor = connection.cursor()
        query = "SELECT a.link, a.id, ad.category, ad.summary FROM article a JOIN article_details ad ON a.id = ad.article_id WHERE ad.category = %s "
        try:
            cursor.execute(query, (category,))
            records = cursor.fetchall()
            return records
        except Error as e:
            print(f"Błąd '{e}' podczas pobierania streszczeń")
            return []
        finally:
            cursor.close()

    def generate_pdf_by_category(self, connection, category):
        records = self.fetch_summaries_by_category(connection, category)
        if not records:
            print(f"No summaries found for category {category}")
            return

        pdf_filename = os.path.join(os.getcwd(), f"{category}_newsletter.pdf")
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter
        margin = 40
        column_width = width - 2 * margin
        y = height - margin

        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, y, "NEWSLETTER")
        y -= 22 + 20

        c.setFont("Helvetica", 12)

        # Funkcja do podziału tekstu na linie
        def wrap_text(text, width):
            from reportlab.pdfbase.pdfmetrics import stringWidth
            words = text.split()
            lines = []
            line = []
            for word in words:
                test_line = ' '.join(line + [word])
                if stringWidth(test_line, "Helvetica", 12) > width:
                    lines.append(' '.join(line))
                    line = [word]
                else:
                    line.append(word)
            lines.append(' '.join(line))
            return lines

        for record in records:
            link = record[0]
            summary = record[3]
            text_link = f"{link}\n"
            text_summary = f"{summary}\n\n"

            lines_link = wrap_text(text_link, column_width)
            lines_summary = wrap_text(text_summary, column_width)


            for line in lines_link:
                if y < margin + 14:
                    c.showPage()
                    y = height - margin
                    c.setFont("Helvetica", 12)
                c.drawString(margin, y, line)
                y -= 14


            for line in lines_summary:
                if y < margin + 14:
                    c.showPage()
                    y = height - margin
                    c.setFont("Helvetica", 12)
                c.drawString(margin, y, line)
                y -= 14

            y -= 14

        c.save()
        print(f"PDF generated: {pdf_filename}")


class PDF():
    name = "mining_summary"

    host_name = 'localhost'
    user_name = 'newsletter'
    user_password = 'newsletter'
    db_name = 'newsletter'
    db = Database()
    connection = None
    summary_instructions = ""

    def start_requests(self):
        self.connection = self.db.connect_to_db(self.host_name, self.user_name, self.user_password, self.db_name)
        self.db.generate_pdf_by_category(self.connection, "R")
        self.db.generate_pdf_by_category(self.connection, "FOCM")


if __name__ == "__main__":

    pdf_instance = PDF()
    pdf_instance.start_requests()


