// Request GLSL 3.3
#version 330

// Texture coordinate input from vertex shader
in vec2 fragTexCoord;
// This is output to color buffer
out vec4 outColor;
// For texture sampling [OpenGL sets this, because there only one texture!]
uniform sampler2D uTexture;

void main()
{
 // Sample color from texture
 outColor = texture(uTexture, fragTexCoord);
}