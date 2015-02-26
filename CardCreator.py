import math

__author__ = 'Shawn Squire'
import csv
from PIL import Image, ImageDraw, ImageFont
from imgurpython import ImgurClient
import textwrap

CARD_SIZE = (250, 350)
CARD_MARGIN = 10
CARD_HEADER_HEIGHT = 90

CARD_FONTS = {
    'name' : ImageFont.truetype("arial.ttf", 30),
    'type' : ImageFont.truetype("arial.ttf", 16),
    'description' : ImageFont.truetype("arial.ttf", 21),
    'code' : ImageFont.truetype("arial.ttf", 10)
}

CARD_COLORS = {
    'Agent' : (100, 100, 255),
    'Building' : (100, 255, 100),
    'Espionage' : (255, 255, 100),
    'Sabotage': (255, 100, 100),
    'Utility': (100, 255, 255)
}

OUTPUT_FODLER = 'output'
CARDS_LIST = 'cards.csv'
IMGUR_FILE = 'imgur_key.txt'

class Card:
    def __init__(self, code, name='', type='', description='', count=1):
        self.code = code
        self.name = name
        self.type = type
        self.description = description
        self.count = int(count)

def createCard(c):
    if len(c.type) > 0:
        print("Type: %s" % c.type)
    if len(c.name) > 0:
        print("Name: %s" % c.name)
    if len(c.description) > 0:
        print("Description: %s" % c.description)
    print()

    file = open("%s/%s.jpg" % (OUTPUT_FODLER, c.code), 'w+')
    img = Image.new('RGB', CARD_SIZE, (255,255,255))
    d = ImageDraw.Draw(img)

    # Draw header
    d.rectangle(((0,0), (CARD_SIZE[0], CARD_HEADER_HEIGHT)), fill=CARD_COLORS[c.type])
    d.text((CARD_MARGIN, CARD_MARGIN), c.type, font=CARD_FONTS['type'], fill=(0,0,0))
    d.text((CARD_MARGIN, CARD_HEADER_HEIGHT - CARD_FONTS['name'].getsize(c.name)[1] - CARD_MARGIN),
           c.name, font=CARD_FONTS['name'], fill=(0,0,0))

    lines = textwrap.wrap(c.description, width = 23) # Width arbitrarily derived
    y_text = CARD_HEADER_HEIGHT + CARD_MARGIN
    for line in lines:
        width, height = CARD_FONTS['description'].getsize(line)
        d.text((CARD_MARGIN, y_text), line, font = CARD_FONTS['description'], fill=(0,0,0))
        y_text += 30 # Predetermined given size of text
    d.text((CARD_SIZE[0] - CARD_MARGIN - CARD_FONTS['code'].getsize(c.code)[0], 330),
           c.code, font=CARD_FONTS['code'], fill=(0,0,0))

    img.save(file, "JPEG", quality=95)
    return img

def combine_images(cards):
    file_name = "%s/sprite.jpg" % (OUTPUT_FODLER)
    file = open(file_name, 'w+')
    img = Image.new('RGB', (CARD_SIZE[0] * 10, CARD_SIZE[1] * 7), (0,0,0))
    x = y = 0
    for c in cards:
        img.paste(c, (x, y))
        if x + CARD_SIZE[0] >= CARD_SIZE[0] * 10:
            x = 0
            y = y + CARD_SIZE[1]
        else:
            x = x + CARD_SIZE[0]
    img.save(file, "JPEG", quality=95)
    return file_name

def upload(file):
    with open(IMGUR_FILE, 'r') as imgur_key:
        id,secret = next(imgur_key).split(':')
        client = ImgurClient(id, secret)
        return client.upload_from_path(file)

def main():
    with open(CARDS_LIST, 'r') as cardscsv:
        cardlist = csv.reader(cardscsv, delimiter=',', quotechar='"')
        next(cardlist) # Skip header row
        cards = [createCard(Card(c[4], name=c[1], type=c[0], description=c[2], count=c[3] if len(c[3]) > 0 else 1)) for c in cardlist]
        imgur = upload(combine_images(cards))
        print("Uploaded %d cards to Imgur: %s" % (len(cards), imgur['link']))

if __name__ == '__main__':
    main()