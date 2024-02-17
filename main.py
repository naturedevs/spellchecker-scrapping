import csv
from spellchecker import SpellChecker

spell = SpellChecker()

def spell_check(text):
    words = text.split()
    misspelled = spell.unknown(words)

    corrected_text = []
    for word in words:
        if word in misspelled:
            corrected_text.append(spell.correction(word))
        else:
            corrected_text.append(word)

    return ' '.join(corrected_text)


# Open the CSV file in read mode
with open('data.csv', mode='r') as file:
    csv_reader = csv.reader(file)

    # Iterate over each row in the CSV file
    for row in csv_reader:
        print(row)

data = [
    ['Name', 'Age', 'City'],
    ['Alice', 30, 'New York'],
    ['Bob', 25, 'San Francisco'],
    ['Charlie', 35, 'Chicago']
]

# Specify the file name
csv_file = 'data.csv'

# Open the CSV file in write mode
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)

    # Write data to the CSV file row by row
    for row in data:
        writer.writerow(row)

print(f'Data has been written to {csv_file}')

text = "Thiss is a samplee text withh somee misspellings."
corrected_text = spell_check(text)
print("Original text:", text)
print("Corrected text:", corrected_text)