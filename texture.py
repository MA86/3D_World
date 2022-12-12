from __future__ import annotations
import OpenGL.GL as GL
import sdl2
import sdl2.sdlimage as sdlimage
import ctypes


class Texture:
    """
    This class uses SDL_Image library to load texture files for PyOpenGL.
    """

    def __init__(self) -> None:
        # OpenGL ID of texture
        self._m_texture_id: ctypes.c_uint = ctypes.c_uint(0)
        # Width/hegith of texture
        self._m_width: int = 0
        self._m_height: int = 0

    def delete(self) -> None:
        # TODO: Not used, perhaps self.unload()?
        pass

    def load(self, file_name: str) -> bool:
        # Python string -> C string (char*)
        file_name = ctypes.c_char_p(file_name.encode())

        # Load image from a file
        surface: sdl2.SDL_Surface = sdlimage.IMG_Load(file_name)
        if surface == None:
            sdl2.SDL_Log(b"Failed to load image file: ", file_name)
            return False

        format = GL.GL_RGB
        if surface.contents.format.contents.BytesPerPixel == 4:
            format = GL.GL_RGBA

        self._m_width = surface.contents.w
        self._m_height = surface.contents.h

        GL.glGenTextures(1, ctypes.byref(self._m_texture_id))
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._m_texture_id)

        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, format, surface.contents.w,
                        surface.contents.h, 0, format, GL.GL_UNSIGNED_BYTE, ctypes.c_char_p(surface.contents.pixels))

        # Free image data
        sdl2.SDL_FreeSurface(surface)

        # Enable bilinear filtering
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        return True

    def unload(self) -> None:
        GL.glDeleteTextures(1, self._m_texture_id)

    def set_active(self) -> None:
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._m_texture_id)

    def get_width(self) -> int:
        return self._m_width

    def get_height(self) -> int:
        return self._m_height
