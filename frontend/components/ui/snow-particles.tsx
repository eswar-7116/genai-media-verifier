"use client";
import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

export const SnowParticles = ({
    className,
    quantity = 40,
}: {
    className?: string;
    quantity?: number;
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const canvasContainerRef = useRef<HTMLDivElement>(null);
    const context = useRef<CanvasRenderingContext2D | null>(null);
    const circles = useRef<any[]>([]);
    const rafID = useRef<number | null>(null);
    const [isVisible, setIsVisible] = useState(true);
    const lastFrameTime = useRef(Date.now());

    useEffect(() => {
        // Disable on mobile or low-end devices
        if (window.innerWidth < 768) {
            setIsVisible(false);
            return;
        }

        // Reduce quantity on smaller screens
        const adjustedQuantity = window.innerWidth < 1024 ? Math.min(quantity, 30) : quantity;

        if (canvasRef.current) {
            context.current = canvasRef.current.getContext("2d", {
                alpha: true,
                desynchronized: true, // Better performance
            });
        }
        initCanvas(adjustedQuantity);
        animate();

        const handleResize = () => {
            initCanvas(adjustedQuantity);
        };

        window.addEventListener("resize", handleResize);

        return () => {
            if (rafID.current) {
                cancelAnimationFrame(rafID.current);
            }
            window.removeEventListener("resize", handleResize);
        };
    }, [quantity]);

    const initCanvas = (adjustedQuantity: number) => {
        if (canvasContainerRef.current && canvasRef.current && context.current) {
            circles.current = [];
            canvasRef.current.width = canvasContainerRef.current.offsetWidth;
            canvasRef.current.height = canvasContainerRef.current.offsetHeight;

            for (let i = 0; i < adjustedQuantity; i++) {
                const x = Math.floor(Math.random() * canvasRef.current.width);
                const y = Math.floor(Math.random() * canvasRef.current.height);
                const dX = (Math.random() - 0.5) * 0.5;
                const dY = (Math.random() * 0.5) + 0.5;
                const size = Math.random() * 2 + 1;
                const alpha = Math.random() * 0.2 + 0.2;
                circles.current.push({ x, y, dX, dY, size, alpha });
            }
        }
    };

    const drawCircle = (x: number, y: number, size: number, alpha: number) => {
        if (context.current) {
            context.current.beginPath();
            context.current.arc(x, y, size, 0, 2 * Math.PI);
            context.current.fillStyle = `rgba(255, 255, 255, ${alpha})`;
            context.current.fill();
        }
    };

    const animate = () => {
        const now = Date.now();
        const elapsed = now - lastFrameTime.current;
        
        // Throttle to 30 FPS for better performance
        if (elapsed >= 33) { // ~30 FPS
            if (canvasRef.current && context.current) {
                context.current.clearRect(
                    0,
                    0,
                    canvasRef.current.width,
                    canvasRef.current.height
                );
                circles.current.forEach((circle: any) => {
                    circle.y += circle.dY;
                    circle.x += circle.dX;

                    if (circle.y > canvasRef.current!.height) {
                        circle.y = 0;
                        circle.x = Math.floor(Math.random() * canvasRef.current!.width);
                    }

                    if (circle.x > canvasRef.current!.width) circle.x = 0;
                    if (circle.x < 0) circle.x = canvasRef.current!.width;

                    drawCircle(circle.x, circle.y, circle.size, circle.alpha);
                });
            }
            lastFrameTime.current = now - (elapsed % 33);
        }
        
        rafID.current = requestAnimationFrame(animate);
    };

    if (!isVisible) {
        return null;
    }

    return (
        <div className={cn("absolute inset-0 pointer-events-none z-0", className)} ref={canvasContainerRef}>
            <canvas ref={canvasRef} className="w-full h-full" />
        </div>
    );
};
