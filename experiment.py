from pathlib import Path
import time
import random
import sys
import select
from tqdm import tqdm
from triggers import setParallelData

class Experiment:
    def __init__(self, ISIs, n_sequences, n_blocks, n_no_stim_blocks, omission_positions, 
                 blocks_between_breaks, rest_duration, trigger_mapping, output_path, participant_id):
        self.ISIs = ISIs
        self.n_sequences = n_sequences
        self.n_blocks = n_blocks
        self.n_no_stim_blocks = n_no_stim_blocks
        self.omission_positions = omission_positions
        self.blocks_between_breaks = blocks_between_breaks
        self.rest_duration = rest_duration
        self.trigger_mapping = trigger_mapping
        self.participant_id = participant_id
        self.output_path = Path(output_path)
        self.blocks = self.setup_experiment()
        
        # Ensure the output directory exists
        if not self.output_path.exists():
            self.output_path.mkdir(parents=True)
        self.logfile = self.output_path / f"experimental_{participant_id}.csv"

    @staticmethod
    def flush_input():
        """Clears out any existing input in the buffer."""
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            sys.stdin.read(1)

    def setup_experiment(self):
        """Sets up an experiment structure with both stimulation and non-stimulation blocks."""
        blocks = []

        # Generate stimulation blocks for each nerve type and ISI
        for stim in ["tibial", "median"]:
            for ISI in self.ISIs:
                for _ in range(self.n_blocks):
                    block_structure = {"ISI": ISI, "nerve": stim, "events": []}
                    for _ in range(self.n_sequences):
                        omission_idx = random.choice(self.omission_positions)
                        n_stimulations = omission_idx - 1

                        # Add stimulations followed by an omission
                        block_structure["events"].extend([self.trigger_mapping[f"stim_{stim}"]] * n_stimulations)
                        block_structure["events"].append(self.trigger_mapping[f"omis_{stim}"])

                    blocks.append(block_structure)

        # Non-stimulation blocks
        mean_omissions = int(sum(self.omission_positions) / len(self.omission_positions))
        for ISI in self.ISIs:
            block_structure = {"ISI": ISI, "nerve": "None", "events": []}
            for _ in range(self.n_no_stim_blocks):
                for _ in range(self.n_sequences):
                    block_structure["events"].extend([self.trigger_mapping["non_stim"]] * mean_omissions)
            blocks.append(block_structure)

        random.shuffle(blocks)
        return blocks

    def get_resting_state(self):
        """Handles the resting state data collection process."""
        self._begin_rest()
        setParallelData(self.trigger_mapping["rest_start"])
        time.sleep(self.rest_duration)
        setParallelData(self.trigger_mapping["rest_end"])
        self._end_rest()

    def _begin_rest(self):
        self.flush_input()
        input("Ready to collect resting state data. Press Enter to begin...")
        time.sleep(1)

    def _end_rest(self):
        self.flush_input()
        input("Finished collecting resting state data. Press Enter to continue...")
        time.sleep(1)

    def calculate_duration(self):
        """Estimates the total duration of the experiment in seconds."""
        total_duration = self.rest_duration * 2
        mean_omissions = int(sum(self.omission_positions) / len(self.omission_positions))

        for ISI in self.ISIs:
            for _ in range(self.n_blocks):
                block_duration = (self.n_sequences * (ISI * mean_omissions))
                total_duration += block_duration * 2

        for ISI in self.ISIs:
            for _ in range(self.n_no_stim_blocks):
                non_stim_duration = self.n_sequences * (ISI * mean_omissions)
                total_duration += non_stim_duration

        n_breaks = len(self.ISIs) * (self.n_blocks * 2 + self.n_no_stim_blocks) // self.blocks_between_breaks
        break_duration = 2
        total_duration += n_breaks * break_duration

        return total_duration

    def run(self):
        """Executes the experiment, managing breaks, resting states, and logging."""
        with open(self.logfile, 'w') as log_file:
            log_file.write("timestamp, block, ISI, nerve, trigger\n")

            experiment_start = time.perf_counter()
            self.get_resting_state()

            for idx, block in enumerate(self.blocks):
                ISI = block["ISI"]

                if (idx + 1) % self.blocks_between_breaks == 0:
                    time.sleep(0.5)
                    self._check_in_on_participant()

                for event in tqdm(block["events"], desc=f"block {idx + 1} out of {len(self.blocks)}"):
                    setParallelData(event)
                    timestamp = time.perf_counter() - experiment_start
                    log_file.write(f"{timestamp}, {idx + 1}, {ISI}, {block['nerve']}, {event}\n")
                    target_time = timestamp + ISI + experiment_start
                    while time.perf_counter() < target_time:
                        pass

            self.get_resting_state()
            print("Experiment done! Go fetch the participant")

    def _check_in_on_participant(self):
        self.flush_input()
        input("Check in on the participant. Press Enter to continue...")
        time.sleep(1)



if __name__ == "__main__":
    experiment = Experiment(
        ISIs=[1, 0.05, 0.1],
        n_sequences=5,
        n_blocks=2,
        n_no_stim_blocks=1,
        omission_positions=[4, 5, 6],
        blocks_between_breaks=3,
        rest_duration=10,
        trigger_mapping={
            "stim_tibial": 1,
            "omis_tibial": 10,
            "stim_median": 2,
            "omis_median": 20,
            "non_stim": 30,
            "rest_start": 100,
            "rest_end": 110
        },
        output_path="output",
        participant_id="001"
    )

    print(f"Estimated duration: {experiment.calculate_duration() / 60:.2f} minutes")
    experiment.run()