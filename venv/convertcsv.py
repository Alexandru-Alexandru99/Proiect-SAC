import csv
import json
 
 
# Function to convert a CSV to JSON
# Takes the file paths as arguments
def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []
      
    #read csv file
    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            row.pop("id")
            row["movie_id"] = row.pop("")
            row["title"] = row.pop("tittle")
            row.pop("cast")
            row.pop("crew")
            row.pop("spoken_languages")
            jsonArray.append(row)
  
    #convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf: 
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)
         
# Driver Code
 
# Decide the two file paths according to your
# computer system
csv_file =  "./dataset/merged_movies.csv"
json_file =  "./dataset/movie_metadata.json"
 
# Call the make_json function
csv_to_json(csv_file, json_file)