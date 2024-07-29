# Homework 4

## Introduction to RDKit

RDKit is an open-source cheminformatics software library that provides a wide range of tools for working with chemical
informatics, particularly focusing on molecule representation, manipulation, and visualization. It is widely used in
both academia and industry for tasks such as molecular modeling, chemical database searching, and molecular property
prediction. One of RDKit's key strengths is its ability to seamlessly integrate with Python, making it accessible and
flexible for a variety of applications.

In this introduction, we will explore the basic functionalities of RDKit, focusing on how to represent, manipulate, and
visualize chemical structures using Python. We will cover the following topics:

1. **Installation of RDKit**
2. **Basic molecular representations**
3. **Substructure search**
4. **Molecular visualization**

### 1. Installation of RDKit

To install [RDKit](https://www.rdkit.org/docs/Install.html), you can use the following commands in your terminal. It's
recommended to use a [conda](https://docs.anaconda.com/miniconda/) environment to manage dependencies easily:

```sh
conda create -c conda-forge -n my-rdkit-env rdkit=2024.03.4 python=3.12
conda activate my-rdkit-env
```

### 2. Basic Molecular Representations

RDKit allows you to create and manipulate molecular structures easily. Here's how you can create a molecule from a
SMILES string and visualize it:

```python
from rdkit import Chem
from rdkit.Chem import Draw

# Create a molecule from a SMILES string
smiles = "CCO"  # Ethanol
molecule = Chem.MolFromSmiles(smiles)

# Draw the molecule
Draw.MolToImage(molecule)
```

### 3. Substructure Search

RDKit can be used to perform substructure searches, identifying specific functional groups or substructures within a
molecule.

```python
from rdkit import Chem

# Define the molecule and the substructure to search for
benzene = Chem.MolFromSmiles("c1ccccc1")
ethanol = Chem.MolFromSmiles("CCO")

# Perform the substructure search
match = ethanol.HasSubstructMatch(benzene)
print("Benzene ring found in ethanol:", match)
```

### 4. Molecular Visualization

RDKit provides several options for visualizing molecules. You can visualize individual molecules or draw multiple
molecules in a grid.

```python
from rdkit.Chem import Draw

# Create a list of molecules
smiles_list = ["CCO", "c1ccccc1", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"]
molecules = [Chem.MolFromSmiles(smiles) for smiles in smiles_list]

# Draw the molecules in a grid
img = Draw.MolsToGridImage(molecules, molsPerRow=2, subImgSize=(200, 200), returnPNG=False)
img.show()
```

## Substructure search

Now you have everything to implement the substructure search function:

<img title="a title" alt="Alt text" src="../../images/1.png">

Implement a function in file `/src/main.py` that takes two arguments:

1. List of molecules as SMILES strings
2. Substructure as SMILES string
   Function should return a list of all molecules from argument 1 that contain substructure from argument 2

```python
substructure_search(["CCO", "c1ccccc1", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O"], "c1ccccc1")
["c1ccccc1", "CC(=O)Oc1ccccc1C(=O)O"]
```
