# Apollo 11 Simulation

## Description
This Python project simulates the generation of data and reports for the Apollo 11 mission. It includes a class `Apollo11Simulation` representing the simulation, a `SimulationThread` for running the simulation in a separate thread, and a `DashboardWindow` for the simulation dashboard. The simulation generates random data files, analyzes events, manages disconnections, consolidates missions, calculates percentages, generates reports, and moves files to a backup folder.

## Installation
Clone the repository to your local machine:

```bash
git clone https://github.com/nicompiledev/apolo-11.git
```

## Dependencies
Ensure you have the following dependencies installed:

- PyQt5
- pandas
- yaml

Install them using:

```bash
pip install PyQt5 pandas pyyaml
```

## Usage

1. Set the `simulation_path` variable in the `__main__` block to the desired simulation path.

```python
simulation_path: str = "/path/to/your/simulation/folder"
```

2. Run the simulation using:

```bash
python your_script_name.py
```

## Class Overview

### `Apollo11Simulation`

#### Methods

- `__init__(simulation_folder: str, config_path: str = "config/config.yml") -> None`: Initializes the `Apollo11Simulation` object.
- `generate_random_data(file_number: int) -> Dict[str, Union[str, int, None]]`: Generates random simulation data.
- `generate_hash(data: Dict[str, Union[str, int, None]]) -> int`: Generates a hash for simulation data.
- `generate_report_filename(report_type: str) -> str`: Generates a report filename.
- `simulate(num_files_range: Tuple[int, int] = (1, 100)) -> None`: Simulates the mission by generating random data files.
- `analyze_events() -> None`: Analyzes events and generates an events report.
- `manage_disconnections() -> None`: Manages disconnections and generates a disconnections report.
- `consolidate_missions() -> None`: Consolidates missions and generates an inoperable devices report.
- `calculate_percentages() -> None`: Calculates percentages and generates a percentages report.
- `generate_file_list_report() -> None`: Generates a file list report.
- `generate_reports() -> None`: Generates all required reports.
- `move_files_to_backup() -> None`: Moves files to the backup folder.
- `get_simulation_data_copy() -> Dict[str, Union[str, int, None]]`: Returns a copy of the simulation data.

### `SimulationThread`

#### Methods

- `__init__(apollo_simulation: Apollo11Simulation) -> None`: Initializes a `SimulationThread` object.
- `run() -> None`: Runs the Apollo simulation in a separate thread.

### `DashboardWindow`

#### Methods

- `__init__(apollo_simulation: Apollo11Simulation) -> None`: Initializes the main window of the Apollo 11 Simulation Dashboard.
- `start_simulation() -> None`: Starts the simulation by initializing the simulation thread.
- `update_labels() -> None`: Updates the labels with the simulation data after the simulation is completed.
- `simulation_finished() -> None`: Performs actions after the simulation is finished.
- `read_log_file() -> str`: Reads the log file and returns its contents.
- `read_reports_files() -> str`: Reads the reports files and returns their contents.
- `show_reports() -> None`: Shows the file dialog for selecting report files and displays the selected files.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
