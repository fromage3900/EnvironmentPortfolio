o=op("/project1/starfield/resonance_rings")
o.par.resolutionw = 1280
o.par.resolutionh = 720
names = ["band1","band2","band3","band4","band5"]
chops = ["band1_analyze","band2_analyze","band3_analyze","band4_analyze","band5_analyze"]
for i,n in enumerate(names):
    o.par["const%iname"%i] = n
    o.par["const%ivalue"%i].expr = "op('/project1/audio/%s')['%s'][0]"%(chops[i], n)
glsl = '''
out vec4 fragColor;
uniform float band1;
uniform float band2;
uniform float band3;
uniform float band4;
uniform float band5;
uniform vec2 uTD2Dsize;

vec3 violet = vec3(0.70, 0.50, 1.00);
vec3 gold   = vec3(1.00, 0.85, 0.40);

float ringBand(vec2 uv, float radius, float thick, float amp){
    float d = distance(uv, vec2(0.5));
    float edge = smoothstep(radius-thick, radius, d) - smoothstep(radius, radius+thick, d);
    return edge * amp;
}

void main(){
    vec2 uv = gl_FragCoord.xy / uTD2Dsize;
    float b1 = clamp(band1,0.0,1.0);
    float b2 = clamp(band2,0.0,1.0);
    float b3 = clamp(band3,0.0,1.0);
    float b4 = clamp(band4,0.0,1.0);
    float b5 = clamp(band5,0.0,1.0);
    float r1 = 0.06 + b1*0.05;
    float r2 = 0.14 + b2*0.06;
    float r3 = 0.22 + b3*0.07;
    float r4 = 0.30 + b4*0.08;
    float r5 = 0.40 + b5*0.09;
    float t  = 0.012;
    float a1 = ringBand(uv, r1, t, b1*0.95);
    float a2 = ringBand(uv, r2, t, b2*0.9);
    float a3 = ringBand(uv, r3, t, b3*0.85);
    float a4 = ringBand(uv, r4, t, b4*0.8);
    float a5 = ringBand(uv, r5, t, b5*0.75);
    float a = max(max(max(max(a1,a2),a3),a4),a5);
    vec3 col = mix(violet, gold, b1*0.6);
    fragColor = vec4(col*a, a);
}
'''
op("/project1/starfield/resonance_rings_pixel").text = glsl
op("/project1/audio/_probe2").text = "configured"
