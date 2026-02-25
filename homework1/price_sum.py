import csv

adult_sum = 0
senior_sum = 0
child_sum = 0

with open('products.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        adult_sum += float(row['Взрослый'])
        senior_sum += float(row['Пенсионер'])
        child_sum += float(row['Ребенок'])

print(f"{adult_sum:.2f} {senior_sum:.2f} {child_sum:.2f}")
