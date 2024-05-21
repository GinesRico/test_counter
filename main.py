import flet as ft
import sqlite3
import os

def main(page: ft.Page):
    page.title = "Ejercicios"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Ruta de la imagen
    #image_base_path = "C:/Users/gines/OneDrive/Documentos/Gym_App/Gym_App/assets"
    #bd_path = "C:/Users/gines/OneDrive/Documentos/Gym_App/Gym_App/assets/datos_ejercicios.db"

    # Conectar a la base de datos y crear la tabla de favoritos si no existe
    conn = sqlite3.connect(bd_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS favoritos (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    cursor.execute("SELECT DISTINCT bodyPart FROM datos")
    body_parts = cursor.fetchall()

    history = []

    def equipment_screen(e):
        body_part = e.control.data
        history.append("body_part")
        page.clean()
        eq = ft.GridView(expand=True, max_extent=150, child_aspect_ratio=1)
        page.add(eq)

        cursor.execute("SELECT DISTINCT equipment FROM datos WHERE bodyPart=?", (body_part,))
        equipments = cursor.fetchall()

        for equip in equipments:
            image_path = os.path.join(image_base_path, f"{body_part.lower()}.png")
            button = ft.ElevatedButton(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Image(src=image_path, fit=ft.ImageFit.COVER, width=100, height=100),
                            ft.Text(equip[0].upper())
                        ],
                        alignment=ft.alignment.center
                    ),
                    alignment=ft.alignment.center
                ),
                on_click=lambda e: exercise_screen(e, body_part),
                data=equip[0],
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
            )
            eq.controls.append(button)

        page.update()

    def exercise_screen(e, body_part):
        equipment = e.control.data
        history.append("equipment")
        page.clean()

        cursor.execute("SELECT name, gifUrl, instructions FROM datos WHERE bodyPart=? AND equipment=?", (body_part, equipment))
        ejercicios = cursor.fetchall()

        ejercicio_card = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.ALWAYS)

        def open_dlg(instructions):
            dlg = ft.AlertDialog(
                title=ft.Text("Instrucciones"),
                content=ft.Text(instructions),
                actions=[ft.TextButton("Cerrar", on_click=lambda _: page.dialog.close())]
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        def mark_favorite(name):
            cursor.execute("SELECT name FROM favoritos WHERE name=?", (name,))
            favorito = cursor.fetchone()
            if favorito:
                cursor.execute("DELETE FROM favoritos WHERE name=?", (name,))
                conn.commit()
                message = f"{name.title()} eliminado de favoritos"
            else:
                cursor.execute("INSERT INTO favoritos (name) VALUES (?)", (name,))
                conn.commit()
                message = f"{name.title()} añadido a favoritos"

            page.snack_bar = ft.SnackBar(content=ft.Text(message))
            page.snack_bar.open = True
            page.update()
            exercise_screen(e, body_part)

        for ejercicio in ejercicios:
            name, gifUrl, instructions = ejercicio

            cursor.execute("SELECT name FROM favoritos WHERE name=?", (name,))
            favorito = cursor.fetchone()
            favorite_icon = ft.icons.STAR if favorito else ft.icons.STAR_OUTLINE_OUTLINED

            card_content = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                title=ft.Text(name.upper()),
                                subtitle=ft.Image(src=gifUrl),
                            ),
                            ft.Row(
                                [
                                    ft.TextButton("Instrucciones", on_click=lambda e, inst=instructions: open_dlg(inst)),
                                    ft.IconButton(
                                        icon=favorite_icon,
                                        icon_size=20,
                                        tooltip="Favorito",
                                        on_click=lambda e, name=name: mark_favorite(name)
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ]
                    ),
                    padding=10,
                )
            )
            ejercicio_card.controls.append(card_content)

        page.add(ejercicio_card)

    def favorites_screen():
        page.clean()
        cursor.execute("SELECT name FROM favoritos")
        favoritos = cursor.fetchall()

        favorites_list = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.ALWAYS)

        for fav in favoritos:
            name = fav[0]
            cursor.execute("SELECT gifUrl, instructions FROM datos WHERE name=?", (name,))
            ejercicio = cursor.fetchone()
            if ejercicio:
                gifUrl, instructions = ejercicio

                def open_dlg(instructions):
                    dlg = ft.AlertDialog(
                        title=ft.Text("Instrucciones"),
                        content=ft.Text(instructions.capitalize()),
                        actions=[ft.TextButton("Cerrar", on_click=lambda _: page.dialog.close())]
                    )
                    page.dialog = dlg
                    dlg.open = True
                    page.update()

                def remove_favorite(name):
                    cursor.execute("DELETE FROM favoritos WHERE name=?", (name,))
                    conn.commit()
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"{name.title()} eliminado de favoritos"))
                    page.snack_bar.open = True
                    page.update()
                    favorites_screen()

                card_content = ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    title=ft.Text(name.upper()),
                                    subtitle=ft.Image(src=gifUrl),
                                ),
                                ft.Row(
                                    [
                                        ft.TextButton("Instrucciones", on_click=lambda e, inst=instructions: open_dlg(inst)),
                                        ft.IconButton(
                                            icon=ft.icons.STAR,
                                            icon_size=20,
                                            tooltip="Eliminar de favoritos",
                                            on_click=lambda e, name=name: remove_favorite(name)
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                            ]
                        ),
                        padding=10,
                    )
                )
                favorites_list.controls.append(card_content)

        page.add(favorites_list)

    def go_back(e):
        if history:
            last_action = history.pop()
            if last_action == "equipment":
                body_screen()
            elif last_action == "body_part":
                home()

    def home():
        page.add(
            ft.Image(src="icon.png", height=400),
            ft.Container(padding=20),
            ft.Text("Bienvenido!"),
            ft.Container(padding=20),
            ft.Container(padding=20),
        )

    def body_screen():
        bp = ft.GridView(expand=True, max_extent=150, child_aspect_ratio=1)
        page.add(bp)

        cursor.execute("SELECT DISTINCT bodyPart FROM datos")
        body_parts = cursor.fetchall()

        for body_part in body_parts:
            image_path = os.path.join(image_base_path, f"{body_part[0].lower()}.png")
            button = ft.ElevatedButton(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Image(src=image_path, fit=ft.ImageFit.COVER, width=100, height=100),
                            ft.Text(body_part[0].upper())
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                ),
                on_click=equipment_screen,
                data=body_part[0],
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
            )
            bp.controls.append(button)
        page.update()

    def nav_change(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            page.clean()
            home()
        elif selected_index == 1:
            page.clean()
            body_screen()
        elif selected_index == 2:
            page.clean()
            favorites_screen()
        elif selected_index == 3:
            page.clean()
            go_back(None)

    page.navigation_bar = ft.CupertinoNavigationBar(
        inactive_color=ft.colors.GREY,
        active_color=ft.colors.BLACK,
        on_change=nav_change,
        destinations=[
            ft.NavigationDestination(icon=ft.icons.EXPLORE, label="Inicio"),
            ft.NavigationDestination(icon=ft.icons.SPORTS_GYMNASTICS_ROUNDED, label="Ejercicios"),
            ft.NavigationDestination(icon=ft.icons.STAR, label="Favoritos"),
            ft.NavigationDestination(icon=ft.icons.ARROW_BACK, label="Atrás")
        ]
    )
    page.add(
        ft.Image(src="icon.png", height=400),
        ft.Container(padding=20),
        ft.Text("Bienvenido!"),
        ft.Container(padding=20),
        ft.Container(padding=20),
    )

    home()

ft.app(target=main, assets_dir="assets", view=ft.WEB_BROWSER)
