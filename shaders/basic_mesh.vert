// Request GLSL 3.3
#version 330

// Uniforms (AKA unchanging!) world transform and view-proj matrices
uniform mat4 uWorldTransform;
uniform mat4 uViewProj;

// Vertex attributes 
layout(location=0) in vec3 inPosition;
layout(location=1) in vec3 inNormal;
layout(location=2) in vec2 inTexCoord;

// Add texture coordinate as output
out vec2 fragTexCoord;

void main()
{
 // Convert position to homogeneous coordinates
 vec4 pos = vec4(inPosition, 1.0);

 // Outputs:
 // Transform position to world space, then clip space
 gl_Position = pos * uWorldTransform * uViewProj;
 // Pass texture coord. to frag shader
 fragTexCoord = inTexCoord; 
}