@echo off
echo ========================================
echo Starting Cloudflared with Extended Timeout
echo ========================================
echo.

REM Start cloudflared in background and capture output
echo Starting cloudflared tunnel...
start /B cloudflared tunnel --url http://localhost:8000 --proxy-connect-timeout 300s --proxy-tcp-keepalive 30s --no-chunked-encoding > cloudflared_output.txt 2>&1

REM Wait for URL to be generated
echo Waiting for tunnel URL...
timeout /t 5 /nobreak > nul

REM Extract URL from output (you'll need to update this manually)
echo.
echo ========================================
echo CHECK cloudflared_output.txt FOR YOUR URL
echo ========================================
echo.
echo Copy the URL that looks like:
echo https://something-random.trycloudflare.com
echo.
echo Then update:
echo 1. frontend\.env.local
echo 2. backend\.env (CORS_ORIGINS)
echo 3. Vercel environment variables
echo.

pause
