from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# URL du site à scraper
url = 'https://tracker.gg/valorant/guides/clips'

# Initialiser le navigateur Selenium
driver = webdriver.Chrome()  # ou tout autre navigateur que vous avez installé

# Accéder à l'URL
driver.get(url)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialiser le navigateur Selenium
driver = webdriver.Chrome()  # ou tout autre navigateur que vous avez installé

# Accéder à l'URL
driver.get('https://tracker.gg/valorant/guides/clips')

try:
    # Attendre que le bouton "Accepter les cookies" soit cliquable
    accept_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
    
    # Cliquer sur le bouton "Accepter les cookies"
    accept_button.click()

    close_ad = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'closeIconHit')))
    close_ad.click()

    close_1stAd = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'trn-button trn-button--circle close-button')))
    close_1stAd.click()



    # Maintenant que les cookies sont acceptés, vous pouvez continuer avec votre processus d'automatisation

    # Par exemple, attendez que l'élément suivant soit présent et cliquez dessus
    # element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'element_id')))
    # element.click()

except Exception as e:
    # Afficher un message d'erreur en cas de problème
    print("Une erreur s'est produite :", e)

# Attendre que la page soit entièrement chargée
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'guide-tile')))

# Trouver tous les éléments avec la classe 'guide-tile'
guide_tiles = driver.find_elements(By.CLASS_NAME, 'guide-tile')


# Boucle à travers tous les "tiles"
for tile in guide_tiles:
    # Cliquez sur la miniature de la vidéo pour charger la vidéo en utilisant JavaScript
    video_thumbnail = WebDriverWait(tile, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.guide-tile__preview .guide-tile__video img')))
    driver.execute_script("arguments[0].click();", video_thumbnail)


    # Attendre que la vidéo soit chargée
    WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME, 'video-stream')))

    pageSource = driver.page_source
    print(pageSource)

    # Récupérer l'URL de la vidéo
    video_url = driver.find_element(By.TAG_NAME, 'video-stream').get_attribute('src')

    # Extraire les autres informations du "tile" avec BeautifulSoup si nécessaire
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    title = soup.find('p', class_='guide-tile__title').text.strip()
    author = soup.find('span', class_='guide-tile__author').text.strip()[3:]
    views = soup.find('span', class_='views').text.strip()
    timestamp = soup.find('span', class_='guide-tile__timestamp').text.strip()
    upvotes = soup.find(class_='score__total').text.strip()
    tags = [tag.text.strip() for tag in soup.find_all('span', class_='badge badge--primary')]

    # Afficher les informations
    print("Title:", title)
    print("Author:", author)
    print("Views:", views)
    print("Timestamp:", timestamp)
    print("Upvotes:", upvotes)
    print("Tags:", tags)
    print("Video URL:", video_url)
    print("\n")  # Ajouter une ligne vide pour séparer les informations de chaque "tile"

# Fermer le navigateur
driver.quit()
