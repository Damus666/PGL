## [<- Back](PGL.md)

# Window

The window static class contains properties to manage the window.

- pixel_rect: `Rect` (read-only): A rect with topleft (0, 0) with the window dimentions in pixels.

- center: `Vec` (read-only): A vector representing the center of the window in pixels.

- size: `Vec`: Get or set the size of the window in pixels. The string "maximized" is allowed.

- position: `Vec`: Get or set the position of the window in pixels. The string "centered" is allowed.

- opacity: `float`

- title: `str`

- resizable, borderless: `bool`

- rect: `Rect` (read-only): The rectangle of the window with applied projection, useful for UI and text. This rect will only change when the window is resized

### `quit()`

Close the window and end the program.

# Camera

The camera static calss will move and scale all objects that don't use the UI shader.<br>
**NOTE**: the camera rect is updated automatically every frame, but if you modify the zoom during that frame it won't be updated but you can do that manually with the `refresh()` method.

- position: `Vec` (read-write)

- zoom: `float` (read-write): Must be > 0

- rect: `Rect` (read-only): A rect representing what the camera can see in the world.

- ui_mouse: `Vec` (read-only): The mouse position relative to the window rect (can be used for UI)

- world_mouse: `Vec` (read-only): The mouse position relative to the camera rect (can be used for world interaction)

- near_plane, far_plane: `float` (read-write)

### `screen_to_world(screen_pos: Vec) -> Vec`:

Convert any point from screen space to world space. You can only pass a vector to this function

### `screen_to_ui(screen_pos: Vec) -> Vec`:

Convert any point from screen space to UI space. You can only pass a vector to this function

# Time

the time static class has properties and method related to time

- fps_limit: `int` (read-write): The highest value the framerate can reach

- delta: `float` (read-only): How much time has passed since the last frame (in seconds)

- time: `float` (read-only): The time since the start of the game with scaling applied (in seconds)

- systime, syscounter: `float` (read-only): Access to `time.time()` and `time.perf_counter()`

- fps: `float` (read-only): The current framerate

- scale: `float` (read-write): The "speed" of the game

### `pause()`:

Set the scale to 0

### `unpause(new_scale = 1)`:

Set the scale to 1 or new_scale

# Binds

Static class that uses the binds from the setting and checks for input.<br>
`check_frame(name: str)` will check for continous input while `check_event(name: str)` will only check the frame the user presses/releases the key code.<br>
You can get the main and alts codes of a bind with the `get(name: str)` method.<br>
You can modify a bind using the `modify(name: str, main, *alts)` method.<br>
You can remove a bind using the `remove(name: str)` method or add a new bind with the `add(name: str, main, *atls)` method.<br>
**NOTE**: The main and alts arguments of the add and modify methods should be bind codes and should follow the same conventions explained in [config.json/"binds"](config.md)

# Frame

The frame static class contains read-only things from pygame that change every frame. <br>
The absolute time is in milliseconds and won't consider time scaling.<br>
The `valid` attribute flags if the game has started yet.
