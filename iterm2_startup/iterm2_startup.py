#!/usr/bin/env python3.7

# Import the iterm2 python module to provide an interface for communicating with iTerm
import iterm2
import os
import json

# Inputs:
window_config_file_path = os.path.join(os.path.dirname(__file__), "window_config.json")


def get_window_config():
    # Load the JSON configuration
    with open(window_config_file_path) as file:
        window_config = json.load(file)

    return window_config


# All the script logic goes in the main function.
# `connection` holds the link to a running iTerm2 process.
# `async` indicates that this function can be interrupted. This is required because iTerm2 communicates with the script over a websocket connection, any time the script sends/receives info from iterm2, it has to wait for a few milliseconds.
async def main(connection):
    # Get a reference to the iterm2.App object - a singleton that provides access to iTerm2’s windows, and in turn their tabs and sessions(panes).
    app = await iterm2.async_get_app(connection)

    # Fetch the “current terminal window” from the app (returns None if there is no current window)
    window = app.current_terminal_window
    if not window:
        window = await iterm2.Window.async_create(connection)
        # You can view this message in the script console.
        print("No current window. So created a new window")

    window_config = get_window_config()["window"]

    await window.async_set_title(window_config["name"])

    tab = None
    for tab_config in window_config["tabs"]:
        if not tab:
            tab = window.current_tab
        else:
            tab = await window.async_create_tab()

        await tab.async_set_title(tab_config["name"])

        pane = None
        for pane_index, pane_config in enumerate(tab_config["panes"]):
            if not pane:
                pane = tab.current_session
            elif pane_index == 3:
                pane = await tab_config["panes"][0]["pane_object"].async_split_pane(vertical=pane_config["is_vertical"])
            else:
                pane = await pane.async_split_pane(vertical=pane_config["is_vertical"])

            if pane_config.get("is_focus"):
                focus_pane_object = pane

            if len(tab_config["panes"]) == 4:
                pane_config["pane_object"] = pane

            for command in pane_config["commands"]:
                await pane.async_send_text(command + "\n")

            await pane.async_set_name(pane_config["name"])

    await focus_pane_object.async_activate(select_tab=True, order_window_front=True)


# Make a connection to iTerm2 and invoke the main function in an asyncio event loop.
# When main returns the program terminates.
iterm2.run_until_complete(main)
