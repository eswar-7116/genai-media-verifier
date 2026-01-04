"use client";
import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { cn } from "@/lib/utils";

const AnoAI = ({ className }: { className?: string }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [shouldRender, setShouldRender] = useState(true);
    const rafIdRef = useRef<number>();
    const lastFrameTime = useRef(Date.now());

    useEffect(() => {
        // Performance check - disable on mobile or low-end devices
        if (window.innerWidth < 768) {
            setShouldRender(false);
            return;
        }

        const container = containerRef.current;
        if (!container || !shouldRender) return;

        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
        const renderer = new THREE.WebGLRenderer({ 
            antialias: false, // Disabled for performance
            alpha: true,
            powerPreference: "low-power" // Request low-power mode
        });

        const width = container.offsetWidth;
        const height = container.offsetHeight;

        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5)); // Cap pixel ratio
        container.appendChild(renderer.domElement);

        const material = new THREE.ShaderMaterial({
            uniforms: {
                iTime: { value: 0 },
                iResolution: { value: new THREE.Vector2(width, height) }
            },
            vertexShader: `
                void main() {
                    gl_Position = vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform float iTime;
                uniform vec2 iResolution;

                #define NUM_OCTAVES 2  // Reduced from 3

                float rand(vec2 n) {
                    return fract(sin(dot(n, vec2(12.9898, 4.1414))) * 43758.5453);
                }

                float noise(vec2 p) {
                    vec2 ip = floor(p);
                    vec2 u = fract(p);
                    u = u*u*(3.0-2.0*u);

                    float res = mix(
                        mix(rand(ip), rand(ip + vec2(1.0, 0.0)), u.x),
                        mix(rand(ip + vec2(0.0, 1.0)), rand(ip + vec2(1.0, 1.0)), u.x), u.y);
                    return res * res;
                }

                float fbm(vec2 x) {
                    float v = 0.0;
                    float a = 0.3;
                    vec2 shift = vec2(100);
                    mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
                    for (int i = 0; i < NUM_OCTAVES; ++i) {
                        v += a * noise(x);
                        x = rot * x * 2.0 + shift;
                        a *= 0.4;
                    }
                    return v;
                }

                void main() {
                    vec2 shake = vec2(sin(iTime * 1.2) * 0.003, cos(iTime * 2.1) * 0.003); // Reduced shake
                    vec2 p = ((gl_FragCoord.xy + shake * iResolution.xy) - iResolution.xy * 0.5) / iResolution.y * mat2(6.0, -4.0, 4.0, 6.0);
                    vec2 v;
                    vec4 o = vec4(0.0);

                    float f = 2.0 + fbm(p + vec2(iTime * 3.0, 0.0)) * 0.5; // Reduced time multiplier

                    // Reduced iterations from 35 to 20 for better performance
                    for (float i = 0.0; i < 20.0; i++) {
                        v = p + cos(i * i + (iTime + p.x * 0.08) * 0.02 + i * vec2(13.0, 11.0)) * 3.5 + vec2(sin(iTime * 2.0 + i) * 0.002, cos(iTime * 2.5 - i) * 0.002);
                        float tailNoise = fbm(v + vec2(iTime * 0.3, i)) * 0.3 * (1.0 - (i / 20.0));
                        vec4 auroraColors = vec4(
                            0.1 + 0.3 * sin(i * 0.2 + iTime * 0.4),
                            0.3 + 0.5 * cos(i * 0.3 + iTime * 0.5),
                            0.7 + 0.3 * sin(i * 0.4 + iTime * 0.3),
                            1.0
                        );
                        vec4 currentContribution = auroraColors * exp(sin(i * i + iTime * 0.8)) / length(max(v, vec2(v.x * f * 0.015, v.y * 1.5)));
                        float thinnessFactor = smoothstep(0.0, 1.0, i / 20.0) * 0.6;
                        o += currentContribution * (1.0 + tailNoise * 0.8) * thinnessFactor;
                    }

                    o = tanh(pow(o / 100.0, vec4(1.6)));
                    gl_FragColor = o * 1.5;
                }
            `
        });

        const geometry = new THREE.PlaneGeometry(2, 2);
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        const targetFPS = 30; // Target 30 FPS instead of 60
        const frameTime = 1000 / targetFPS;

        const animate = () => {
            const now = Date.now();
            const elapsed = now - lastFrameTime.current;

            // Only render if enough time has passed (throttle to 30 FPS)
            if (elapsed >= frameTime) {
                material.uniforms.iTime.value += 0.016;
                renderer.render(scene, camera);
                lastFrameTime.current = now - (elapsed % frameTime);
            }

            rafIdRef.current = requestAnimationFrame(animate);
        };
        animate();

        const handleResize = () => {
            if (!container) return;
            const newWidth = container.offsetWidth;
            const newHeight = container.offsetHeight;

            renderer.setSize(newWidth, newHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
            material.uniforms.iResolution.value.set(newWidth, newHeight);
        };
        window.addEventListener('resize', handleResize);

        return () => {
            if (rafIdRef.current) {
                cancelAnimationFrame(rafIdRef.current);
            }
            window.removeEventListener('resize', handleResize);
            if (container.contains(renderer.domElement)) {
                container.removeChild(renderer.domElement);
            }
            geometry.dispose();
            material.dispose();
            renderer.dispose();
        };
    }, [shouldRender]);

    if (!shouldRender) {
        // Fallback gradient for mobile/low-end devices
        return (
            <div 
                className={cn("absolute inset-0 z-0", className)}
                style={{
                    background: 'radial-gradient(ellipse at 50% 50%, rgba(30, 60, 120, 0.3) 0%, rgba(10, 20, 40, 0.2) 50%, transparent 100%)'
                }}
            />
        );
    }

    return (
        <div ref={containerRef} className={cn("absolute inset-0 z-0", className)} />
    );
};

export default AnoAI;
