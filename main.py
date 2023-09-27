from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from selenium import webdriver
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

app = Flask(__name__)

# Configuração do banco de dados SQLite
DATABASE = 'database.sqlite'

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            screenshot BLOB
        )
    ''')
    conn.commit()
    conn.close()


create_table()

os.environ['WDM_SSL_VERIFY']='0'

driver = ChromeDriverManager().install()

@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM links')
    favoritos = cursor.fetchall()
    conn.close()
    return render_template('index.html', favoritos=favoritos)

@app.route('/adicionar_link', methods=['POST'])
def adicionar_link():
    url = request.form['url']
    
    # Capturar screenshot da página
    driver = ChromeDriverManager().install()
    _options = webdriver.ChromeOptions()
    _options.add_argument('headless')
    driver = webdriver.Chrome(options=_options)
    driver.get(url)
    
    # Aguarda a pagina terminar de carregar
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    screenshot = driver.get_screenshot_as_base64()
    driver.quit()
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO links (url, screenshot) VALUES (?, ?)', (url, screenshot))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))


def parse_bookmarks():
    ''' Função que vai receber arquivo bookmark.html do Google Chrome para importar em massa'''
    pass
    soup = BeautifulSoup('', "html.parser")
    bookmarks = []

    conn = sqlite3.connect(DATABASE)
    with sqlite3.connect(DATABASE) as conn:
        for link in soup.find_all("a"):
            url = link.get("href")
            title = link.string

            # Capturar screenshot da página

            driver = webdriver.Chrome(driver)
            driver.get(url)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            screenshot = driver.get_screenshot_as_base64()
            driver.quit()


            cursor = conn.cursor()
            cursor.execute('INSERT INTO links (url, screenshot) VALUES (?, ?)', (url, screenshot))
            conn.commit()
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
