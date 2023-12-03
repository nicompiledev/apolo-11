import os
import random

from datetime import datetime
from collections import defaultdict
import time


class Apollo11Simulation:
    def __init__(self, simulation_folder):
        self.simulation_folder = simulation_folder
        self.missions = ["ORBONE", "CLNM", "TMRS", "GALXONE", "UNKN"]
        self.device_types = ["satellite", "spaceship", "spacesuit", "space_vehicle"]
        self.device_states = [
            "excellent",
            "good",
            "warning",
            "faulty",
            "killed",
            "unknown",
        ]

    def generate_random_data(self, mission):
        data = {
            "date": datetime.now().strftime("%d%m%y%H%M%S"),
            # "mission": mission,
            "mission": random.choice(self.missions),
            "device_type": random.choice(self.device_types),
            "device_status": random.choice(self.device_states),
            "hash": None,
        }

        if mission != "UNKN":
            data["hash"] = self.generate_hash(data)

        return data

    def generate_hash(self, data):
        hash_string = f"{data['date']}{data['mission']}{data['device_type']}{data['device_status']}"
        return hash(hash_string)

    def generate_report_filename(self, report_type):
        return os.path.join(
            self.simulation_folder,
            f"APLSTATS-{report_type}-{datetime.now().strftime('%d%m%y%H%M%S')}.log",
        )

    def simulate(self, num_files_range=(1, 100), simulation_interval=20):
        for mission in self.missions:
            num_files = random.randint(num_files_range[0], num_files_range[1])

            for i in range(1, num_files + 1):
                data = self.generate_random_data(mission)
                filename = os.path.join(
                    self.simulation_folder, f"APL{mission}-{i:04d}.log"
                )

                with open(filename, "w") as file:
                    file.write(str(data))

            self.generate_reports()

            # Mover los archivos generados a la carpeta devices
            devices_folder = os.path.join(self.simulation_folder, "devices")
            os.makedirs(devices_folder, exist_ok=True)

            for file in os.listdir(self.simulation_folder):
                if file.endswith(".log"):
                    file_path = os.path.join(self.simulation_folder, file)
                    os.rename(file_path, os.path.join(devices_folder, file))

            # # Mover los archivos procesados a la carpeta backups
            # backup_folder = os.path.join(self.simulation_folder, "backups")
            # os.makedirs(backup_folder, exist_ok=True)

            # for file in os.listdir(self.simulation_folder):
            #     if file.endswith(".log"):
            #         file_path = os.path.join(self.simulation_folder, file)
            #         os.rename(file_path, os.path.join(backup_folder, file))

            # Simulate the interval
            time.sleep(20)

    def generate_reports(self):
        # Implement report generation logic here
        pass


if __name__ == "__main__":
    simulation_folder = "/home/atlanticsoft/my_repos/apolo-11"
    apollo_11_simulation = Apollo11Simulation(simulation_folder)
    apollo_11_simulation.simulate()
