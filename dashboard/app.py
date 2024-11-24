# --------------------------------------------
# Import dependencies/Libraries
# --------------------------------------------

# From shiny, import just reactive and render
from shiny import reactive, render
# From shiny.express, import just ui and inputs if needed
from shiny.express import ui

import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
import palmerpenguins
from shinywidgets import render_plotly
from scipy import stats

# --------------------------------------------
# Import faicons to generate icons from text.
# --------------------------------------------

from faicons import icon_svg

# --------------------------------------------
# Shiny EXPRESS VERSION
# --------------------------------------------

# --------------------------------------------
# First, set a constant UPDATE INTERVAL for all live data
# Constants are defined in uppercase letters
# Use a type hint to make it clear that it's an integer (: int)
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 10

# --------------------------------------------
# Define REACTIVE VALUEs with a common data structure
# The reactive values are used to hold or store live data. (information)
# Used by all the display components that show this live data.
# Reactive value is a wrapper around a DEQUE of readings
# Reactive value keeps track of data stored in deque.
# --------------------------------------------

DEQUE_SIZE: int = 5
DEQUE_SIZE_TWO: int = 10
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))
reactive_value_wrapper_two = reactive.value(deque(maxlen=DEQUE_SIZE_TWO))

# --------------------------------------------
# Initialize a REACTIVE CALC that all display components can call
# to get the latest data and display it.
# The calculation is invalidated every UPDATE_INTERVAL_SECS
# to trigger updates.
# It returns a defined data structure with everything needed to display the data.
# Very easy to expand or modify.
# --------------------------------------------

@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic
    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple with everything we need
    # Every time we call this function, we'll get all these values
    return deque_snapshot, df, latest_dictionary_entry


def reactive_calc_generate():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    ##############################
    # Get dataset to be presented and load into pandas dataframe
    ###############################
    # Dataset Description
    ###############################
    # species: penguin species (Chinstrap, Adelie, or Gentoo)
    # island: island name (Dream, Torgersen, or Biscoe) in the Palmer Archipelago
    # bill_length_mm: length of the bill in millimeters
    # bill_depth_mm: depth of the bill in millimeters
    # flipper_length_mm: length of the flipper in millimeters
    # body_mass_g: body mass in grams
    # sex: MALE or FEMALE

    try:
        # Load the Palmer Penguins dataset
        penguins_df = palmerpenguins.load_penguins()
        print(penguins_df)
        
        # Generate random rows of penguins_df
        num_of_rows = 5
        new_random_rows = penguins_df.sample(n=num_of_rows)
        
        # Convert dataframe to dictionary
        new_random_rows_dict = new_random_rows.to_dict(orient='records')
        
        # Get the deque and append the new sample generated
        deque_snapshot = reactive_value_wrapper_two.get()  # Assuming this is a deque
        deque_snapshot.append(new_random_rows_dict)
        
        #  Deque is converted to DataFrame for display
        df = pd.DataFrame(deque_snapshot)
        
        # Ensure we have the right data types and handle any errors
        df = df.assign(
            species = df['species'].astype(str),island = df['island'].astype(str),
            bill_length_mm = pd.to_numeric(df['bill_length_mm'], errors='coerce'),
            body_mass_g = pd.to_numeric(df['body_mass_g'], errors='coerce'),
            bill_depth_mm = pd.to_numeric(df['bill_depth_mm'], errors='coerce'),
            flipper_length_mm = pd.to_numeric(df['flipper_length_mm'], errors='coerce'),
            sex = df['sex'].astype(str)
        )
        
        
        # Get the latest dictionary entry
        latest_random_rows_dict = new_random_rows_dict
        
        # Return various data structure with everything we need
        return deque_snapshot, df, latest_random_rows_dict
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return [], pd.DataFrame(), []
    


# Define Web App user interface
# Call the ui.page_opts() function
# Set title to a string in quotes that will appear at the top
# Set fillable to True to use the whole page width for the UI
ui.page_opts(title="PyShiny Express: Palmer Penguins of Antarctica Dashboard", fillable=True)

# Sidebar is typically used for user interaction/information
# Note the with statement to create the sidebar followed by a colon
# Everything in the sidebar is indented consistently
with ui.sidebar(open="open"):
    ui.h2("Antarctica Explorer", class_="text-center")
    ui.p(
        "Real-time temperature readings in Antarctica and presentation of randomly selected\
        penguin data.",
        class_="text-center",
    )
    ui.hr()
    ui.h6("Links:")
    ui.a(
        "GitHub Repository",
        href="https://github.com/kwameape123/cintel-05-cintel",
        target="_blank",
    )
    ui.a(
        "GitHub App",
        href="https://kwameape123.github.io/cintel-05-cintel/",
        target="_blank",
    )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a(
        "PyShiny Express",
        href="https://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
    )

# In Shiny Express, everything not in the sidebar is in the main panel
# Tabs was included in the user interface to organize output
with ui.navset_pill(id="tab"): 
    with ui.nav_panel("Temperature"):
        with ui.layout_columns():
            with ui.value_box(

                showcase=icon_svg("thermometer"),
                theme="bg-gradient-green-purple",
            ):
                "Current Temperature"

                @render.text
                def display_temp():
                    """Get the latest reading and return a temperature string"""
                    deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
                    return f"{latest_dictionary_entry['temp']} C"

                "warmer than usual"

        with ui.card(full_screen=True):
            ui.card_header("Current Date and Time")

            @render.text
            def display_time():
                """Get the latest reading and return a timestamp string"""
                deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
                return f"{latest_dictionary_entry['timestamp']}"

        with ui.card(full_screen=True):
            ui.card_header("Most Recent Readings")

            @render.data_frame
            def display_df():
                """Get the latest reading and return a dataframe with current readings"""
                deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
                pd.set_option('display.width', None)        # Use maximum width
                return render.DataGrid(df, width="100%")

        with ui.card():
            ui.card_header("Chart with Current Trend")

            @render_plotly
            def display_plot():
                # Fetch from the reactive calc function
                deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

                # Ensure the DataFrame is not empty before plotting
                if not df.empty:
                    # Convert the 'timestamp' column to datetime for better plotting
                    df["timestamp"] = pd.to_datetime(df["timestamp"])

                    # Create scatter plot for readings
                    fig = px.scatter(df,
                                     x="timestamp",
                                     y="temp",
                                     title="Temperature Readings with Regression Line",
                                     labels={"temp": "Temperature (°C)", "timestamp": "Time"},
                                     color_discrete_sequence=["blue"])

                    # Linear regression
                    # For x let's generate a sequence of integers from 0 to len(df)
                    sequence = range(len(df))
                    x_vals = list(sequence)
                    y_vals = df["temp"]

                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
                    df['best_fit_line'] = [slope * x + intercept for x in x_vals]

                    # Add the regression line to the figure
                    fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

                    # Update layout as needed to customize further
                    fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")

                    return fig

    with ui.nav_panel("Palmer Penguin Data"):
        with ui.card(full_screen=True):
            ui.card_header("Penguin Data Table")
            penguins_df = palmerpenguins.load_penguins()
            @render.data_frame
            def display_df_one():
                 pd.set_option('display.width', None)
                 return render.DataGrid(penguins_df, width="100%")
              
        with ui.card(full_screen=True):
            ui.card_header("Random Penguin Data")     
            @render.data_frame
            def display_df_two():
                """Get the latest reading and return a dataframe with current readings"""
                deque_snapshot, df, latest_random_rows_dict = reactive_calc_generate()
                pd.set_option('display.width', None)        # Use maximum width
                return render.DataGrid(df, width="100%")

