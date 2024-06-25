## [<- Back](PGL.md)

# Timer

Handy class to call a function after some amount of time. If your function returns true the timer will be restarted. You can start it manually with the `start()` method.

# NoiseSettings

You need the noise module to use this. Freeze noise settings and switch between noise functions using the type parameter. <br>
The type should be used with the constants `NOISE_...`<br>
The activation is needed for the check, and you can check for <= or >= with the `NOISE_LT` and `NOISE_GT` constants.<br>
The `get()` method returns the noise value while the `check()` method applies the activation and returns a boolean.<br>
Both functions expect a float for 1D, a sequence of 2 floats for 2D and a sequence of 3 floats for 3D.

# Animation

An helper class to update values over time with different easings. Animations are updated automatically. you can start and stop them with the methods. When an animation ends a custom function can be called (use `functools.partial` to use parameters with it).

The value type can be `ANIMTYPE_NUMBER` to animate a number (`0.5`->`2.3`), `ANIMTYPE_COLOR` to animate a `pygame.Color` (green->blue) (note that you'll need to convert it back with `from_pg_color`), `ANIMTYPE_SEQUENCE` to animate all values of a sequence, useful for size or position (`(0.4, 0.8)`->`(0.2, 1.4)`).

Easings should be an object of type _Ease, so all classes that start with Ease like `EaseLinear` or `EaseIn`. Don't forget to instantiate the class.

## frange(start: float, stop: float, step: float)
Works exactly like the built-in range function but all the arguments can and should be floating point numbers.

## from_pg_color(color: pygame_ColorValue, alpha: bool = True)

It's an extra utility function that converts a pygame color value (string, tuple or Color object) to a color tuple that you can use with PGL. The alpha argument decides whether the color should have 3 of 4 components.
