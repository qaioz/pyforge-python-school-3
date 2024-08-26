from rdkit import Chem


def fund_substructures(mol, mols):
    """
    I will rely on duck typing here,
    parameters can be  anything that has a SMILES attribute.
    """

    return [
        m
        for m in mols
        if Chem.MolFromSmiles(mol.smiles).HasSubstructMatch(
            Chem.MolFromSmiles(m.smiles)
        )
    ]
