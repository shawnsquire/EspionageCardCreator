import math

__author__ = 'Shawn Squire'
import csv
from itertools import repeat
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
    'Utility': (100, 255, 255),
    'Hidden': (120, 120, 120)
}

SPRITE_COLS = 10
SPRITE_ROWS = 7

OUTPUT_FODLER = 'output'
CARDS_LIST = 'cards.csv'
IMGUR_FILE = 'imgur_key.txt'

def chunks(l, n):
    """ Yield successive n-sized chunks from l
    """
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

class Sprite:
    def __init__(self, image, count=0):
        self.image = image
        self.count = count

class Card:
    def __init__(self, code, name='', type='', description='', count=1):
        self.code = code
        self.name = name
        self.type = type
        self.description = description
        self.count = int(count)
        self.image = None

def displayCard(c):
    if len(c.type) > 0:
        print("Type: %s" % c.type)
    if len(c.name) > 0:
        print("Name: %s" % c.name)
    if len(c.description) > 0:
        print("Description: %s" % c.description)
    print()


def createCard(c):
    file = open("%s/%s.jpg" % (OUTPUT_FODLER, c.code), 'w+')
    img = Image.new('RGB', CARD_SIZE, (255,255,255))
    d = ImageDraw.Draw(img)

    # Draw header
    d.rectangle(((0,0), (CARD_SIZE[0], CARD_HEADER_HEIGHT)),
            fill=CARD_COLORS[c.type])
    d.text((CARD_MARGIN, CARD_MARGIN), c.type, font=CARD_FONTS['type'],
            fill=(0,0,0))
    bbox = CARD_FONTS['name'].getbbox(c.name)
    title_height = bbox[3] - bbox[1]
    d.text((CARD_MARGIN, CARD_HEADER_HEIGHT - title_height - CARD_MARGIN),
           c.name, font=CARD_FONTS['name'], fill=(0,0,0))

    lines = textwrap.wrap(c.description, width = 23) # 23 arbitrarily derived
    y_text = CARD_HEADER_HEIGHT + CARD_MARGIN
    for line in lines:
        bbox = CARD_FONTS['description'].getbbox(line)
        width, height = (bbox[2] - bbox[0], bbox[3] - bbox[1])
        d.text((CARD_MARGIN, y_text), line, font = CARD_FONTS['description'],
                fill=(0,0,0))
        y_text += 30 # Predetermined given size of text
    bbox = CARD_FONTS['code'].getbbox(c.code)
    code_width = bbox[2] - bbox[0]
    d.text((CARD_SIZE[0] - CARD_MARGIN - code_width, 330),
           c.code, font=CARD_FONTS['code'], fill=(0,0,0))

    c.image = img
    img.save(file, "JPEG", quality=95)
    return c

def createHiddenCard():
    img = Image.new('RGB', CARD_SIZE, (255,255,255))
    d = ImageDraw.Draw(img)
    d.rectangle(((0,0), (CARD_SIZE[0], CARD_HEADER_HEIGHT)),
            fill=CARD_COLORS["Hidden"])
    d.text((CARD_MARGIN, CARD_MARGIN), 'Hidden', font=CARD_FONTS['type'],
            fill=(0,0,0))
    bbox = CARD_FONTS['name'].getbbox('Hidden')
    title_height = bbox[3] - bbox[1]
    d.text((CARD_MARGIN, CARD_HEADER_HEIGHT - title_height - CARD_MARGIN),
           'Hidden Card', font=CARD_FONTS['name'], fill=(0,0,0))
    d.text((CARD_MARGIN, CARD_HEADER_HEIGHT + CARD_MARGIN),
            "This card is hidden", font = CARD_FONTS['description'],
            fill=(0,0,0))
    return img

def combine_images(cards):
    cards = [c for card in cards for c in repeat(card, card.count)]
    max_cards = SPRITE_ROWS * SPRITE_COLS - 1
    sprites = []
    if(len(cards) > max_cards):
        deck_count = math.ceil(len(cards) / max_cards)
        print("Found %d cards. Splitting into %d decks" % (len(cards), deck_count))

    for i,deck in enumerate(list(chunks(cards, max_cards))):
        sprite = Sprite("%s/sprite-%d.jpg" % (OUTPUT_FODLER, i), len(deck))
        file = open(sprite.image, 'w+')
        img = Image.new('RGB', (CARD_SIZE[0] * SPRITE_COLS,
                        CARD_SIZE[1] * SPRITE_ROWS), (0,0,0))
        x = y = 0
        for card in deck:
            img.paste(card.image, (x, y))
            if x + CARD_SIZE[0] >= CARD_SIZE[0] * SPRITE_COLS:
                x = 0
                y = y + CARD_SIZE[1]
            else:
                x = x + CARD_SIZE[0]

        img.paste(createHiddenCard(),
                (CARD_SIZE[0] * (SPRITE_COLS - 1), CARD_SIZE[1] * (SPRITE_ROWS - 1)))
        img.save(file, "JPEG", quality=95)
        sprites.append(sprite)
    return sprites

def upload(file):
    try:
        with open(IMGUR_FILE, 'r') as imgur_key:
            id,secret = next(imgur_key).split(':')
            client = ImgurClient(id, secret)
            return client.upload_from_path(file)
    except FileNotFoundError:
        print("ERROR: Missing %s" % IMGUR_FILE)
        print("Make sure this file is present and contains the Imgur key.")
        print("Proper syntax is one line with \"CLIENT_ID:CLIENT_SYNTAX\"")
        return None

def main():
    with open(CARDS_LIST, 'r') as cardscsv:
        cardlist = csv.reader(cardscsv, delimiter=',', quotechar='"')
        next(cardlist) # Skip header row
        cards = [createCard(Card(c[4], name=c[1], type=c[0],
                        description=c[2], count=c[3] if int(c[3]) > 0 else 1))
                for c in cardlist]
        sprites = combine_images(cards)
        print("Finished processing %d unique cards across %d decks" % (len(cards), len(sprites)))
        for i,sprite in enumerate(sprites):
            imgur = upload(sprite.image)
            if imgur != None:
                print("Uploaded deck %d with %d cards: %s" % (i+1, sprite.count, imgur['link']))


if __name__ == '__main__':
    main()
