## [<- Back](PGL.md)

# Timer

Handy class to call a function after some amount of time. If your function returns true the timer will be restarted. You can start it manually with the `start()` method

# NoiseSettings

You need the noise module to use this. Freeze noise settings and switch between noise functions using the type parameter. <br>
The type should be used with the constants NOISE\_...<br>
The activation is needed for the check, and you can check for <= or >= with the NOISE_LT and NOISE_GT constants.<br>
The get() method returns the noise value while the check() method applies the activation and returns a boolean.<br>
Both functions expect a float for 1D, a sequence of 2 floats for 2D and a sequence of 3 floats for 3D.

## from_pg_color(color: pygame_ColorValue, alpha: bool = True)

It's an extra utility function that converts a pygame color value (string, tuple or Color object) to a color tuple that you can use with PGL. The alpha argument decides whether the color should have 3 of 4 components.
