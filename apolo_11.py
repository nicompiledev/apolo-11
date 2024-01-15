"""
Module that simulates the generation of data and reports for the Apollo 11 mission.
"""
from typing import List, Dict, Tuple, Union

import os
import random
from datetime import datetime
import time
import pandas as pd


class Apollo11Simulation:
    """
    Class representing the Apollo 11 simulation.
    """

    def __init__(self, simulation_folder: str) -> None:
        """
        Initialize the Apollo11Simulation object.

        Args:
            simulation_folder (str): Path to the simulation folder.
        """
        self.simulation_folder = simulation_folder
        self.missions: List[str] = ["ORBONE", "CLNM", "TMRS", "GALXONE", "UNKN"]
        self.device_types: List[str] = [
            "satellite",
            "spaceship",
            "spacesuit",
            "space_vehicle",
        ]
        self.device_states: List[str] = [
            "excellent",
            "good",
            "warning",
            "faulty",
            "killed",
            "unknown",
        ]
        self.simulation_data: List[Dict[str, Union[str, int, None]]] = []

    def generate_random_data(
        self, mission: str, file_number: int
    ) -> Dict[str, Union[str, int, None]]:
        """
        Generate random simulation data.

        Args:
            mission (str): Mission name.
            file_number (int): File number.

        Returns:
            dict: Randomly generated simulation data.
        """
        data: Dict[str, Union[str, int, None]] = {
            "date": datetime.now().strftime("%d%m%y%H%M%S"),
            "mission": mission
            if mission != "UNKN"
            else f"UNKNOWN-{datetime.now().strftime('%d%m%y%H%M%S')}",
            "device_type": "unknown"
            if mission == "UNKN"
            else random.choice(self.device_types),
            "device_status": "unknown"
            if mission == "UNKN"
            else random.choice(self.device_states),
            "hash": None,
            "filename": f"APL{mission}-{file_number:04d}.log",
        }

        if mission != "UNKN":
            data["hash"] = self.generate_hash(data)

        return data

    def generate_hash(self, data: Dict[str, Union[str, int, None]]) -> int:
        """
        Generate hash for simulation data.

        Args:
            data (dict): Simulation data.

        Returns:
            int: Hash value.
        """
        hash_string = f"{data['date']}{data['mission']}{data['device_type']}{data['device_status']}"
        return hash(hash_string)

    def generate_report_filename(self, report_type: str) -> str:
        """
        Generate report filename.

        Args:
            report_type (str): Type of report.

        Returns:
            str: Report filename.
        """
        return os.path.join(
            self.simulation_folder,
            f"APLSTATS-{report_type}-{datetime.now().strftime('%d%m%y%H%M%S')}.csv",
        )

    def simulate(self, num_files_range: Tuple[int, int] = (1, 100)) -> None:
        """
        Run the simulation.

        Args: \
            num_files_range (tuple, optional): Range of number of files to simulate. \
                                       Defaults to (1, 100).
        """

        devices_folder = os.path.join(self.simulation_folder, "devices")
        os.makedirs(devices_folder, exist_ok=True)

        print("Simulation is running...")

        for mission in self.missions:
            num_files = random.randint(num_files_range[0], num_files_range[1])

            for i in range(1, num_files + 1):
                data = self.generate_random_data(mission, i)
                filename = os.path.join(devices_folder, data["filename"])

                with open(filename, "w", encoding="utf-8") as file:
                    file.write(str(data))
                    self.simulation_data.append(data)

        self.generate_file_list_report()
        self.generate_reports()
        self.move_files_to_backup()

    def move_files_to_backup(self) -> None:
        """
        Move files to backup folder.
        """
        backup_folder = os.path.join(self.simulation_folder, "backups")
        os.makedirs(backup_folder, exist_ok=True)

        devices_folder = os.path.join(self.simulation_folder, "devices")
        os.makedirs(devices_folder, exist_ok=True)

        for file in os.listdir(devices_folder):
            file_path = os.path.join(devices_folder, file)
            os.rename(file_path, os.path.join(backup_folder, file))

    def analyze_events(self) -> None:
        """
        Analyze events and generate events report.
        """
        events_data = pd.DataFrame(self.simulation_data)
        events_report = (
            events_data.groupby(["mission", "device_status"])
            .size()
            .unstack(fill_value=0)
        )
        events_report.to_csv(self.generate_report_filename("events"), index=True)

    def manage_disconnections(self) -> None:
        """
        Manage disconnections and generate disconnections report.
        """
        disconnections_data = pd.DataFrame(self.simulation_data)
        unknown_disconnections = disconnections_data[
            (disconnections_data["device_status"] == "unknown")
            & (disconnections_data["mission"] != "UNKN")
        ]
        disconnections_report = (
            unknown_disconnections.groupby(["mission", "device_type"])
            .size()
            .sort_values(ascending=False)
        )
        disconnections_report.to_csv(
            self.generate_report_filename("disconnections"),
            header=["Disconnected Devices"],
        )

    def consolidate_missions(self) -> None:
        """
        Consolidate missions and generate inoperable devices report.
        """
        consolidated_data = pd.DataFrame(self.simulation_data)
        inoperable_devices = consolidated_data[
            consolidated_data["device_status"].isin(["killed"])
        ]
        inoperable_report = inoperable_devices.groupby("mission").size()
        inoperable_report.to_csv(
            self.generate_report_filename("inoperable_devices"),
            header=["Inoperable Devices"],
        )

    def calculate_percentages(self) -> None:
        """
        Calculate percentages and generate percentages report.
        """
        percentages_data = pd.DataFrame(self.simulation_data)
        percentages_report = (
            percentages_data.groupby(["mission", "device_type"]).size()
            / len(percentages_data)
            * 100
        )
        percentages_report.to_csv(
            self.generate_report_filename("percentages"), header=["Percentage of Data"]
        )

    def generate_file_list_report(self) -> None:
        """
        Generate file list report.
        """
        files_list = []

        for data in self.simulation_data:
            file_info = {
                "filename": data["filename"],
                "date": data["date"],
                "mission": data["mission"],
                "device_type": data["device_type"],
                "device_status": data["device_status"],
                "hash": data["hash"],
                "file's size ": os.path.getsize(
                    os.path.join(self.simulation_folder, "devices", data["filename"])
                ),
                "last_modified": datetime.fromtimestamp(
                    os.path.getmtime(
                        os.path.join(
                            self.simulation_folder, "devices", data["filename"]
                        )
                    )
                ).strftime("%d%m%y%H%M%S"),
            }
            files_list.append(file_info)

        files_report = pd.DataFrame(files_list)
        files_report.to_csv(self.generate_report_filename("file_list"), index=False)

    def generate_reports(self) -> None:
        """
        Generate all the required reports.
        """
        self.analyze_events()
        self.manage_disconnections()
        self.consolidate_missions()
        self.calculate_percentages()

        self.simulation_data = []


if __name__ == "__main__":
    simulation_path: str = "/home/atlanticsoft/my_repos/apolo_11"
    apollo_11_simulation: Apollo11Simulation = Apollo11Simulation(simulation_path)

    while True:
        apollo_11_simulation.simulate()
        time.sleep(20)
