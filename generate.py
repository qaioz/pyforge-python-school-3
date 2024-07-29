import csv


# function to generate csv file for testing later
# smiles,name,description
# below method generates a file with the following content:

# smiles,name,description
# CC(=O)Oc1ccccc1C(=O)O,"Asp,irin","Aspi,rin is in a group of medications called salicylates..."
# C,Carbon,Base of all life on Earth,Something
# C
#
# julia dream,dreamboat queen,queen of all my dreams
# ,when i,come home

# out of the 6 lines above, first one is the header, second and third are valid lines, fourth and fifth are invalid
def generate_csv():
    with open('./molecules.csv', mode='w') as file:
        writer = csv.writer(file)

        writer.writerow(['smiles', 'name', 'description'])

        # notice the line below, it has a commas in name and description but it is still valid because it is enclosed
        # in quotes thanks to the csv module
        writer.writerow(['CC(=O)Oc1ccccc1C(=O)O', 'Asp,irin', 'Aspi,rin is in a group of medications called '
                                                              'salicylates...'])

        # line below is invalid because it has an extra column
        writer.writerow(['C', 'Carbon', 'Base of all life on Earth', 'Something'])

        # line below is also valid because it does not have name and description, but they are optional
        writer.writerow(['C'])

        # line below is invalid because it has an invalid smiles string
        writer.writerow(['julia dream', 'dreamboat quuen', 'queen of all my dreams'])

        # empty line
        writer.writerow([])

        # another invalid line because it has a missing smiles string
        writer.writerow(['', 'when i', 'come home'])


generate_csv()
