import pygame
from tkinter import filedialog
import pgl
import os
import pathlib

try:
    raise ModuleNotFoundError
    # import mili
except (ModuleNotFoundError, ImportError):
    import pgl._mili as mili

S = 3
Z = 9999
OUTLINE = (60, 60, 70)


class PGLApp:
    def __init__(self):
        pygame.init()
        desktop_w, desktop_h = pygame.display.get_desktop_sizes()[0]
        self.win = pygame.Window(
            "PGL Projects", (desktop_w / 2, desktop_h / 2), resizable=True
        )
        self.clock = pygame.Clock()
        self.screen = self.win.get_surface()
        self.mili = mili.MILI(self.screen)
        self.mili.default_styles(
            rect={"border_radius": 0},
            line={"color": "white", "size": 1},
            text={"name": "Segoe UI", "sysfont": True},
        )
        self.list_Scroll = mili.ScrollHelper()
        self.error = None
        self.error_time = -Z * Z

    def ui_conditional_rect_bg(self, interaction):
        return mili.conditional_style(
            interaction,
            {"color": (35, 35, 45)},
            {"color": (55, 55, 65)},
            {"color": (19, 19, 24)},
        )

    def ui(self):
        with self.mili.begin(self.screen.get_rect()) as self.main_cont:
            self.mili.rect(
                {
                    "color": (25, 25, 30),
                }
            )

            self.ui_x()
            self.ui_main()

            if pygame.time.get_ticks() - self.error_time < 5000:
                self.mili.text_element(
                    f"{self.error}",
                    {
                        "size": 18,
                        "growy": True,
                        "wraplen": self.screen.width / 1.5,
                        "color": "red",
                        "align": "center",
                        "font_align": pygame.FONT_CENTER,
                    },
                    pygame.Rect(0, 0, self.screen.width, self.screen.height),
                    {"ignore_grid": True, "blocking": False},
                )

    def ui_main(self):
        self.mili.text_element(
            "PGL Projects",
            {"size": 25, "growy": True},
            (0, 0, 0, 0),
            {"fillx": True},
        )
        self.mili.line_element(
            (("-50", 0), ("50", 0)),
            {"size": 1, "color": (100, 100, 110)},
            (0, 0, 0, 20),
            {"fillx": True},
        )

        self.ui_set_dir()
        self.ui_projects()

    def ui_projects(self):
        with self.mili.begin(
            (0, 0, 0, 0), {"fillx": True, "resizey": True}, get_data=True
        ) as list_data:
            self.list_Scroll.update(list_data)

            projects_dir = pgl.get_projects_dir(False)
            if not os.path.exists(projects_dir):
                self.mili.text_element(
                    "The projects directory does not exist. Set a new one",
                    {"growx": True, "growy": True, "size": 20},
                    None,
                    {"align": "center"},
                )
                return

            projects = pgl.list_projects(False)
            if len(projects) <= 0:
                self.mili.text_element(
                    "No projects in directory yet",
                    {"growx": True, "growy": True, "size": 20},
                    None,
                    {"align": "center"},
                )

            for project_name in pgl.list_projects(False):
                self.ui_project(project_name, list_data.rect.w)

            self.ui_create_project()

    def ui_project(self, project, w):
        with self.mili.begin(
            (0, 0, w, 40),
            {
                "anchor": "last",
                "axis": "x",
                "align": "center",
                "offset": self.list_Scroll.get_offset(),
            },
        ) as data:
            self.mili.rect(self.ui_conditional_rect_bg(data))
            self.mili.text(f"{project}", {"size": 24})
            self.mili.text_element("sdadsa")

            if data.hovered:
                self.ui_popup("Build and run project", 18)
            if data.left_just_released:
                try:
                    pgl.build_project(project)
                    pgl.run_project(project)
                except pgl.PGLError as e:
                    self.error = e
                    self.error_time = pygame.time.get_ticks()

            if buildata := self.mili.element((0, 0, 35, 35), {"align": "center"}):
                self.mili.rect(self.ui_conditional_rect_bg(buildata))
                self.mili.circle({"color": "white", "padx": "20.5", "pady": "20.5"})
                if buildata.hovered:
                    self.ui_popup(
                        "Build project",
                    )
                if buildata.left_just_released:
                    try:
                        pgl.build_project(project)
                    except pgl.PGLError as e:
                        self.error = str(e)
                        self.error_time = pygame.time.get_ticks()

            if rundata := self.mili.element((0, 0, 35, 35), {"align": "center"}):
                self.mili.rect(self.ui_conditional_rect_bg(rundata))
                self.mili.polygon(
                    [("-25", "-25"), ("25", 0), ("-25", "25")], {"color": "white"}
                )
                if rundata.hovered:
                    self.ui_popup("Run project")
                if rundata.left_just_released:
                    try:
                        pgl.run_project(project)
                    except pgl.PGLError as e:
                        self.error = str(e)
                        self.error_time = pygame.time.get_ticks()

    def ui_popup(self, text, textsize=18):
        self.mili.basic_element(
            (pygame.mouse.get_pos(), (0, 35)),
            {
                "ignore_grid": True,
                "z": Z,
                "blocking": False,
                "parent_id": self.main_cont.id,
            },
            text,
            {"growx": True, "growy": True, "size": textsize},
            {"color": (35, 35, 45)},
            {"color": OUTLINE},
        )

    def ui_create_project(self):
        self.mili.element((0, 0, 10, S))
        if data := self.mili.element((0, 0, 35, 35), {"align": "center"}):
            self.mili.rect(self.ui_conditional_rect_bg(data))
            self.mili.text(
                "Create Project",
                {"color": "white", "size": 20, "growx": True, "growy": True},
            )
            if data.left_just_released:
                self.create_proj()

    def ui_set_dir(self):
        if data := self.mili.element(
            (S, S, 0, 35),
            {"ignore_grid": True, "z": Z},
        ):
            self.mili.rect(self.ui_conditional_rect_bg(data))
            self.mili.text("Set Dir", {"growx": True, "size": 20})

            if data.hovered:
                self.ui_popup(f"{pgl.get_projects_dir(False)}", 20)

            if data.left_just_released:
                self.set_directory()

    def set_directory(self):
        try:
            new_dir = filedialog.askdirectory()
            if not new_dir:
                return

            pgl.set_directory(new_dir)
        except Exception:
            pygame.display.message_box(
                "Filedialog Error",
                "Could not open tkinter filedialog, use the CLI equivalent for the same result (python pgl set_dir <path>)",
                "error",
                buttons=("Understood",),
            )

    def create_proj(self):
        try:
            proj_dir = filedialog.askdirectory()
            if not proj_dir:
                return

            path = pathlib.Path(proj_dir)
            try:
                pgl.create_project(path.stem)
            except pgl.PGLError as e:
                self.error = str(e)
                self.error_time = pygame.time.get_ticks()
        except Exception:
            pygame.display.message_box(
                "Filedialog Error",
                "Could not open tkinter filedialog, use the CLI equivalent for the same result (python pgl create <name>)",
                "error",
                buttons=("Understood",),
            )

    def ui_x(self):
        if data := self.mili.element(
            pygame.Rect(0, 0, 35, 35).move_to(topright=(self.screen.width - S, S)),
            {"ignore_grid": True, "z": Z},
        ):
            self.mili.rect(self.ui_conditional_rect_bg(data))
            self.mili.line((("-25", "-25"), ("25", "25")))
            self.mili.line((("-25", "25"), ("25", "-25")))

            if data.left_just_released:
                pygame.quit()
                raise SystemExit

    def run(self):
        while True:
            self.mili.start({"padx": 0, "pady": 0})
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            self.screen.fill(0)

            self.ui()
            self.mili.update_draw()

            self.win.flip()
            self.clock.tick()


def main():
    PGLApp().run()


if __name__ == "__main__":
    main()
