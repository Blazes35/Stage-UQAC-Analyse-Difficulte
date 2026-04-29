from shared import app_dir, df_levels, df_logs
from shiny import render
from shiny.express import input, ui

# Injection du CSS pour le rendu des logs
ui.tags.style("""
    td {
        white-space: pre-wrap !important;
    }
""")

with ui.navset_card_pill(id="main_tabs"):
    # ONGLET 1 : Base des Niveaux (Inchangé)
    with ui.nav_panel("Base des Niveaux"):
        @render.data_frame
        def levels_table():
            return render.DataGrid(df_levels, filters=True, selection_mode="row")

    # ONGLET 2 : Logs Vidéos (Avec Filtrage)
    with ui.nav_panel("Logs Vidéos Détallés"):
        # Ajout des cases à cocher pour filtrer les types de données
        ui.input_checkbox_group(
            "log_types",
            "Filtrer les données :",
            choices={
                "Evenement": "Événements",
                "Mort": "Morts",
                "Changement Niveau": "Changements de Niveau"
            },
            selected=["Evenement", "Mort", "Changement Niveau"],
            inline=True
        )


        @render.data_frame
        def logs_table():
            # On filtre le DataFrame original selon les choix de l'utilisateur
            # input.log_types() renvoie une liste des valeurs cochées
            filtered_df = df_logs[df_logs["Type"].isin(input.log_types())]
            return render.DataGrid(filtered_df, filters=True, selection_mode="row")

# --- Section d'affichage de l'image ---
with ui.card(id="my_card", full_screen=True):
    ui.card_header("Carte du Niveau Sélectionné")


    @render.ui
    def selected_image():
        is_log_tab = input.main_tabs() == "Logs Vidéos Détallés"

        if is_log_tab:
            selection = logs_table.cell_selection()
            # TRÈS IMPORTANT : On doit appliquer le même filtre ici pour que
            # l'index de la ligne sélectionnée corresponde aux données affichées
            current_df = df_logs[df_logs["Type"].isin(input.log_types())].reset_index(drop=True)
            level_col = 'Niveau'
        else:
            selection = levels_table.cell_selection()
            current_df = df_levels
            level_col = 'Level'

        isfullscreen = input.my_card_full_screen()

        if selection and len(selection.get("rows", [])) > 0:
            row_index = min(selection["rows"])

            if row_index < len(current_df):
                lvl_val = current_df.loc[row_index, level_col]
                # Nettoyage des caractères Unicode pour le nom de fichier
                clean_lvl = str(lvl_val).replace('\xa0', ' ').replace('\u2011', '-')

                img_src = f"Level_{clean_lvl}.png"

                style = "height: 100%; width: auto; max-width: none; image-rendering: pixelated;" if isfullscreen else "max-height: 250px; width: auto;"

                return ui.div(
                    ui.img(src=img_src, style=style),
                    # FIX: Changed 'justify-content-center' to 'justify-content-start'
                    class_="d-flex justify-content-start align-items-center h-100 overflow-auto"
                )

        return ui.div("Sélectionnez une ligne pour voir la carte.", class_="text-muted p-4")