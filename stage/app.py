from shared import app_dir, df
from shiny import render
from shiny.express import input, ui

# Tell the browser to respect literal \n characters and force line breaks
ui.tags.style("""
    td {
        white-space: pre-wrap !important;
    }
""")


# Main content area - DataGrid
with ui.card(full_screen=True):
    ui.card_header("Complete Level Database")

    @render.data_frame
    def data_table():
        return render.DataGrid(df, filters=True, selection_mode="row")

with ui.card(id="my_card", full_screen=True):
    with ui.card_header(class_="d-flex justify-content-between align-items-center"):
        ui.h5("Selected Image")


    @render.ui
    def selected_image():
        # Get selection directly from the data_table object
        selection = data_table.cell_selection()

        # Dynamically check the reactive input for the card's fullscreen state
        isfullscreen = input.my_card_full_screen()

        if isfullscreen:
            style_str = "height: 100%; width: auto; max-width: none; image-rendering: pixelated;"
            div_class = "h-100 overflow-auto"
        else:
            # Regular styles: set a max height to prevent the tall box, keep aspect ratio, let div shrink
            style_str = "max-height: 250px; max-width: 100%; object-fit: contain;"  # Example constraint, adjust as desired
            div_class = "d-flex justify-content-center align-items-center overflow-hidden"  # Div adapts to constrained image

        # Apply logic inside the rendering (use penguin example context from your app.py)
        if selection is not None and len(selection.get("rows", [])) > 0:
            rows = selection["rows"]
            row_index = min(rows)

            # Find image URL for selected row in original dataframe (use existing logic/variable)
            if row_index < len(df):
                level_id = df.loc[row_index, 'Level_ID']
                image_filename = f"Level_{level_id}.png"
                return ui.div(
                    ui.img(
                        src=image_filename, # by default shiny search in www/ like for standard website
                        alt=f"Selected Image for Level {level_id}",
                        class_="img-fluid",
                        style=style_str  # Inline dynamic style
                    ),
                    class_=div_class
                )

        # Fallback UI if no row is selected, matching style class conditionally
        fallback_class = "d-flex justify-content-center align-items-center h-100 text-muted" if isfullscreen else "d-flex justify-content-center align-items-center text-muted"
        return ui.div(
            ui.p("Select an image to display."),  # Generic message for penguin example
            class_=fallback_class
        )