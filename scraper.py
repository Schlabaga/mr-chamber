from bs4 import BeautifulSoup
import requests

url = 'https://tracker.gg/valorant/guides/clips?objective=all&agent=all'



page = requests.get(url)
html_content = page.text
soup = BeautifulSoup(html_content, 'html')
guide_tiles = soup.find_all(class_='guide-tile')
print(guide_tiles)

for tile in guide_tiles:

    video_img = tile.find('div', class_='video-stream h-full w-full').find('iframe')['src']
    tags = [tag.text.strip() for tag in tile.find_all('span', class_='badge badge--primary')]
    title = tile.find('p', class_='guide-tile__title').text.strip()
    author = tile.find('span', class_='guide-tile__author').text.strip()[3:]
    views = tile.find('span', class_='views').text.strip()
    timestamp = tile.find('span', class_='guide-tile__timestamp').text.strip()
    upvotes = tile.find(class_='score__total').text.strip()


    # Afficher les informations*
    print("Agent:", tags[0])
    print("Map:", tags[1])
    print("Side:", tags[2])
    print("Title:", title)
    print("Author:", author)
    print("Views:", views)
    print("Timestamp:", timestamp)
    print("Upvotes:", upvotes)
    print("Video:", video_img)
    
    print("\n")

liste = "class=guides__list"
lineups = 'class="guide-tile"'