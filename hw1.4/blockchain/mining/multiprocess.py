import multiprocessing
from .singleprocess import proof_of_work


def patch_generator(compl: str, previous_proof: int, patch_length: int):
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


def proof_of_work_wrapper(pars: tuple):
    return proof_of_work(*pars)


def mp_mining_proof(previous_proof: int, compl: str):
    """finding proof and adding it to the created block"""
    with multiprocessing.Pool() as pool:
        patch_length = 10 ** len(compl)
        for patch in patch_generator(compl, previous_proof, patch_length):
            for result in pool.imap_unordered(proof_of_work_wrapper, patch):
                if result:
                    return result
