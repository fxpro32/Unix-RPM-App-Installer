##############################################################################################
##############################################################################################
#                               ESSENTIAL APPLICATIONS TOOLS                                 #
#                ESSENTIAL SOFTWARE INSTALLER FOR RED HAT - RPM SYSTEMS                      #
##############################################################################################
##############################################################################################
#                                                                                            #
#           Copyright (c) By Pietro Casoar - Freeware - Licensed Under GNU3.0                #
#          This Menu is primarily only for use with RedHat / RPM Based Systems               #
#                                                                                            #
#                         Why develop this Software Application?                             #
#    I'm a Linux daily user, namely using Nobara / Fedora RPM Systems as a daily driver      #
# and I thought I would help people move across from unethical & low Quality Windows system  #
#        to high quality Nobara / Fedora / Rocky / Red Hat RPM Operating systems             #
# By making this software installer, it will help fast track people to obtain the software   #
#  applications that most end users need and use, installed on their Linux daily driver OS   #
#                                                                                            #
##############################################################################################
##############################################################################################

# Initiate script
import os
import curses
import time
import subprocess
import sys
import threading
import select
import textwrap

######################################################################################################

# Define the function to check if an application is installed
def check_installed(app, debug):
    debug_info = ""

    # Check if the application is in the PATH
    result = subprocess.run(["which", app], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if debug:
        debug_info += "Checking if {} is in the PATH: {}\n".format(app, result.returncode == 0)
    if result.returncode == 0:
        return True, debug_info

    # Check if the application is in the RPM database
    result = subprocess.run(["rpm", "-q", app], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if debug:
        debug_info += "Checking if {} is in the RPM database: {}\n".format(app, result.returncode == 0)
    return result.returncode == 0, debug_info

# Define the function to start Docker service
def start_docker_service(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Starting Docker service...")
    stdscr.refresh()
    result = subprocess.run(["sudo", "systemctl", "start", "docker"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        stdscr.addstr(1, 0, "Docker service started successfully")
    else:
        stdscr.addstr(1, 0, "Failed to start Docker service: {}".format(result.stderr.decode()))
    stdscr.refresh()
    time.sleep(0.01)  # Pause for 0.01 seconds - for debug

# Define the function to check Docker status
def check_docker_status(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Checking Docker status...")
    stdscr.refresh()
    result = subprocess.run(["sudo", "systemctl", "status", "docker"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdscr.addstr(2, 0, result.stdout.decode())
    stdscr.refresh()
    time.sleep(3)  # Pause for 3 seconds - for debug

# Define the function to check required packages
def check_required_packages(stdscr, debug=False):
    required_apps = ["fuse", "docker", "ruby-irb","rubygems", "rubygem-bigdecimal", "rubygem-rake", "rubygem-i18n", "rubygem-bundler", "git", "svn", "ruby", "ruby-devel", "libcap-devel", "rake", "curl"]
    missing_apps = []

    # Check if the applications are installed
    for app in required_apps:
        stdscr.clear()
        stdscr.addstr(0, 0, "Checking if {} is installed...".format(app))
        stdscr.refresh()
        time.sleep(0.01)  # Pause for 0.01 seconds between each application check - for debug

        is_installed, debug_info = check_installed(app, debug)
        if debug:
            stdscr.clear()
            stdscr.addstr(0, 0, debug_info)
            stdscr.refresh()
        time.sleep(0.01)  # Pause for 0.01 seconds after each application check - for debug

        if not is_installed:
            missing_apps.append(app)

    if missing_apps:
        stdscr.clear()
        stdscr.addstr(0, 0, "The following required applications are missing: {}".format(", ".join(missing_apps)))
        stdscr.addstr(1, 0, "Would you like to install them? (Y/N)")
        stdscr.refresh()

        time.sleep(0.01)  # Pause for 01 second before proceeding - for debug

        while True:
            key = stdscr.getch()
            if key in [ord('Y'), ord('y')]:
                # User confirmed to install the packages
                for app in missing_apps:
                    stdscr.clear()
                    stdscr.addstr(0, 0, "Installing {}... Please wait...".format(app))
                    stdscr.refresh()
                    spinner = threading.Thread(target=spin, args=(stdscr, 0, 50,))
                    spinner.start()
                    result = subprocess.run(["sudo", "dnf", "install", "-y", app], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    spinner.do_run = False
                    spinner.join()
                    if result.returncode == 0:
                        stdscr.addstr(1, 0, "{} has been installed successfully".format(app))
                    else:
                        stdscr.addstr(1, 0, "Failed to install {}: {}".format(app, result.stderr.decode()))
                    stdscr.addstr(2, 0, "Press Enter to continue.")
                    stdscr.refresh()
                    time.sleep(0.01)  # Pause for 01 second after each installation - for debug

                break
            elif key in [ord('N'), ord('n')]:
                stdscr.addstr(2, 0, "The applications listed are required, without these the installation script will not function. Press ENTER to exit.")
                stdscr.refresh()
                time.sleep(1)  # Pause for 1 second before exiting the script - for debug
                sys.exit()  # Exit Script

def spin(stdscr, y, x):
    spinner = "|/-\\"
    i = 0
    current_thread = threading.current_thread()
    while getattr(current_thread, "do_run", True):
        stdscr.addstr(y, x, spinner[i])
        stdscr.refresh()
        time.sleep(0.2)
        i = (i + 1) % len(spinner)
    stdscr.addstr(y, x, " ")

# Main function
def main(stdscr):
    # Check for required packages with debugging enabled
    check_required_packages(stdscr, True)

    # Start Docker service
    start_docker_service(stdscr)

    # Check Docker status
    check_docker_status(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)

# dnf checking procedure
installed_packages_process = subprocess.run(["dnf", "list", "installed"], stdout=subprocess.PIPE, text=True)
installed_packages = installed_packages_process.stdout

# Add 'menu' as a parameter
def print_menu(stdscr, selected_row_idx, menu): #, padding=0):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Multi-line ASCII art
    your_ascii_art = """
 __ __ ____  ____ __ __      ______  ___   ___  _     _____
|  T  |    \l    |  T  T    |      T/   \ /   \| T   / ___/
|  |  |  _  Y|  T|  |  |    |      Y     Y     | |  (   \_ 
|  |  |  |  ||  |l_   _j    l_j  l_|  O  |  O  | l___\__  T
|  :  |  |  ||  ||     |      |  | |     |     |     /  \ |
l     |  |  |j  l|  |  |      |  | l     l     |     \    |
 \__,_l__j__|____|__j__|      l__j  \___/ \___/l_____j\___j
                                                                                       
** Copyright (c) By FXPRO - Freeware - Licensed Under GNU3.0 **
** Based on the menu idea by LionSec with Katoolin on Debian Systems **

 _____  ___  ____       ____    ___ ___        __ __  ____ ______                 ____  ____  ___ ___ 
|     |/   \|    \     |    \  /  _|   \      |  T  T/    |      T               |    \|    \|   T   T
|   __Y     |  D  )    |  D  )/  [_|    \     |  l  Y  o  |      |     _____     |  D  |  o  | _   _ |
|  l_ |  O  |    /     |    /Y    _|  D  Y    |  _  |     l_j  l_j    |     |    |    /|   _/|  \_/  |
|   _]|     |    \     |    \|   [_|     |    |  |  |  _  | |  |      l_____j    |    \|  |  |   |   |
|  T  l     |  .  Y    |  .  |     |     |    |  |  |  |  | |  |                 |  .  |  |  |   |   |
l__j   \___/l__j\_j    l__j\_l_____l_____j    l__j__l__j__j l__j                 l__j\_l__j  l___j___j
    """

    # Get the size of your ASCII art
    ascii_art_lines = your_ascii_art.split('\n')
    ascii_art_height = len(ascii_art_lines)
    ascii_art_width = max(len(line) for line in ascii_art_lines)

    # Check if ASCII art can fit in the terminal
    if ascii_art_width <= w and ascii_art_height <= h:
        stdscr.attron(curses.color_pair(2))  # Turn on color pair 2 (should be green)
        for i, line in enumerate(ascii_art_lines):
            if i < h:  # Only try to print the line if it's within the window's height
                x = (w - len(line)) // 2  # Calculate x position for center alignment
                stdscr.addstr(i, x, line)
        stdscr.attroff(curses.color_pair(2))  # Turn off color pair 2

    # Calculate padding as 25% of the terminal height
    padding = int(h * 0.50)

# print menu here
    for idx, row in enumerate(menu):
        x = w//2 - len(row)//2
        y = h//2 - len(menu)//2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
    stdscr.refresh()

def main(stdscr):
    # initialize color pair
    curses.curs_set(0)
    # colour scheme
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # Specify the current selected row
    current_row = 0

    # initialize menu
    current_row = 0
    menu = ['First Step - Install Required Repositories',
            'Second Step - View Categories',
            'Third Step - ##Spare##',
            'Help', 'Exit']
    print_menu(stdscr, current_row, menu)
    while True:
        key = stdscr.getch()

        # navigate up and down the menu
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        # when an option is selected
        elif key == curses.KEY_ENTER or key in [10, 13]:

            if menu[current_row] == 'First Step - Install Required RPM Repositories':
                # Handle the installation of repositories
                submenu_install_repositories(stdscr)

            elif menu[current_row] == 'Second Step - View Categories':
                # Handle the display of categories
                submenu_categories(stdscr)

            elif menu[current_row] == 'Third Step - Spare Section Here':
                # Handle the installation of Kali Menu & Stuff
                stdscr.addstr(0, 0, "This is a spare section")

            elif menu[current_row] == 'Help':
                # Handle the display of Help
                submenu_help(stdscr)

            elif menu[current_row] == 'Exit':
                # Exit the application
                stdscr.addstr(0, 0, "Exiting the application")
                stdscr.refresh()
                stdscr.getch()
                break

            stdscr.getch()
            # if user selected last row, exit the program
            if current_row == len(menu) - 1:
                break

        print_menu(stdscr, current_row, menu)

        stdscr.refresh()
        # End of the main menu section

# This section is for Main Menu Selection #1
def submenu_install_repositories(stdscr):
    # Sub-menu for Install Repositories
    menu = ['Automatically install ALL repositories required', 
            'Go Back']
    current_row = 0
    print_menu(stdscr, current_row, menu)

    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if menu[current_row] == 'Go Back':
                break
            # Similar stubbing for each category
            elif menu[current_row] == 'Automatically install ALL required repositories':
                stdscr.clear()
                stdscr.addstr(0, 0, "Install additional repositories here")
                stdscr.refresh()
                stdscr.getch()

        print_menu(stdscr, current_row, menu)

#def submenu_install_repositories(stdscr):
    # Sub-menu for Install Repositories
    menu = ['Automatically install ALL repositories required', 
            'Go Back']
    current_row = 0
    print_menu(stdscr, current_row, menu)

    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if menu[current_row] == 'Go Back':
                break
            elif menu[current_row] == 'Automatically install ALL repositories required':
                stdscr.clear()
                repositories = [
                    'https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm', 
                    'https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm'
                ]
                install_repositories(stdscr, repositories)
        print_menu(stdscr, current_row, menu)

# Repository Section
def install_repositories(stdscr, repositories):
    # Check if repositories are already installed
    result = subprocess.run(["dnf", "repolist"], capture_output=True, text=True)
    if "rpmfusion" in result.stdout:
        stdscr.addstr(0, 0, "Repositories are already installed. Press Enter to continue.")
        stdscr.refresh()
        stdscr.getch()
        return

    for repo in repositories:
        try:
            stdscr.addstr(0, 0, "Attempting to Install {} Please Wait...".format(repo))
            os.system('sudo dnf install -y {}'.format(repo))
            stdscr.addstr(1, 0, "{} has been installed successfully".format(repo))
            # Wait a second before moving on to the next repository
            time.sleep(1)
        except Exception as e:
            stdscr.addstr(1, 0, "Failed to install {}: {}".format(repo, e))

    stdscr.addstr(2, 0, "All done. Press Enter to continue.")
    stdscr.refresh()
    stdscr.getch()

# This section is for Selection Number #2
def submenu_categories(stdscr):

    # Multi-line ASCII art
    submenu2_ascii_heading = """
 __ __ ____  ____ __ __      ______  ___   ___  _     _____
|  T  |    \l    |  T  T    |      T/   \ /   \| T   / ___/
|  |  |  _  Y|  T|  |  |    |      Y     Y     | |  (   \_ 
|  |  |  |  ||  |l_   _j    l_j  l_|  O  |  O  | l___\__  T
|  :  |  |  ||  ||     |      |  | |     |     |     /  \ |
l     |  |  |j  l|  |  |      |  | l     l     |     \    |
 \__,_l__j__|____|__j__|      l__j  \___/ \___/l_____j\___j
    __  ____ ______   ___  ____  ___  ____  __ __       _______ __ ____  ___ ___   ___ ____  __ __ 
   /  ]/    |      T /  _]/    T/   \|    \|  T  T     / ___|  T  |    \|   T   T /  _|    \|  T  T
  /  /Y  o  |      |/  [_Y   __Y     |  D  |  |  |    (   \_|  |  |  o  | _   _ |/  [_|  _  |  |  |
 /  / |     l_j  l_Y    _|  T  |  O  |    /|  ~  |     \__  |  |  |     |  \_/  Y    _|  |  |  |  |
/   \_|  _  | |  | |   [_|  l_ |     |    \l___, |     /  \ |  :  |  O  |   |   |   [_|  |  |  :  |
\     |  |  | |  | |     |     l     |  .  |     !     \    l     |     |   |   |     |  |  l     |
 \____l__j__j l__j l_____l___,_j\___/l__j\_l____/       \___j\__,_l_____l___j___l_____l__j__j\__,_j
    """

# ASCII heading
    ascii_heading_lines = submenu2_ascii_heading.split('\n')

    h, w = stdscr.getmaxyx()  # get the height and width of the window

    stdscr.attron(curses.color_pair(3))  # Turn on color pair 3 (should be yellow)
    for i, line in enumerate(ascii_heading_lines):
        if i < h:
            x = (w - len(line)) // 2  # Calculate x position for center alignment
            stdscr.addstr(i, x, line)
    stdscr.attroff(curses.color_pair(3))  # Turn off color pair 3

def submenu_menu1(stdscr):
    # Sub-menu for categories
    menu = ['Internet Applications', 
            'Multimedia Applications', 
            'Office and Productivity Applications', 
            'Graphics and Photography Applications', 
            'Educational Applications', 
            'Coding and Developer Applications', 
            'Social Media Applications', 
            'Scientific Applications', 
            'System Applications', 
            'Games', 
            'General Utilities', 
            'Hacking Applications', 
            'Emulators', 

            'Bittorrent Clients', 
            'Downloader Clients', 
            'Miscellaneous Applications', 

            'Full Install Section', 
            'Go Back']
    current_row = 0
    h, w = stdscr.getmaxyx()
    padding = int(h * 0.10)

    while True:
        stdscr.clear()
        stdscr.attron(curses.color_pair(3))  # Turn on color pair 3 (should be yellow)
        for i, line in enumerate(ascii_heading_lines):  # Added these lines
            if i < h:
                x = (w - len(line)) // 2  # Calculate x position for center alignment
                stdscr.addstr(i, x, line)
        stdscr.attroff(curses.color_pair(3))  # Turn off color pair 3

        for idx, row in enumerate(menu):
            x = w//2 - len(row)//2
            y = h//2 - len(menu)//2 + idx + padding
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, row)
        stdscr.refresh()

        # Added: navigation code
        key = stdscr.getch()

        # Navigate the menu
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]: # Enter keys
            if menu[current_row] == 'Go Back':  # if 'Go Back' option is selected
                return  # return to the calling function
            else:
                stdscr.addstr(0, 0, "You selected '{}'".format(menu[current_row]))

            # On 'Enter', handle the selection
            if menu[current_row] == 'Web Browsers':
                submenu_menu1(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Web Browsers here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Multimedia Applications':
#                submenu_menu2(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Multimedia Applications here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Office and Productivity Applications':
#                submenu_menu3(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Office and Productivity Applications here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Graphics and Photography Applications':
#                submenu_menu4(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Graphics and Photography Applications here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Educational Applications':
#                submenu_menu5(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Educational Applications here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Coding and Developer Applications':
#                submenu_menu6(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Coding and Developer Applications here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Social Media Applications':
#                submenu_menu7(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Social Media Applications here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Scientific Applications':
#                submenu_menu8(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Scientific Applications here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'System Applications':
#                submenu_menu9(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display System Applications here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Games':
#                submenu_menu10(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Games here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'General Utilities':
#                submenu_menu11(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display General Utilities here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Hacking Applications':
#                submenu_menu12(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Hacking Applications here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Emulators':
#                submenu_menu13(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Emulators here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Bittorrent Clients':
#                submenu_menu14(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Bittorrent Clients here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Downloader Clients':
#                submenu_menu15(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Downloader Clients here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Miscellaneous Applications':
#                submenu_menu16(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Miscellaneous Applications here")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == 'Full Install Section':
#                submenu_full_install_section(stdscr)
                stdscr.clear()
                stdscr.addstr(0, 0, "Display Full Install Section here")
                stdscr.refresh()
                stdscr.getch()

        print_menu(stdscr, current_row, menu) #, padding)

# Installation Tools
def install_tool(stdscr, tool, install_command):
    try:
        stdscr.clear()
        stdscr.addstr(0, 0, "Attempting to Install {} Please Wait...".format(tool))
        stdscr.refresh()

        process = subprocess.Popen(install_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            stdscr.addstr(1, 0, "{} has been installed successfully".format(tool))
        else:
            stdscr.addstr(1, 0, "Failed to install {}. Error: {}".format(tool, stderr.decode()))

    except Exception as e:
        stdscr.addstr(1, 0, "Failed to install {}: {}".format(tool, str(e)))

    stdscr.addstr(2, 0, "Press Enter to continue.")
    stdscr.refresh()
    stdscr.getch()

################################################################
################## INTERNET APPLICATIONS MENU ##################
############################# MENU1 ############################
################################################################

# 3 Columns print special menu 1
def print_menu_three_columns1(stdscr, selected_row_idx, menu, tool_descriptions_1, installed_packages):
    stdscr.clear()

# Multi-line ASCII art
    menu1_ascii_heading = """
  __  __ ___ ____   ____ _____ _     _        _    _   _ _____ ___  _   _ ____  
 |  \/  |_ _/ ___| / ___| ____| |   | |      / \  | \ | | ____/ _ \| | | / ___| 
 | |\/| || |\___ \| |   |  _| | |   | |     / _ \ |  \| |  _|| | | | | | \___ \ 
 | |  | || | ___) | |___| |___| |___| |___ / ___ \| |\  | |__| |_| | |_| |___) |
 |_|  |_|___|____/ \____|_____|_____|_____/_/   \_|_| \_|_____\___/ \___/|____/ 
  _____ ___   ___  _     ____  
 |_   _/ _ \ / _ \| |   / ___| 
   | || | | | | | | |   \___ \ 
   | || |_| | |_| | |___ ___) |
   |_| \___/ \___/|_____|____/ 
"""
    # ASCII heading
    ascii_heading_lines1 = menu1_ascii_heading.split('\n')
    h, w = stdscr.getmaxyx()
    max_rows = h * 3
    if len(menu) > max_rows:
        menu = menu[:max_rows-1] + ['...']

    column_width = max([len(item) for item in menu]) + 2
    total_width = column_width * 3
    total_height = len(menu) // 3 + (len(menu) % 3 > 0)
    start_x = (w - total_width) // 2
    start_y = (h - total_height) // 2
    start_y += int(h * 0.25)
    stdscr.attron(curses.color_pair(3))
    for i, line in enumerate(ascii_heading_lines1):
        if i < h:
            x = (w - len(line)) // 2
            stdscr.addstr(i, x, line)
    stdscr.attroff(curses.color_pair(3))
    h, w = stdscr.getmaxyx()
    max_rows = h * 3
    if len(menu) > max_rows:
        menu = menu[:max_rows-1] + ['...']

    column_width = max([len(item) for item in menu]) + 2
    total_width = column_width * 3
    total_height = len(menu) // 3 + (len(menu) % 3 > 0)
    start_x = (w - total_width) // 2
    start_y = (h - total_height) // 2

def print_menu_three_columns1(stdscr, selected_row_idx, menu, tool_descriptions_1, installed_packages):
    for idx, row in enumerate(menu):
        x = start_x + column_width * (idx % 3)
        y = start_y + idx // 3
        if 0 <= y < h and 0 <= x < w - len(row):
            is_installed = row in installed_packages
            if is_installed:
                stdscr.attron(curses.color_pair(2))
            if idx == selected_row_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, row)
            if idx == selected_row_idx:
                stdscr.attroff(curses.color_pair(1))
            if is_installed:
                stdscr.attroff(curses.color_pair(2))
# Corrected indentation of the following line
if menu[selected_row_idx] in tool_descriptions_1:
    description = tool_descriptions_1[menu[selected_row_idx]]
    stdscr.addstr(h-1, 0, description[:w-1])
stdscr.refresh()
####################################################################################################################

# Define the function to install a tool with spinner
def install_tool_with_spinner(stdscr, tool_name, install_command):
    stdscr.clear()
    message = f"Installing {tool_name}... Please wait..."
    stdscr.addstr(0, 0, message)
    stdscr.refresh()

    spinner_thread = threading.Thread(target=spin, args=(stdscr, 0, len(message) + 2,))
    spinner_thread.start()

    def run_and_output():
        process = subprocess.Popen(install_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        y = 1
        while process.poll() is None:
            reads = [process.stdout.fileno(), process.stderr.fileno()]
            ret = select.select(reads, [], [])

            for fd in ret[0]:
                if fd == process.stdout.fileno():
                    read = process.stdout.readline()
                if fd == process.stderr.fileno():
                    read = process.stderr.readline()
                if y >= stdscr.getmaxyx()[0] - 1:
                    break
                stdscr.addstr(y, 0, read.decode().rstrip())
                y += 1
                stdscr.refresh()

        return process.returncode

    output_thread = threading.Thread(target=run_and_output)
    output_thread.start()
    output_thread.join()

    spinner_thread.do_run = False
    spinner_thread.join()

    stdscr.addstr(stdscr.getyx()[0] + 1, 0, "Press Enter to continue.")
    stdscr.refresh()

    stdscr.nodelay(True)
    while True:
        key = stdscr.getch()
        if key == curses.KEY_ENTER or key in [10, 13]:
            break
    stdscr.nodelay(False)
    stdscr.clear()
    stdscr.refresh()


def submenu_menu1(stdscr):
    menu = ['Brave-Browser', 
            'Falkon-Browser', 
            'Microsoft-Edge-Browser', 
            'Chrome-Web-Browser', 
            'Chromium-Web-Browser', 
            'Libre-Wolf-Browser', 
            'Opera-Browser', 
            'Yandex-Browser', 
            'Waterfox-Browser', 
            'Go Back']
    current_row = 0
    print_menu_three_columns1(stdscr, current_row, menu, tool_descriptions_1, installed_packages)


    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu)-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if menu[current_row] == 'Go Back':
                break
            elif menu[current_row] == 'Brave-Browser':
                  install_tool_with_spinner(stdscr, 'Brave-Browser', 'flatpak install flathub com.brave.Browser')
            elif menu[current_row] == 'Falkon-Browser':
                  install_tool_with_spinner(stdscr, 'Falkon-Browser', 'flatpak install flathub org.kde.falkon')
            elif menu[current_row] == 'Microsoft-Edge-Browser':
                  install_tool_with_spinner(stdscr, 'Microsoft-Edge-Browser', 'flatpak install flathub com.microsoft.Edge')
            elif menu[current_row] == 'Chrome-Web-Browser':
                  install_tool_with_spinner(stdscr, 'Chrome-Web-Browser', 'flatpak install flathub com.google.Chrome')
            elif menu[current_row] == 'Chromium-Web-Browser':
                  install_tool_with_spinner(stdscr, 'Chromium-Web-Browser', 'flatpak install flathub org.chromium.Chromium')
            elif menu[current_row] == 'Libre-Wolf-Browser':
                  install_tool_with_spinner(stdscr, 'Libre-Wolf-Browser', 'flatpak install flathub io.gitlab.librewolf-community')
            elif menu[current_row] == 'Opera-Browser':
                  install_tool_with_spinner(stdscr, 'Opera-Browser', 'flatpak install flathub com.opera.Opera')
            elif menu[current_row] == 'Yandex-Browser':
                  install_tool_with_spinner(stdscr, 'Yandex-Browser', 'flatpak install flathub ru.yandex.Browser')
            elif menu[current_row] == 'Waterfox-Browser':
                  install_tool_with_spinner(stdscr, 'Waterfox-Browser', 'flatpak install flathub net.waterfox.waterfox')
            #elif menu[current_row] == 'metasploit':
            #      command = 'sudo sh -c \'cd "$(eval echo ~$(logname))/Downloads"; curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall; chmod 755 msfinstall; ./msfinstall\''
            #      install_tool_with_spinner(stdscr, 'metasploit', command)
                  subprocess.call(command, shell=True)


        print_menu_three_columns1(stdscr, current_row, menu, tool_descriptions_1, installed_packages)
return menu

    # Add this part to display the description of the selected tool
    if menu[selected_row_idx] in tool_descriptions_1:
        h, w = stdscr.getmaxyx()  # get the height and width of the window
        description_start_y = h - 6  # Calculate the start y position for the description

        for i in range(5):  # Clear up to 5 lines
            stdscr.addstr(description_start_y + i, 0, ' ' * (w-1))

        description_lines = wrap_text(tool_descriptions_1[menu[selected_row_idx]], w-1)
        for i, line in enumerate(description_lines[-5:], start=1):  # Display up to 5 lines from the end
            stdscr.addstr(description_start_y + i, 0, line)

# Word Wrap Definition
def wrap_text(text, width):
    return textwrap.wrap(text, width)

# Tool Descriptions
tool_descriptions_1 = {
    'Brave-Browser': 'Description for aaaaaaaaaaaaaaaaaaaaa Brave-Browser...aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'Falkon-Browser': 'Description for aaaaaaaaaaaaaaaaaaaaa Falkon-Browser...aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'Microsoft-Edge-Browser': 'Description for aaaaaaaaaaaaaaaaaaaaa Microsoft-Edge-Browser...aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'Chrome-Web-Browser': 'Description for aaaaaaaaaaaaaaaaaaaaa Chrome-Web-Browser...aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'Chromium-Web-Browser': 'Description for aaaaaaaaaaaaaaaaaaaaa Chromium-Web-Browser...aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'Libre-Wolf-Browser': 'Description for aaaaaaaaaaaaaaaaaaaaa Libre-Wolf-Browser...aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'Opera-Browser': 'Description for aaaaaaaaaaaaaaaaaaaaa Opera-Browser...aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'Yandex-Browser': 'Description for aaaaaaaaaaaaaaaaaaaaa Yandex-Browser...aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'Waterfox-Browser': 'Description for aaaaaaaaaaaaaaaaaaaaa Waterfox-Browser...aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    # Add more descriptions for other tools...
}
# Add this part to display the description of the selected tool
if menu[selected_row_idx] in tool_descriptions_1:
    description_lines = wrap_text(tool_descriptions_1[menu[selected_row_idx]], w-1)
    for i, line in enumerate(description_lines[-5:], start=1):  # Display up to 5 lines from the end
        stdscr.addstr(description_start_y + i, 0, line)

stdscr.refresh()





curses.wrapper(main)
# END OF CODE
