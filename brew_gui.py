import subprocess
import sys

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


# --- REUSABLE WORKER ---
# This worker can now run any function with any arguments in a thread.
class Worker(QObject):
    finished = Signal()

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        finally:
            self.finished.emit()


# --- BACKEND FUNCTIONS ---
def get_installed_packages():
    try:
        all_packages = []

        # Get formulae
        formulae_result = subprocess.run(
            ["/opt/homebrew/bin/brew", "list", "--formula"],
            capture_output=True,
            text=True,
            check=True,
        )
        formulae = formulae_result.stdout.strip().split("\n")
        if formulae and formulae[0]:  # Check if list has content
            all_packages.extend(formulae)

        # Get casks
        cask_result = subprocess.run(
            ["/opt/homebrew/bin/brew", "list", "--cask"],
            capture_output=True,
            text=True,
            check=True,
        )
        casks = cask_result.stdout.strip().split("\n")
        if casks and casks[0]:  # Check if list has content
            all_packages.extend(casks)

        return sorted(all_packages)  # Return a single, sorted list

    except (subprocess.CalledProcessError, FileNotFoundError):
        return ["Error: Could not get /opt/homebrew/bin/brew packages."]


def search_packages(package_name):
    try:
        result = subprocess.run(
            ["/opt/homebrew/bin/brew", "search", package_name],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split("\n")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ["Error: Search failed."]


def install_package(package_name):
    subprocess.run(
        ["/opt/homebrew/bin/brew", "install", package_name], capture_output=True
    )


def uninstall_package(package_name):
    subprocess.run(
        ["/opt/homebrew/bin/brew", "uninstall", package_name], capture_output=True
    )


def upgrade_all_packages():
    subprocess.run(["/opt/homebrew/bin/brew", "upgrade"], capture_output=True)


# --- MAIN APPLICATION ---
app = QApplication(sys.argv)

# UI Elements
list_widget = QListWidget()
search_input = QLineEdit()


filter_button = QPushButton("Filter Installed")
search_new_button = QPushButton("Search New")

install_button = QPushButton("Install Selected")
uninstall_button = QPushButton("Uninstall Selected")
upgrade_button = QPushButton("Upgrade All")

# Layouts
search_layout = QHBoxLayout()
search_layout.addWidget(search_input)
search_layout.addWidget(filter_button)
search_layout.addWidget(search_new_button)

button_layout = QHBoxLayout()
button_layout.addWidget(install_button)
button_layout.addWidget(uninstall_button)
button_layout.addWidget(upgrade_button)

layout = QVBoxLayout()
layout.addLayout(search_layout)
layout.addWidget(list_widget)
layout.addLayout(button_layout)

central_widget = QWidget()
central_widget.setLayout(layout)

window = QMainWindow()
window.setWindowTitle("Brew GUI")
window.resize(600, 500)
window.setCentralWidget(central_widget)

# --- THREADING and HANDLERS ---
thread = None
worker = None


def run_long_task(function, *args):
    global thread, worker

    # Disable buttons during task
    install_button.setEnabled(False)
    uninstall_button.setEnabled(False)
    upgrade_button.setEnabled(False)

    thread = QThread()
    worker = Worker(function, *args)
    worker.moveToThread(thread)

    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    def on_finish():
        refresh_list()
        install_button.setEnabled(True)
        uninstall_button.setEnabled(True)
        upgrade_button.setEnabled(True)

    worker.finished.connect(on_finish)
    thread.start()


def refresh_list():
    list_widget.clear()
    list_widget.addItems(get_installed_packages())


def set_search_mode(mode):
    global search_mode
    search_mode = mode
    if mode == "filter":
        filter_button.setStyleSheet("background-color: #add8e6;")  # Light blue
        search_new_button.setStyleSheet("")
        search_input.setPlaceholderText("Filter installed packages...")
        refresh_list()
    else:  # 'search' mode
        search_new_button.setStyleSheet("background-color: #add8e6;")
        filter_button.setStyleSheet("")
        search_input.setPlaceholderText(
            "Search all of Home/opt/homebrew/bin/brew for new packages..."
        )
        list_widget.clear()


def handle_search():
    query = search_input.text().lower()
    if not query:
        if search_mode == "filter":
            refresh_list()
        return

    if search_mode == "filter":
        # Live filter logic
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setHidden(query not in item.text().lower())
    else:  # 'search' mode
        # Run /opt/homebrew/bin/brew search
        results = search_packages(query)
        list_widget.clear()
        list_widget.addItems(results)


def handle_install():
    current_item = list_widget.currentItem()
    if current_item:
        run_long_task(install_package, current_item.text())


def handle_uninstall():
    current_item = list_widget.currentItem()
    if current_item:
        run_long_task(uninstall_package, current_item.text())


def handle_upgrade():
    run_long_task(upgrade_all_packages)


# --- CONNECTIONS ---


filter_button.clicked.connect(lambda: set_search_mode("filter"))
search_new_button.clicked.connect(lambda: set_search_mode("search"))
search_input.returnPressed.connect(handle_search)
install_button.clicked.connect(handle_install)
uninstall_button.clicked.connect(handle_uninstall)
upgrade_button.clicked.connect(handle_upgrade)

# --- STARTUP ---
set_search_mode("filter")
refresh_list()
window.show()
app.exec()
