import json
import mysql.connector
from mysql.connector import Error

class NewsAPI:
    def __init__(self):
        self.connection = self.connect()
        if self.connection is None:
            raise Exception("Failed to connect to the database")

    def connect(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='newsletter',
                password='newsletter',
                database='newsletter'
            )
            print("Connected to MySQL database")
            return connection
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return None

    def save_article(self, link, title, scrapy_text, source):
        cursor = self.connection.cursor()
        query = """INSERT INTO articles (link, title, scrapy_text, source) 
                   VALUES (%s, %s, %s, %s)"""
        values = (link, title, scrapy_text, source)
        try:
            cursor.execute(query, values)
            self.connection.commit()
            print(f"Article saved: {title}")
            return cursor.lastrowid
        except Error as e:
            print(f"Error saving article: {e}")
            return None
        finally:
            cursor.close()

    def save_summary(self, article_id, summary, category):
        cursor = self.connection.cursor()
        query = """INSERT INTO summaries (article_id, summary, category) 
                   VALUES (%s, %s, %s)"""
        values = (article_id, summary, category)
        try:
            cursor.execute(query, values)
            self.connection.commit()
            print(f"Summary saved for article ID: {article_id}")
        except Error as e:
            print(f"Error saving summary: {e}")
        finally:
            cursor.close()

    def get_categories(self):
        cursor = self.connection.cursor()
        query = "SELECT name FROM categories"
        try:
            cursor.execute(query)
            return [category[0] for category in cursor.fetchall()]
        except Error as e:
            print(f"Error fetching categories: {e}")
            return []
        finally:
            cursor.close()

    def add_subscription(self, user_id, category_name, frequency='weekly'):
        cursor = self.connection.cursor()
        query = """INSERT INTO subscriptions (user_id, category_id, frequency)
                   SELECT %s, id, %s FROM categories WHERE name = %s"""
        values = (user_id, frequency, category_name)
        try:
            cursor.execute(query, values)
            self.connection.commit()
            print(f"Subscription added for user {user_id} to category {category_name}")
        except Error as e:
            print(f"Error adding subscription: {e}")
        finally:
            cursor.close()

    def get_articles_by_category(self, category):
        cursor = self.connection.cursor()
        query = """
        SELECT a.id, a.title, s.summary 
        FROM articles a
        JOIN summaries s ON a.id = s.article_id
        WHERE s.category = %s 
        ORDER BY a.id DESC LIMIT 10
        """
        try:
            cursor.execute(query, (category,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching articles for category {category}: {e}")
            return []
        finally:
            cursor.close()

    def get_article(self, article_id):
        cursor = self.connection.cursor()
        query = """
        SELECT a.*, s.summary, s.category
        FROM articles a
        LEFT JOIN summaries s ON a.id = s.article_id
        WHERE a.id = %s
        """
        try:
            cursor.execute(query, (article_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching article with id {article_id}: {e}")
            return None
        finally:
            cursor.close()

    def save_user(self, email, password, preferences):
        cursor = self.connection.cursor()
        query = """INSERT INTO users (email, password, preferences) 
                   VALUES (%s, %s, %s)"""
        values = (email, password, preferences)
        try:
            cursor.execute(query, values)
            self.connection.commit()
            print(f"User saved: {email}")
        except Error as e:
            print(f"Error saving user: {e}")
        finally:
            cursor.close()

    def get_users_by_category(self, category):
        cursor = self.connection.cursor()
        query = "SELECT email FROM users WHERE JSON_CONTAINS(preferences, %s, '$.categories')"
        try:
            cursor.execute(query, (json.dumps(category),))
            return [user[0] for user in cursor.fetchall()]
        except Error as e:
            print(f"Error fetching users for category {category}: {e}")
            return []
        finally:
            cursor.close()

    def update_article(self, article_id, title=None, scrapy_text=None, source=None):
        cursor = self.connection.cursor()
        query = "UPDATE articles SET "
        values = []
        if title:
            query += "title = %s, "
            values.append(title)
        if scrapy_text:
            query += "scrapy_text = %s, "
            values.append(scrapy_text)
        if source:
            query += "source = %s, "
            values.append(source)
        query = query.rstrip(', ') + " WHERE id = %s"
        values.append(article_id)

        try:
            cursor.execute(query, tuple(values))
            self.connection.commit()
            print(f"Article updated: ID {article_id}")
        except Error as e:
            print(f"Error updating article: {e}")
        finally:
            cursor.close()

    def remove_subscription(self, user_id, category_name):
        cursor = self.connection.cursor()
        query = """DELETE FROM subscriptions 
                   WHERE user_id = %s AND category_id = (SELECT id FROM categories WHERE name = %s)"""
        values = (user_id, category_name)
        try:
            cursor.execute(query, values)
            self.connection.commit()
            print(f"Subscription removed for user {user_id} from category {category_name}")
        except Error as e:
            print(f"Error removing subscription: {e}")
        finally:
            cursor.close()

    def update_user_preferences(self, user_id, new_preferences):
        cursor = self.connection.cursor()
        query = "UPDATE users SET preferences = %s WHERE id = %s"
        values = (json.dumps(new_preferences), user_id)
        try:
            cursor.execute(query, values)
            self.connection.commit()
            print(f"Preferences updated for user {user_id}")
        except Error as e:
            print(f"Error updating user preferences: {e}")
        finally:
            cursor.close()

    def article_exists(self, link):
        cursor = self.connection.cursor()
        query = "SELECT id FROM articles WHERE link = %s"
        try:
            cursor.execute(query, (link,))
            result = cursor.fetchone()
            return result is not None
        except Error as e:
            print(f"Error checking if article exists: {e}")
            return False
        finally:
            cursor.close()

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

