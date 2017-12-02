import json
import csv


f = open('Azurelogs.json')
data = json.load(f)
t_data = data['value']
f.close()

new_file = open('Azurelogs.csv', 'w')
csvwriter = csv.writer(new_file)
count = 0

for i in t_data:
      if count == 0:
             header = i.keys()
             csvwriter.writerow(header)
             count += 1
      csvwriter.writerow(i.values())
new_file.close()
