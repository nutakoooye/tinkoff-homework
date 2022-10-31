import multiprocessing
from typing import Optional

from .utils import get_sha256


def proof_of_work(params: tuple) -> Optional[int]:
    """search for proof in a certain range"""
    compl, previous_proof, start_proof, stop_proof = params

    new_proof = start_proof
    check_proof = False
    while check_proof is False and new_proof <= stop_proof:
        hash_operation = get_sha256(new_proof, previous_proof)
        if hash_operation[: len(compl)] == compl:
            check_proof = True
        else:
            new_proof += 1
    return new_proof if check_proof else None


def range_gen(compl: str, previous_proof: int, patch_length: int):
    """
    generating ranges to find proof

    :param previous_proof:
    :param patch_length:length of the return range to search for evidence
    :return: range broken down by the number of cores in the system
    """
    start = 0
    end = patch_length
    step = (end - start) // multiprocessing.cpu_count()

    while True:
        iterable = []
        for start_range in range(start, end, step):
            end_range = start_range + step
            iterable.append((compl, previous_proof, start_range, end_range))
        yield iterable
        start = end
        end += patch_length


# old
def mining_proof(previous_proof: int, compl: str):
    """finding proof and adding it to the created block"""
    with multiprocessing.Pool() as pool:
        patch_length = 10 ** len(compl)
        iterable = range_gen(compl, previous_proof, patch_length)
        for pars in iterable:
            for result in pool.imap_unordered(proof_of_work, pars):
                if result:
                    return result
