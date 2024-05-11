## [<- Back](PGL.md)

# Window

The window static class contains properties to manage the window.

<details>
<summary>Functionality</summary>

## pixel_rect: Rect (read-only)

A rect with topleft (0, 0) with the window dimentions in pixels.

## center: Vec (read-only)

A vector representing the center of the window in pixels.

## size: Vec (read-write)

Get or set the size of the window in pixels. The string "maximized" is allowed.

## title: str (read-write)

## resizable, borderless: bool (read-write)

## rect: Rect (read-only)

The rectangle of the window with applied projection, useful for UI and text. <br>
This rect will only change when the window is resized

## quit()

Close the window and end the program

</details>

# Camera

The camera static calss will move and scale all objects that don't use the UI shader.<br>
NOTE: the camera rect is updated automatically every frame, but if you modify the zoom during that frame it won't be updated but you can do that manually with the refresh method.

<details>
<summary>Functionality</summary>

## position: Vec (read-write)

## zoom: float (read-write)

The zoom of the camera. Must be > 0

## rect: Rect (read-only)

A rect representing what the camera can see in the world.

## ui_mouse: Vec (read-only)

The mouse position relative to the window rect (can be used for UI)

## world_mouse: Vec (read-only)

The mouse position relative to the camera rect (can be used for world interaction)

## near_plane, far_plane: float (read-write)

## screen_to_world(screen_pos: Vec) -> Vec

Convert any point from screen space to world space

## screen_to_ui(screen_pos: Vec) -> Vec

Convert any point from screen space to UI space

</details>

# Time

the time static class has properties and method related to time

<details>
<summary> Functionality </summary>

## fps_limit: int (read-write)

The highest value the framerate can reach

## delta: float (read-only)

How much time has passed since the last frame (in seconds)

## time: float (read-only)

The time since the start of the game with scaling applied (in seconds)

## systime, syscounter: float (read-only)

Access to time.time() and time.perf_counter()

## fps: float (read-only)

The current framerate

## scale: float (read-write)

The "speed" of the game

## pause()

Set the scale to 0

## unpause(new_scale = 1)

Set the scale to 1 or new_scale

</details>

# Binds

Static class that uses the binds from the setting and checks for input.<br>
`check_frame(name: str)` will check for continous input while `check_event(name: str)` will only check the frame the user presses/releases the key code.<br>
You can get and modify a bind using the `get(name: str)` method

# Frame

The frame static class contains read-only things from pygame that change every frame. The absolute time is in milliseconds and won't consider time scaling.<br>
The valid attribute flags if the game has started yet.
