from __future__ import annotations
import OpenGL.GL as GL
import sdl2
import ctypes


class Shader:
    """
    This class encapsulates a shader.

    It creates vertex/frag shaders, combine, and link them into
    a final 'shader program'.
    """

    def __init__(self) -> None:
        # Store shader object IDs
        self._m_vertex_shader_id: ctypes.c_uint = ctypes.c_uint()
        self._m_frag_shader_id: ctypes.c_uint = ctypes.c_uint()
        self._m_shader_program_id: ctypes.c_uint = ctypes.c_uint()

    def delete(self) -> None:
        # TODO: Perhaps self.unload()? Currently unused
        raise NotImplementedError

    # Load vertex & frag shaders
    def load(self, vert_name: str, frag_name: str) -> bool:
        # Compile vertex & pixel shaders
        if (self._compile_shader(vert_name, GL.GL_VERTEX_SHADER, "vertex") == False
                or self._compile_shader(frag_name, GL.GL_FRAGMENT_SHADER, "frag") == False):
            return False

        # Link them together to create a 'shader program'
        self._m_shader_program_id = GL.glCreateProgram()
        GL.glAttachShader(self._m_shader_program_id, self._m_vertex_shader_id)
        GL.glAttachShader(self._m_shader_program_id, self._m_frag_shader_id)
        GL.glLinkProgram(self._m_shader_program_id)

        # Verify that program linked
        if not self._is_valid_program:
            return False
        return True

    def unload(self) -> None:
        # Delete shader program along with two other shaders
        GL.glDeleteProgram(self._m_shader_program_id)
        GL.glDeleteShader(self._m_vertex_shader_id)
        GL.glDeleteShader(self._m_frag_shader_id)

    # Sets active shader program
    def set_active(self) -> None:
        GL.glUseProgram(self._m_shader_program_id)

    def set_matrix_uniform(self, name: str, matrix: Matrix4) -> None:
        # Find uniform shader variable
        loc: GL.GLuint = GL.glGetUniformLocation(
            self._m_shader_program_id, name)

        # Send matrix data to uniform variable
        GL.glUniformMatrix4fv(
            loc,            # Uniform ID
            1,              # Num of matrices
            GL.GL_TRUE,     # Transpose [using row vecs]
            matrix.m_mat    # Pointer to matrix
        )

        # For Debugging: Seeing uniform's value
        # p = (ctypes.c_float * 12)()
        # p = ((ctypes.c_float * 4) * 4)()
        # GL.glGetUniformfv(self._m_shader_program_id, loc, p)
        # print(list(p[0]))

    # Compile specified shader, [TODO simplify this func.]
    def _compile_shader(self, file_name: str, shader_type: GL.GLenum, name: str) -> bool:
        if name == "vertex":
            # Open file
            source_file_obj = open(file_name, "r")
            if source_file_obj:
                # Read file to byte object
                source_byte_obj = source_file_obj.read().encode()
                source_file_obj.close()

                # Create a shader of specific type
                self._m_vertex_shader_id = GL.glCreateShader(shader_type)
                # Set a source code for this shader
                GL.glShaderSource(self._m_vertex_shader_id, source_byte_obj)
                # Try to compile this shader
                GL.glCompileShader(self._m_vertex_shader_id)

                if not self._is_compiled(self._m_vertex_shader_id):
                    sdl2.SDL_Log(b"Failed to compile shader: ", file_name)
                    return False
            else:
                sdl2.SDL_Log(b"Shader file not found: ", file_name)
                return False
            return True

        elif name == "frag":
            # Open file
            source_file_obj = open(file_name, "r")
            if source_file_obj:
                # Read file to byte object
                source_byte_obj = source_file_obj.read().encode()
                source_file_obj.close()

                # Create a shader of specific type
                self._m_frag_shader_id = GL.glCreateShader(shader_type)
                # Set a source code for this shader
                GL.glShaderSource(self._m_frag_shader_id, source_byte_obj)
                # Try to compile this shader
                GL.glCompileShader(self._m_frag_shader_id)

                if not self._is_compiled(self._m_frag_shader_id):
                    sdl2.SDL_Log(b"Failed to compile shader: ", file_name)
                    return False
            else:
                sdl2.SDL_Log(b"Shader file not found: ", file_name)
                return False

            return True
        else:
            raise NotImplementedError()

    # Test whether shader is compiled
    def _is_compiled(self, shader_id: ctypes.c_uint) -> bool:
        # Query compile status
        status: int = GL.glGetShaderiv(shader_id, GL.GL_COMPILE_STATUS)

        if status != GL.GL_TRUE:
            err = GL.glGetShaderInfoLog(shader_id)
            sdl2.SDL_Log(b"GLSL compile failed because: ", err)
            return False
        return True

    # Test whether shaders link
    def _is_valid_program(self) -> bool:
        # Query compile status
        status: int = GL.glGetProgramiv(self._m_shader_program_id,
                                        GL.GL_LINK_STATUS)

        if status != GL.GL_TRUE:
            err = GL.glGetProgramInfoLog(self._m_shader_program_id)
            sdl2.SDL_Log(b"GLSL link failed because: ", err)
            return False
        return True
