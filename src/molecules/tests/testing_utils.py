import collections
import logging
import random

logger = logging.getLogger(__name__)

# simplest organic compounds
alkanes = collections.OrderedDict(
    {
        "methane": {"smiles": "C", "name": "Methane", "molecule_id": 100},
        "ethane": {"smiles": "CC", "name": "Ethane", "molecule_id": 101},
        "propane": {"smiles": "CCC", "name": "Propane", "molecule_id": 102},
        "butane": {"smiles": "CCCC", "name": "Butane", "molecule_id": 103},
        "pentane": {"smiles": "CCCCC", "name": "Pentane", "molecule_id": 104},
        "hexane": {"smiles": "CCCCCC", "name": "Hexane", "molecule_id": 105},
        "heptane": {"smiles": "CCCCCCC", "name": "Heptane", "molecule_id": 106},
        "octane": {"smiles": "CCCCCCCC", "name": "Octane", "molecule_id": 107},
        "nonane": {"smiles": "CCCCCCCCC", "name": "Nonane", "molecule_id": 108},
        "decane": {"smiles": "CCCCCCCCCC", "name": "Decane", "molecule_id": 109},
    }
)

alkane_request_jsons = {
    i: (lambda: {"name": f"Alkane {i}", "smiles": "C" * i})() for i in range(1, 100)
}


def validate_response_dict_for_alkane(response_dict, alkane):
    if response_dict["name"] != alkane["name"]:
        logger.error(f"{response_dict['name']} != {alkane['name']}")
        return False

    if response_dict["smiles"] != alkane["smiles"]:
        logger.error(f"{response_dict['smiles']} != {alkane['smiles']}")
        return False

    if response_dict["molecule_id"] is None:
        logger.error(f"{response_dict['molecule_id']} is None")
        return False

    if response_dict["created_at"] is None:
        logger.error(f"{response_dict['created_at']} is None")
        return False

    if response_dict["updated_at"] is None:
        logger.error(f"{response_dict['updated_at']} is None")
        return False

    expected_links = {
        "self": {
            "href": f"/molecules/{response_dict['molecule_id']}",
            "rel": "self",
            "type": "GET",
        },
        "substructures": {
            "href": f"/molecules/search/substructures?smiles={response_dict['smiles']}",
            "rel": "substructures",
            "type": "GET",
        },
        "superstructures": {
            "href": f"/molecules/search/superstructures?smiles={response_dict['smiles']}",
            "rel": "superstructures",
            "type": "GET",
        },
    }

    if response_dict["links"] != expected_links:
        # print first difference
        for key in response_dict["links"]:
            if response_dict["links"][key] != expected_links[key]:
                logger.error(f"response_dict['links'][{key}] != expected_links[{key}]")
                return False
        return False

    return True


def validate_response_dict_for_ith_alkane(response_dict, i):
    alkane = alkane_request_jsons[i]
    return validate_response_dict_for_alkane(response_dict, alkane)


heptane_isomer_requests = {
    1: {"smiles": "CCCCCCC", "name": "n-Heptane"},
    2: {"smiles": "CCCCC(C)", "name": "2-Methylhexane"},
    3: {"smiles": "CCCC(C)CC", "name": "3-Methylhexane"},
    4: {"smiles": "CCCC(CC)C", "name": "2,2-Dimethylpentane"},
    5: {"smiles": "CCC(C)(C)CC", "name": "2,3-Dimethylpentane"},
    6: {"smiles": "CC(C)C(C)CC", "name": "2,4-Dimethylpentane"},
    7: {"smiles": "CCC(CC)CC", "name": "3,3-Dimethylpentane"},
    8: {"smiles": "CC(CCC)CC", "name": "3-Ethylpentane"},
    9: {"smiles": "CC(C)(C)C(C)(C)", "name": "2,2,3-Trimethylbutane"},
}


def get_imaginary_alkane_requests(n, shuffle=False):
    """
    generates a list of alkanes with imaginary names,
    first one is named "gaozane" and the rest are named "gaozane32", "gaozane48", etc. number means the mass

    Used for testing the search endpoints
    :param n: number of alkanes to generate
    :param shuffle: whether to shuffle the list randomly
    :return: list of alkanes
    """
    imaginary_alkane_requests = [
        {"smiles": "C" * i, "name": f"gaozane{i * 16}"} for i in range(2, n + 1)
    ]
    imaginary_alkane_requests.insert(0, {"smiles": "C", "name": "gaozane"})
    if shuffle:
        random.shuffle(imaginary_alkane_requests)
    return imaginary_alkane_requests
