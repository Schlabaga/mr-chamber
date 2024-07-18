from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
from imgEdit import crop_image, supperpose_image
import os
import shortuuid
from config import dbValorant

# dbValorant.crosshairs.delete_many({"type":"top"})

def parse_crosshairs(type):
    
    # Chemin vers le chromedriver téléchargé
    chrome_driver_path = "D:/DOCUMENTS DISQUE D/chromedriver-win64/chromedriver.exe"  # Remplacez par le chemin correct

    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Assurez-vous que l'interface graphique est désactivée
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_extension("extension/ublockOrigin.crx")
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.clipboard": 1,  # 1 pour autoriser, 2 pour bloquer
    })

    # Définir le service pour le driver Chrome
    webdriver_service = Service(chrome_driver_path)

    # Choisir le navigateur Chrome
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    if type == "top":
        type = ""

    # Étape 1 : Ouvrir la page web
    url = f"https://www.vcrdb.net/{type}"
    driver.get(url)
    
    
    if type == "":
        type = "top"
        
        

    driver.maximize_window()

    time.sleep(5)

    driver.refresh()

    time.sleep(5)

    # Étape 2 : Trouver le conteneur principal pour les crosshairs
    try:
        x_hairs_div = driver.find_element(By.ID, 'x-hairs')
    except Exception as e:
        print(f"Erreur lors de la récupération du conteneur principal: {e}")
        driver.quit()
        exit(1)

    # Étape 3 : Extraire les données de chaque crosshair
    crosshairs = []

    x_hair_containers = x_hairs_div.find_elements(By.CLASS_NAME, 'x-hair-container')

    for x_hair_container in x_hair_containers:
        
        fade = False
        
        x_hair_container.click()  # Cliquer sur chaque x-hair container
        
        time.sleep(0.01)  # Attendre que la page se charge
        
            # Créer le dossier pour le crosshair s'il n'existe pas déjà
            
        random_id = shortuuid.ShortUUID().random(length=7)
        crosshair_folder = f"crosshairs/{type}/{random_id}"
        
        details = driver.find_element(By.ID, 'details')
        if not os.path.exists(crosshair_folder):
            os.makedirs(crosshair_folder)
            
        try:
            # Vérifier si l'élément existe
            
            hofDiv = details.find_element(By.ID, "detailsImageHOF")
            
            if hofDiv.get_attribute("class") == "hof-hidden":
                print("Ce crosshair n'est pas un fade.")
                pass
            
            else:
                fade_canvas = hofDiv.find_element(By.TAG_NAME, 'x-hair').find_element(By.TAG_NAME, 'canvas')
                fade_image_data_url = driver.execute_script("return arguments[0].toDataURL('image/png');", fade_canvas)

                # Convertir le contenu du canvas en image PNG
                fade_image_data = fade_image_data_url.split(',')[1]  # Supprimer le préfixe "data:image/png;base64,"
                fade_image_bytes = base64.b64decode(fade_image_data)


                # Chemin complet du fichier image fade
                fade_image_file_path = f"{crosshair_folder}/fade.png"
                

                with open(fade_image_file_path, "wb") as fade_image_file:
                    fade_image_file.write(fade_image_bytes)

                # Supperpose fade image with background images
                background_path = f"backgrounds/png/default.png"
                
                supperpose_image(crop_image(fade_image_file_path, random_id), background_path, "")

                print("Ce crosshair est un fade.")
                
                fade = True
        
            
        except Exception as e:
            
            print(str(e))
            
            
            
        try:
            # Récupérer le nom du crosshair
            crosshair_name = x_hair_container.find_element(By.TAG_NAME, 'h2').text
            
            # Récupérer le contenu du canvas
            x_hair_canvas = x_hair_container.find_element(By.TAG_NAME, 'x-hair').find_element(By.TAG_NAME, 'canvas')
            image_data_url = driver.execute_script("return arguments[0].toDataURL('image/png');", x_hair_canvas)

            # Convertir le contenu du canvas en image PNG
            image_data = image_data_url.split(',')[1]  # Supprimer le préfixe "data:image/png;base64,"
            image_bytes = base64.b64decode(image_data)

            # Chemin complet du fichier image
            image_file_path = f"{crosshair_folder}/blank.png"

    
            with open(image_file_path, "wb") as image_file:
                image_file.write(image_bytes)

            for dessous in ["blaugelb","blue","default","grass","green","metall","orange","sky","yellow"]:
                background_path = f"backgrounds/png/{dessous}.png"
                supperpose_image(crop_image(image_file_path, dessous, crosshair_folder),background_path, "")


            # Cliquer sur le bouton "detailsCopy"
            details_button = WebDriverWait(driver, 0.01).until(
                EC.element_to_be_clickable((By.ID, 'detailsCopy'))
            )
            details_button.click()
            
            time.sleep(0.2)  # Attendre que le contenu soit copié dans le presse-papier
            
            # Coller le contenu du presse-papier dans la console
            clipboard_content = driver.execute_script("return navigator.clipboard.readText();")
            
            dbValorant.crosshairs.update_one({"name":crosshair_name}, {"$set": {"id":random_id,
                                                                                "name":crosshair_name,
                                                                                "code": clipboard_content,
                                                                                "type":type,
                                                                                "path":crosshair_folder,
                                                                                "fade":fade}}, upsert=True)
            
            # print(clipboard_content)
            # print('---')
            # print(crosshair_name)
            # print('---')
            # print(image_data_url)
            # print('---\n')
                    
            # Cliquer sur le bouton "detailsClose"
            details_close_button = WebDriverWait(driver, 0.2).until(
                EC.element_to_be_clickable((By.ID, 'detailsClose'))
            )
            details_close_button.click()
            time.sleep(0.01)  # Attendre que la page se recharge
            
        except Exception as e:
            print(f"Erreur lors de l'extraction des données du crosshair: {e}")
            driver.quit()
            exit(1)

    # Fermer le navigateur
    
    print("---------------------------------------------")
    print("Extraction des données terminée avec succès.")
    print("---------------------------------------------")
    
    driver.quit()


parse_crosshairs("top")