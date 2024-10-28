from pathlib import Path
import time
from triggers import setParallelData
import random
import select
import sys
from tqdm import tqdm

def flush_input():
    # This function clears out any existing input in the buffer
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        sys.stdin.read(1)


def setup_experiment(ISIs:list[float], n_sequences:int, n_blocks:int, n_no_stim_blocks:int, omission_positions:list[int], trigger_mapping:dict):
    """
    Sets up an experiment structure with both stimulation and non-stimulation blocks.

    Parameters:
        ISIs (list of float): List of inter-stimulus intervals for each condition.
        n_sequences (int): Number of sequences in each block.
        n_blocks (int): Number of stimulation blocks per ISI per nerve.
        n_no_stim_blocks (int): Number of non-stimulation blocks per ISI.
        omission_positions (list of int): Possible positions for omissions within sequences.
        trigger_mapping (dict): Mapping of triggers for different types of events.

    Returns:
        list of dict: List of blocks with ISI, nerve type, and sequence of events.
    """ 

    blocks = []

    # Generate stimulation blocks for each nerve type and ISI
    for stim in ["tibial", "median"]:
        for ISI in ISIs:
            for _ in range(n_blocks):
                block_structure = {"ISI": ISI, "nerve":stim, "events": []}
                
                for _ in range(n_sequences):
                    omission_idx = random.choice(omission_positions) # sample a random omission position
                    n_stimulations = omission_idx-1 # number of stimulations before the omissions

                    # Add stimulations followed by an omission
                    block_structure["events"].extend([trigger_mapping[f"stim_{stim}"]]*n_stimulations)
                    block_structure["events"].append(trigger_mapping[f"omis_{stim}"])

                blocks.append(block_structure)
    
    mean_omissions = int(sum(omission_positions)/len(omission_positions))
    for ISI in ISIs:
        block_structure = {"ISI": ISI, "nerve":"None", "events": []}
        for _ in range(n_no_stim_blocks):
            for _ in range(n_sequences):
                block_structure["events"].extend([trigger_mapping["non_stim"]] * mean_omissions)
            
        blocks.append(block_structure)

    random.shuffle(blocks)
    
    return blocks


def check_in_on_participant():
    flush_input()
    input("Check in on the participant. Press Enter to continue the experiment...")
    time.sleep(1)  # Delay to avoid accidental double input

def begin_rest():
    flush_input()
    input("Ready to collect resting state data. Make sure audiobook is turned off. Press Enter to begin resting state...")
    time.sleep(1)  # Delay to avoid accidental double input

def end_rest():
    flush_input()
    input("Finished collecting resting state data. Turn audiobook on and let particpant know experiment is about to start. Press enter to continue (or end experiment if this is the last resting state)...")
    time.sleep(1)  # Delay to avoid accidental double input
    pass

def get_resting_state(rest_duration, trigger_start:int, trigger_end:int):

    begin_rest()
    setParallelData(trigger_start)
    time.sleep(rest_duration)
    setParallelData(trigger_end)

    end_rest()


def run_experiment(blocks, logfile, trigger_mapping:dict, blocks_between_breaks:int, rest_duration):

    # Open the log file for writing
    with open(logfile, 'w') as log_file: # NOTE REMEMBER TO SAVE IF EXPERIMENT IS STOPPED!!!!
        log_file.write("timestamp, block, ISI, nerve, trigger\n")  # Header

        experiment_start = time.perf_counter()  # Reference start time for timestamps

        
        get_resting_state(rest_duration=rest_duration, trigger_start=trigger_mapping["rest_start"], trigger_end=trigger_mapping["rest_end"])

        for idx, block in enumerate(blocks):
            ISI = block["ISI"]


            # check if it is time for a break
            if (idx + 1) % blocks_between_breaks == 0:
                time.sleep(0.5)  # Brief pause to ensure any accidental input clears
                check_in_on_participant()
            
            # loop over events in the block
            for event in tqdm(block["events"], desc=f"block {idx+1} out of {len(blocks)}"):
                setParallelData(event)
                timestamp = time.perf_counter() - experiment_start
                
                # record event timestamp and details
                log_file.write(f"{timestamp}, {idx + 1}, {ISI}, {block['nerve']}, {event}\n") # this seems to delay it so ISI is not correct
                
                # Wait for the specified ISI duration
                target_time = timestamp + block["ISI"] + experiment_start
                while time.perf_counter() < target_time:
                    pass  # Busy-waiting until the exact ISI time

    get_resting_state(rest_duration=rest_duration, trigger_start=trigger_mapping["rest_start"], trigger_end=trigger_mapping["rest_end"])


    print("Experiment done! Go fetch the participant")


if __name__ in "__main__":
    
    output_path = Path(__file__).parent / "output" 
    if not output_path.exists():
        output_path.mkdir(parents=True)
    
    participant = "001"

    ISI = [1, 0.05, 0.1]#[0.5, 1, 1.5] # in seconds
    n_sequences = 5 # the number of sequences in each block
    n_blocks = 2 # the number of blocks per ISI (per stimulation type)
    n_non_stim_blocks = 1 # the number of blocks per ISI (per stimulation type)
    omission_positions = [4, 5, 6]
    blocks_between_breaks = 3
    rest_duration = 1 # in seconds

    trigger_mapping = {
        "stim_tibial":1,
        "omis_tibial": 10,
        "stim_median": 2,
        "omis_median": 20,
        "non_stim": 30,
        "rest_start":100,
        "rest_end":110
    }

    blocks = setup_experiment(
        ISIs=ISI, 
        n_sequences=n_sequences, 
        n_blocks=n_blocks, 
        n_no_stim_blocks=n_non_stim_blocks,
        omission_positions=omission_positions, 
        trigger_mapping=trigger_mapping
        )
    

    run_experiment(
        blocks, 
        logfile= output_path / f"experimental_{participant}.csv", 
        trigger_mapping=trigger_mapping, 
        blocks_between_breaks=blocks_between_breaks,
        rest_duration=rest_duration
        )
