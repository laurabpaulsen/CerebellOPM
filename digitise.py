"""

"""

# for local imports
import sys
from pathlib import Path

# make sure to append path to OPM_lab
sys.path.append("/Users/au661930/Library/CloudStorage/OneDrive-Aarhusuniversitet/Dokumenter/project placement/OPM_lab") 
from OPM_lab.digitise import Digitiser, FastrakConnector
from OPM_lab.sensor_position import FL_alpha1_helmet, EEGcapTemplate

from .config import OPM_sensors, EEG_sensors, fiducials

def get_participant_information():
    print("Please enter participant information:")
    
    participant_info = {}

    participant_info['participant_id'] = input("Participant ID: ")

    return participant_info



if __name__ == "__main__":
    participant_info = get_participant_information()
    output_path = Path(__file__).parent / "output"

    if not output_path.exists():
        output_path.mkdir(parents=True)

    head_surface_size = 100

    connector = FastrakConnector(usb_port='/dev/cu.usbserial-110')
    connector.prepare_for_digitisation()

    digitiser = Digitiser(connector=connector)
    
    digitiser.add(category="fiducials", labels=fiducials, dig_type="single")
    digitiser.add(category="OPM", labels=OPM_sensors, dig_type="single", template=FL_alpha1_helmet)
    digitiser.add(category="EEG", labels=EEG_sensors, dig_type="single", template= EEGcapTemplate("easycap-M1"))
    digitiser.add(category="head", n_points=head_surface_size, dig_type="continuous")

    digitiser.run_digitisation()

    digitiser.save_digitisation(output_path = output_path / f'{participant_info["participant_id"]}_digitisation.csv')

    