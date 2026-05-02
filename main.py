# pyinstaller --onedir --icon="C:\Users\Krist\AppData\Local\lønix\logo.png" --name="Lønix" main.py



"""
Jeg vil gerne lige se hvordan det vil se ud med en professionelt GUI, lavet med PyQt.
Du skal nu lægge en plan for hvordan du kan konvertere HELT min program og alle funktionaliteter til at bruge PyQt5 med en pæn og professionelt GUI.
Herefter skal du udføre handlingen, og gøre det simpelt, brugervenligt og moderne.
Som output til mig skal du også komme med forslag til nyttige og praktiske ting og funktionaliter jeg kunne tilføje i programmet senere.
"""


import os

from colorama import Fore, Style, init

import functions as ft
import indberet
import loenberegner
import næste_udbetaling
import statistik
import udbetalinger

init()


def main():
    while True:
        ft.header("Hovedmenu")

        separator = ft.ui_line(22)
        print(Fore.LIGHTBLACK_EX + separator + Fore.LIGHTBLUE_EX)
        print("(1) Indberet")
        print("(2) Lønberegner")
        print("\n(3) Næste udbetaling")
        print("(4) udbetalinger")
        print("(5) Statistik" + Fore.RED)
        print("\n(0) Afslut")
        print(Fore.LIGHTBLACK_EX + separator)

        choice_main = input(Fore.WHITE + "\n\nVælg: " + Style.RESET_ALL).strip().lower()
        if choice_main not in ["0", "1", "2", "3", "4", "5"]:
            ft.error_message(sti="Hovedmenu", besked=None, ugyldigt_valg=True, sov=False, get_input=True)

        elif choice_main == "0":
            return

        elif choice_main == "1":
            indberet.main()

        elif choice_main == "2":
            loenberegner.main()

        elif choice_main == "3":
            næste_udbetaling.main()

        elif choice_main == "4":
            udbetalinger.main()

        elif choice_main == "5":
            statistik.main()


if __name__ == "__main__":
    try:
        if not os.path.exists("data"):
            os.mkdir("data")
        ft.load_data()
        ft.load_settings()
        main()
        ft.clear_terminal()
        print("Afslutter...")
    except Exception as error:
        ft.error_message(sti="Hovedmenu", besked=f"UKENDT FATAL FEJL:\n\n{error}", ugyldigt_valg=False, sov=False, get_input=False)
        input(Fore.LIGHTBLACK_EX + "\n\nTryk på enter for at lukke ned...")
        ft.clear_terminal()
