"""
Module that simulates the generation of data and reports for the Apollo 11 mission.
"""

from typing import List, Dict, Tuple, Union

import os
import random
from datetime import datetime
import time
import shutil
import logging
import sys
from PyQt5.QtGui import QDesktopServices, QColor
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QMutex, QMutexLocker, QUrl, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QSizePolicy,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QLabel,
    QTextEdit,
    QPushButton,
    QFileDialog,
)
import yaml
import pandas as pd


class Apollo11Simulation:
    """
    Class representing the Apollo 11 simulation.
    """

    def __init__(self, config_path: str = "../config/config.yml") -> None:
        """
        Initialize the Apollo11Simulation object.

        Args:
            simulation_folder (str): Path to the simulation folder.
        """
        self.simulation_folder = "data"
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

        self.simulation_data_mutex = QMutex()

        with open(config_path, "r", encoding="utf-8") as config_file:
            config_data = yaml.safe_load(config_file)

        self.timesleep = config_data.get("timesleep")
        self.num_files_range = (
            config_data.get("num_files_range", {}).get("min", 1),
            config_data.get("num_files_range", {}).get("max", 100),
        )

        loggins_folder = os.path.join(self.simulation_folder, "loggins")
        os.makedirs(loggins_folder, exist_ok=True)

        logging.basicConfig(
            filename=os.path.join(loggins_folder, "simulation.log"),
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        logging.getLogger().addHandler(console_handler)

    def generate_random_data(
        self, file_number: int
    ) -> Dict[str, Union[str, int, None]]:
        """
        Generate random simulation data.

        Args:
            mission (str): Mission name.
            file_number (int): File number.

        Returns:
            dict: Randomly generated simulation data.
        """
        mission = random.choice(self.missions)

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
        reports_folder = os.path.join(self.simulation_folder, "reports")
        os.makedirs(reports_folder, exist_ok=True)

        return os.path.join(
            reports_folder,
            f"APLSTATS-{report_type}-{datetime.now().strftime('%d%m%y%H%M%S')}.csv",
        )

    def simulate(self, num_files_range: Tuple[int, int] = (1, 100)) -> None:
        """
        Simulates the mission by generating random data files and performing necessary operations.

        Args:
            num_files_range (Tuple[int, int], optional): Range of the number of files
                                                         to be generated for each mission.
                                                         Defaults (1, 100).

        Returns:
            None"""

        try:
            devices_folder = os.path.join(self.simulation_folder, "devices")
            os.makedirs(devices_folder, exist_ok=True)

            logging.info("Simulation is running...")

            total_files_to_generate = random.randint(
                num_files_range[0], num_files_range[1]
            )

            total_files_to_generate_log = total_files_to_generate

            files_created_counter = 0

            while total_files_to_generate > 0:
                num_files = min(
                    total_files_to_generate,
                    random.randint(num_files_range[0], num_files_range[1]),
                )

                for i in range(1, num_files + 1):
                    data = self.generate_random_data(i)
                    filename = os.path.join(devices_folder, data["filename"])

                    with open(filename, "w", encoding="utf-8") as file:
                        file.write(str(data))
                        self.simulation_data.append(data)

                    with QMutexLocker(self.simulation_data_mutex):
                        self.simulation_data.append(data)

                    total_files_to_generate -= 1
                    files_created_counter += 1

            logging.debug(
                "Files created in 'devices' folder: %d", files_created_counter
            )
            logging.info(
                "Total files generated in this simulation: %d",
                total_files_to_generate_log,
            )

            self.generate_file_list_report()
            self.generate_reports()
            self.move_files_to_backup()
            logging.info("Simulation completed successfully.")

        except (FileNotFoundError, PermissionError) as e:
            logging.error("An error occurred during simulation: %s", str(e))

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
        try:
            self.analyze_events()
            self.manage_disconnections()
            self.consolidate_missions()
            self.calculate_percentages()
            self.generate_file_list_report()

            logging.info("Reports generated successfully.")
        except (FileNotFoundError, PermissionError, pd.errors.EmptyDataError) as e:
            logging.error("Error generating reports: %s", str(e))

        self.simulation_data = []

    def move_files_to_backup(self) -> None:
        """
        Move files to backup folder.
        """
        backup_folder = os.path.join(self.simulation_folder, "backups")
        os.makedirs(backup_folder, exist_ok=True)

        devices_folder = os.path.join(self.simulation_folder, "devices")

        files_before_move = os.listdir(devices_folder)

        for file in os.listdir(devices_folder):
            file_path = os.path.join(devices_folder, file)
            backup_path = os.path.join(backup_folder, file)

            try:
                shutil.move(file_path, backup_path)
            except OSError as e:
                logging.error("Error moving file %s to backups: %s", file, str(e))
            else:
                logging.debug("Moved file %s to backups", file)

        files_after_move = os.listdir(devices_folder)

        files_moved_count = len(files_before_move) - len(files_after_move)

        logging.info("Moved %d files from 'devices' to 'backups'", files_moved_count)

    def get_simulation_data_copy(self):
        """
        Returns a copy of the simulation data.

        Returns:
            dict: A copy of the simulation data.
        """
        with QMutexLocker(self.simulation_data_mutex):
            return self.simulation_data.copy()


class SimulationThread(QThread):
    """
    A QThread subclass for running the Apollo simulation in a separate thread.

    This class provides a mechanism to execute the Apollo simulation without blocking the main application thread.
    It handles the execution of the simulation and emits a signal when the simulation is completed.

    Attributes:
        simulation_completed (pyqtSignal): A signal emitted when the simulation has finished.
    """

    simulation_completed = pyqtSignal()

    def __init__(self, apollo_simulation):
        """
        Initializes a SimulationThread object.

        Parameters:
            apollo_simulation (ApolloSimulation): The ApolloSimulation object used for the simulation.

        Returns:
            None
        """
        super().__init__()
        self.apollo_simulation = apollo_simulation

    def run(self):
        """
        Runs the Apollo simulation.

        This method initiates the Apollo simulation by calling the `simulate` method of the `apollo_simulation` object.
        It also emits a signal `simulation_completed` when the simulation is completed.

        Parameters:
            None

        Returns:
            None
        """
        self.apollo_simulation.simulate(
            num_files_range=self.apollo_simulation.num_files_range
        )
        self.simulation_completed.emit()


class DashboardWindow(QWidget):
    """
    Represents the main window of the Apollo 11 Simulation Dashboard.
    """

    def __init__(self, apollo_simulation):
        super().__init__()

        primary_color = QColor(33, 150, 243)  # Blue
        secondary_color = QColor(255, 150, 0)  # Orange
        background_color = QColor(38, 50, 56)  # Dark Gray

        self.setStyleSheet(
            """
            QWidget {
                background-color: %s;
                color: %s;
            }
            QLabel {
                color: %s;
            }
            QPushButton {
                background-color: %s;
                color: white;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: %s;
            }
            QGroupBox {
                border: 2px solid %s;
                border-radius: 15px;
                margin-top: 10px;
            }
            QTextEdit {
                background-color: white;
                border: 2px solid %s;
            }
            """
            % (
                background_color.name(),
                primary_color.name(),
                primary_color.name(),
                secondary_color.name(),
                secondary_color.lighter(110).name(),
                primary_color.name(),
                primary_color.name(),
            )
        )

        self.setWindowTitle("Apollo 11 Simulation Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        self.setStyleSheet("background-color: #001f3f; color: white;")

        self.description_label = QLabel(
            "This Python project simulates the generation of data and reports for the Apollo 11 mission.\n"
            "The simulation generates random data files, analyzes events, manages disconnections, consolidates "
            "missions, calculates percentages, generates reports, and moves files to a backup folder.",
            self,
        )
        self.description_label.setWordWrap(True)

        self.label_simulation = QLabel("Initializing simulation...", self)

        self.log_group_box = QGroupBox("Log", self)
        self.log_text_edit = QTextEdit(self.log_group_box)
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setMinimumHeight(200)
        self.log_text_edit.setMaximumWidth(800)

        self.reports_group_box = QGroupBox("Reports", self)
        self.reports_text_edit = QTextEdit(self.reports_group_box)
        self.reports_text_edit.setReadOnly(True)
        self.reports_text_edit.setMinimumHeight(200)
        self.reports_text_edit.setMaximumWidth(800)

        self.show_reports_button = QPushButton("Show Reports", self)
        self.show_reports_button.setFixedWidth(150)
        self.show_reports_button.clicked.connect(self.show_reports)
        self.show_reports_button.setStyleSheet(
            f"background-color: {secondary_color.name()}; color: black;"
        )

        self.footer_label = QLabel(
            'Copyright © 2024 <a style="color: lightgray;" href="https://github.com/nicompiledev/apolo-11">@nicompiledev</a> and company. All rights reserved.<br>'
            "This project was funded by SoftServe through the #CodingUpMyFuture Python Bootcamp 2023.",
            self,
        )
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setOpenExternalLinks(True)

        self.layout = QVBoxLayout(self)

        hbox_layout = QHBoxLayout()

        reports_layout = QVBoxLayout(self.reports_group_box)
        reports_layout.addWidget(self.reports_text_edit)
        reports_layout.addWidget(self.show_reports_button)

        hbox_layout.addWidget(self.log_group_box)
        hbox_layout.addWidget(self.reports_group_box)

        self.layout.addWidget(self.description_label)
        self.layout.addWidget(self.label_simulation)
        self.layout.addLayout(hbox_layout)
        self.layout.addWidget(self.footer_label)

        log_layout = QVBoxLayout(self.log_group_box)
        log_layout.addWidget(self.log_text_edit)

        self.apollo_simulation = apollo_simulation

        self.simulation_thread = SimulationThread(apollo_simulation)
        self.simulation_thread.simulation_completed.connect(self.update_labels)
        self.simulation_thread.finished.connect(self.simulation_finished)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_simulation)
        self.timer.start(apollo_simulation.timesleep * 1000)

        self.show()

        self.mutex_for_labels = QMutex()

    def start_simulation(self):
        """
        Starts the simulation by initializing the simulation thread and updating the simulation label.
        """
        print("Simulating...")
        self.label_simulation.setText("Generating files and reports...")
        self.simulation_thread.start()

    def update_labels(self):
        """
        Updates the labels with the simulation data after the simulation is completed.
        """
        with QMutexLocker(self.mutex_for_labels):
            simulation_data_copy = self.apollo_simulation.get_simulation_data_copy()

            print(f"Files Generated: {len(simulation_data_copy)}")
            print(
                f"Reports Generated: {len(set(data['filename'] for data in simulation_data_copy))}"
            )
            print("Simulation completed")

    def simulation_finished(self):
        """
        Performs actions after the simulation is finished, such as updating labels, displaying log records, and displaying reports.
        """
        print("Simulation finished")
        self.update_labels()

        log_contents = self.read_log_file()
        self.log_text_edit.setPlainText(log_contents)

        reports_contents = self.read_reports_files()
        self.reports_text_edit.setPlainText(reports_contents)

    def read_log_file(self):
        """
        Reads the log file and returns its contents.

        Returns:
            str: The contents of the log file.
        """
        log_file_path = os.path.join(
            self.apollo_simulation.simulation_folder, "loggins", "simulation.log"
        )
        try:
            with open(log_file_path, "r", encoding="utf-8") as log_file:
                return log_file.read()
        except FileNotFoundError:
            return f"Log file not found at: {log_file_path}"

    def read_reports_files(self):
        """
        Reads the reports files and returns their contents.

        Returns:
            str: The contents of the reports files.
        """
        reports_folder = os.path.join(
            self.apollo_simulation.simulation_folder, "reports"
        )
        reports_contents = ""

        try:
            for file in os.listdir(reports_folder):
                reports_contents += f"{os.path.basename(file)}\n"
        except FileNotFoundError:
            return "Reports folder not found."

        return reports_contents

    def show_reports(self):
        """
        Shows the file dialog for selecting report files and displays the selected files in the reports text edit.
        """
        reports_folder = os.path.join(
            self.apollo_simulation.simulation_folder, "reports"
        )
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        file_dialog = QFileDialog(self)
        file_dialog.setDirectory(reports_folder)
        file_dialog.setWindowTitle("Select Report Files")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(
            "CSV files (*.csv);;Text files (*.txt);;All files (*)"
        )
        file_dialog.setOptions(options)

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()

            reports_contents = "\n".join(
                os.path.basename(file) for file in selected_files
            )

            self.reports_text_edit.setPlainText(reports_contents)

            for file_path in selected_files:
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    simulation_path: str = os.path.join(script_dir, "apolo-11")
    apollo_11_simulation: Apollo11Simulation = Apollo11Simulation()

    app = QApplication([])
    dashboard = DashboardWindow(apollo_11_simulation)
    app.exec_()
