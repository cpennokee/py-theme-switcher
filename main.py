import json
import sys
import argparse
import os
import time
import re

def is_json_file(filepath):
    """
    Checks if the content of a file is a valid JSON document.

    Args:
        filepath (str): The path to the file.

    Returns:
        bool: True if the file contains valid JSON, False otherwise.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)  # Attempt to load the file content as JSON
        return True
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return False
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        return False
    except Exception as e: # Catch other potential errors during file reading
        print(f"An unexpected error occurred: {e}")
        return False

def verify_json_values(filepath):
    # function to make sure all necessary configuration variables exist in theme config
    # runs after is_json_file, so no need to verify json again
    
    # check to see that all values exist
    required_values = {"name","dpi","font","font-size","window-button-ordering-style","prefer-dark-theme","gtk-theme","sound-theme","icon-theme","cursor-theme","cursor-size","kde-global-theme","kde-splash","widget-style","kde-color-scheme","window-decoration-theme","kvantum-theme","qt-style","qt-dark-mode"}
    values_exist = True
    
    # loop through each value to ensure it exists
    for item in required_values:
        if data.get(item) is None:
            print(f"Value: {item} not specified in json file.")
            values_exist = False
    
    return values_exist

def update_xresources(data, dpi):
    # admittedly, this isn't really how i want to write this function, but I just want to make it work for now
    
    # cursor theme
    command='sed -i "s/^Xcursor.theme: .*/Xcursor.theme: {0}/" "$HOME/.Xresources"'.format(data['cursor-theme'])
    os.system(command)

    # cursor size
    command='sed -i "s/^Xcursor.size: .*/Xcursor.size: {0}/" "$HOME/.Xresources"'.format(data['cursor-size'])
    os.system(command)

    # dpi
    command='sed -i "s/^Xft.dpi: .*/Xft.dpi: {0}/" "$HOME/.Xresources"'.format(dpi)
    os.system(command)

    print(f"Finished updating xresources!")

def update_kde(data, dpi):

    # Update global theme
    command = 'lookandfeeltool -a {0}'.format(data['kde-global-theme'])
    os.system(command)

    # change color scheme
    command = 'kwriteconfig6 --file kdeglobals --group General --key ColorScheme {0}'.format(data['kde-color-scheme'])
    os.system(command)

    # change widget style
    command = 'kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle "{0}"'.format(data['widget-style'])
    os.system(command)

    # change icon theme
    command = 'kwriteconfig6 --file kdeglobals --group Icons --key Theme "{0}"'.format(data['icon-theme'])
    os.system(command)

    # change cursor theme
    command = 'kwriteconfig6 --file ~/.config/kcminputrc --group Mouse --key cursorTheme "{0}"'.format(data['cursor-theme'])
    os.system(command)

    # change cursor size
    command = "kwriteconfig6 --file ~/.config/kcminputrc --group Mouse --key cursorSize {0}".format(data['cursor-size'])
    os.system(command)

    # change splash theme
    command = "kwriteconfig6 --file ~/.config/ksplashrc --group KSplash --key Theme {0}".format(data['kde-splash'])
    os.system(command)

    # change sound theme
    command = "kwriteconfig6 --file kdeglobals --group Sounds --key Theme {0}".format(data['sound-theme'])
    os.system(command)
    
    # window decorations
    if "window-decoration-library" in data:
        command = "/usr/lib/kwin-applywindowdecoration __aurorae__svg__{0}".format(data['window-decoration-theme'])
    
        print(f"Finished updating KDE theme settings!")

def update_gnome(data, dpi):
    # command = f''.format()

    # overall theme
    command = 'gsettings set org.gnome.desktop.interface gtk-theme "{0}"'.format(data['gtk-theme'])
    os.system(command)

    # unsure exactly what this is. Leave at Adwaita
    command = 'gsettings set org.gnome.desktop.wm.preferences theme "{0}"'.format(data['window-decoration-theme'])
    os.system(command)

    # system font
    font = "{0}, {1}".format(data['font'], data['font-size'])
    command = 'gsettings set org.gnome.desktop.interface font-name "{0}"'.format(font)
    os.system(command)

    # prefer dark theme
    if bool(data['prefer-dark-theme']): 
        command = 'gsettings set org.gnome.desktop.interface color-scheme "prefer-dark"'
    else:
        command = 'gsettings set org.gnome.desktop.interface color-scheme "default"'
    os.system(command)
    
    # icon theme
    command = 'gsettings set org.gnome.desktop.interface icon-theme "{0}"'.format(data['icon-theme'])
    os.system(command)

    # cursor theme
    command = 'gsettings set org.gnome.desktop.interface cursor-theme "{0}"'.format(data['cursor-theme'])
    os.system(command)

    # cursor size (needed for gnome)
    command = 'gsettings set org.gnome.desktop.interface cursor-size "{0}"'.format(data['cursor-size'])
    os.system(command)

    # gnome shell
    command = 'gsettings set org.gnome.shell.extensions.user-theme name "{0}"'.format(data['gtk-theme'])
    os.system(command)

    # change window button ordering
    if data['window-button-ordering-style'] == "mac-os": 
        # use mac button ordering ( left side of window : close | minimize | maximize)
        command = "gsettings set org.gnome.desktop.wm.preferences button-layout 'close,minimize,maximize:'"
    else:
        # use windows button ordering by default ( right side of window : minimize | maximize | close)
        command = "gsettings set org.gnome.desktop.wm.preferences button-layout ':minimize,maximize,close'"

    os.system(command)
    
    print(f"Finished updating gnome theme settings")

def update_gtk_configs(data, dpi):
    # gtk-2.0
    # -------------------------------
    print(f"Updating GTK2.0 configs...")
    # gtk-theme-name
    command = 'sed -i "s/^gtk-theme-name=.*/gtk-theme-name={0}/" "$HOME/.gtkrc-2.0"'.format(data['gtk-theme'])
    os.system(command)
    # gtk-icon-theme-name
    command = 'sed -i "s/^gtk-icon-theme-name=.*/gtk-icon-theme-name={0}/" "$HOME/.gtkrc-2.0"'.format(data['icon-theme'])
    os.system(command)
    # gtk-font-name
    command = 'sed -i "s/^gtk-font-name=.*/gtk-font-name={0}, {1}/" "$HOME/.gtkrc-2.0"'.format(data['font'], data['font-size'])
    os.system(command)
    # gtk-cursor-theme-name
    command = 'sed -i "s/^gtk-cursor-theme-name=.*/gtk-cursor-theme-name={0}/" "$HOME/.gtkrc-2.0"'.format(data['cursor-theme'])
    os.system(command)
    # gtk-cursor-theme-size=30
    command = 'sed -i "s/^gtk-cursor-theme-size=.*/gtk-cursor-theme-size={0}/" "$HOME/.gtkrc-2.0"'.format(data['cursor-size'])
    os.system(command)

    # gtk-3.0
    # ------------------------------
    print(f"Updating GTK3 configs...")
    # dark theme?
    command = 'sed -i "s/^gtk-application-prefer-dark-theme=.*/gtk-application-prefer-dark-theme={0}/" "$HOME/.config/gtk-3.0/settings.ini"'.format(data['prefer-dark-theme'])
    os.system(command)
    # gtk-cursor-theme-name
    command = 'sed -i "s/^gtk-cursor-theme-name=.*/gtk-cursor-theme-name={0}/" "$HOME/.config/gtk-3.0/settings.ini"'.format(data['cursor-theme'])
    os.system(command)
    # gtk-cursor-theme-size
    command = 'sed -i "s/^gtk-cursor-theme-size=.*/gtk-cursor-theme-size={0}/" "$HOME/.config/gtk-3.0/settings.ini"'.format(data['cursor-size'])
    os.system(command)
    # gtk-font-name
    command = 'sed -i "s/^gtk-font-name=.*/gtk-font-name={0}, {1}/" "$HOME/.config/gtk-3.0/settings.ini"'.format(data['font'], data['font-size'])
    os.system(command)
    # gtk-icon-theme-name
    command = 'sed -i "s/^gtk-icon-theme-name=.*/gtk-icon-theme-name={0}/" "$HOME/.config/gtk-3.0/settings.ini"'.format(data['icon-theme'])
    os.system(command)
    # gtk-sound-theme-name
    command = 'sed -i "s/^gtk-sound-theme-name=.*/gtk-sound-theme-name={0}/" "$HOME/.config/gtk-3.0/settings.ini"'.format(data['sound-theme'])
    os.system(command)
    # gtk-theme-name
    command = 'sed -i "s/^gtk-theme-name=.*/gtk-theme-name={0}/" "$HOME/.config/gtk-3.0/settings.ini"'.format(data['gtk-theme'])
    os.system(command)
    # dpi
    command = 'sed -i "s/^gtk-xft-dpi=.*/gtk-xft-dpi={0}/" "$HOME/.config/gtk-3.0/settings.ini"'.format(dpi)
    os.system(command)

    # gtk-4.0
    # ------------------------------
    print(f"Updating GTK4 configs...")
    # dark theme?
    command = 'sed -i "s/^gtk-application-prefer-dark-theme=.*/gtk-application-prefer-dark-theme={0}/" "$HOME/.config/gtk-4.0/settings.ini"'.format(data['prefer-dark-theme'])
    os.system(command)
    # gtk-cursor-theme-name
    command = 'sed -i "s/^gtk-cursor-theme-name=.*/gtk-cursor-theme-name={0}/" "$HOME/.config/gtk-4.0/settings.ini"'.format(data['cursor-theme'])
    os.system(command)
    # gtk-cursor-theme-size
    command = 'sed -i "s/^gtk-cursor-theme-size=.*/gtk-cursor-theme-size={0}/" "$HOME/.config/gtk-4.0/settings.ini"'.format(data['cursor-size'])
    os.system(command)
    # gtk-font-name
    command = 'sed -i "s/^gtk-font-name=.*/gtk-font-name={0}, {1}/" "$HOME/.config/gtk-4.0/settings.ini"'.format(data['font'], data['font-size'])
    os.system(command)
    # gtk-icon-theme-name
    command = 'sed -i "s/^gtk-icon-theme-name=.*/gtk-icon-theme-name={0}/" "$HOME/.config/gtk-4.0/settings.ini"'.format(data['icon-theme'])
    os.system(command)
    # gtk-sound-theme-name
    command = 'sed -i "s/^gtk-sound-theme-name=.*/gtk-sound-theme-name={0}/" "$HOME/.config/gtk-4.0/settings.ini"'.format(data['sound-theme'])
    os.system(command)
    # gtk-theme-name
    command = 'sed -i "s/^gtk-theme-name=.*/gtk-theme-name={0}/" "$HOME/.config/gtk-4.0/settings.ini"'.format(data['gtk-theme'])
    os.system(command)
    # dpi
    command = 'sed -i "s/^gtk-xft-dpi=.*/gtk-xft-dpi={0}/" "$HOME/.config/gtk-4.0/settings.ini"'.format(dpi)
    os.system(command)
    
    print(f"Finished updating GTK configs.")

def update_qt(data, dpi):
    # Change QT Settings
    if data['prefer-dark-theme'] == "true":
        print("Dark theme is preferred. Enabling QT dark mode")
        # For this to work on it's own, you must make color_scheme_path=/usr/share/qt5ct/colors/darker.conf in both files.
        command = 'sed -i "s/^custom_palette=.*/custom_palette=true/" "$HOME/.config/qt5ct/qt5ct.conf"'
        os.system(command)
        command = 'sed -i "s/^custom_palette=.*/custom_palette=true/" "$HOME/.config/qt6ct/qt6ct.conf"'
        os.system(command)
    else:
        print("Light theme is preferred. Enabling QT light mode")
        command = 'sed -i "s/^custom_palette=.*/custom_palette=false/" "$HOME/.config/qt5ct/qt5ct.conf"'
        os.system(command)
        command = 'sed -i "s/^custom_palette=.*/custom_palette=false/" "$HOME/.config/qt6ct/qt6ct.conf"'
        os.system(command)

    # change qt icons
    command = 'sed -i "s/^icon_theme=.*/icon_theme={0}/" "$HOME/.config/qt5ct/qt5ct.conf"'.format(data['icon-theme'])
    os.system(command)
    command = 'sed -i "s/^icon_theme=.*/icon_theme={0}/" "$HOME/.config/qt6ct/qt6ct.conf"'.format(data['icon-theme'])
    os.system(command)
    
    # change qt style
    command = 'sed -i "s/^style=.*/style={0}/" "$HOME/.config/qt5ct/qt5ct.conf"'.format(data['qt-style'])
    os.system(command)
    command = 'sed -i "s/^style=.*/style={0}/" "$HOME/.config/qt6ct/qt6ct.conf"'.format(data['qt-style'])
    os.system(command)
    
    # change qt5 fonts
    command = "sed -i 's/^fixed=.*/fixed=\"{0},{1},-1,5,50,0,0,0,0,0,Regular\"/' $HOME/.config/qt5ct/qt5ct.conf".format(data['font'], data['font-size'])
    os.system(command)
    command = "sed -i 's/^general=.*/general=\"{0},{1},-1,5,50,0,0,0,0,0,Regular\"/' $HOME/.config/qt5ct/qt5ct.conf".format(data['font'], data['font-size'])
    os.system(command)
    
    # change qt6 fonts
    command = "sed -i 's/^fixed=.*/fixed=\"{0},{1},-1,5,50,0,0,0,0,0,Regular\"/' $HOME/.config/qt6ct/qt6ct.conf".format(data['font'], data['font-size'])
    os.system(command)
    command = "sed -i 's/^general=.*/general=\"{0},{1},-1,5,50,0,0,0,0,0,Regular\"/' $HOME/.config/qt6ct/qt6ct.conf".format(data['font'], data['font-size'])
    os.system(command)

    # Change kvantum theme
    command = "kvantummanager --set {0}".format(data['kvantum-theme'])
    os.system(command)
    
    print(f"Updated QT config!")

if len(sys.argv) > 1 and is_json_file(sys.argv[1]):
    filepath = sys.argv[1]
    
    # Open the JSON file in read mode ('r')
    with open(filepath, 'r') as file:
        # Use json.load() to deserialize the JSON data into a Python object
        data = json.load(file)
        
        # make sure all necessary values exist before proceeding
        if not verify_json_values(file):
            print("JSON file is not valid.")
            print("Exiting...")
            sys.exit() # Exits the program
        
        # Echo theme name
        print(f"Applying theme: {data['name']}")

        # do any necessary calculations to get in expected format
        dpi = int(data['dpi']) * 96
        gtk_dpi = dpi * 1024

        # Start applying the changes to the file via bash commands

        #########################
        ### Change XResources ###
        #########################
        update_xresources(data, dpi)

        #################################
        ### Change KDE Theme Settings ###
        #################################
        update_kde(data, dpi)

        ###################################
        ### Change GNOME Theme Settings ###
        ###################################
        update_gnome(data, dpi)
        
        ###################################
        ### Change GTK Settings ###
        ###################################
        update_gtk_configs(data, gtk_dpi)
        
        ###################################
        ### Change QT Settings ###
        ###################################
        update_qt(data, dpi)
        
        # reload xresources after applying changes
        os.system("xrdb $HOME/.Xresources")
