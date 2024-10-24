from datetime import datetime,timedelta
import math
from fastapi import FastAPI, Form
import os
import subprocess
import asyncio
import uvicorn
from starlette.responses import FileResponse 
from fastapi.middleware.cors import CORSMiddleware  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://frontend:80"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Directorio donde está el video estático y donde se guardarán los videos recortados
STATIC_VIDEO_PATH = "./static/video.mp4"  # Ruta del video estático
OUTPUT_DIR = "./trimmed_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def trim_video_with_ffmpeg(input_file: str, start_time: float, end_time: float, output_file: str):
    # Ejecutar el comando ffmpeg para recortar el video, ajustar la resolución y calidad
    print("procesando video...")
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_file,              # Archivo de entrada (el video estático)
        "-ss", str(start_time),        # Tiempo de inicio
        "-to", str(end_time),
        "-c", "copy",          # Tiempo de final
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",  # Asegurar que la resolución sea divisible por 2
        "-r", "20",                    # Reducir los FPS a 15 para mejorar la velocidad
        "-c:v", "libx264",             # Usar el codec H.264 para la compresión
        "-preset", "ultrafast",        # Priorizar la velocidad
        "-crf", "30",                  # Ajustar el CRF para reducir la calidad                # Codec de audio AAC
        "-y",                          # Sobrescribir el archivo de salida si ya existe
        output_file                    # Archivo de salida
    ]

    print("ejecutando ffmpeg")
    subprocess.run(ffmpeg_cmd, check=True)


@app.post("/api/videos")
async def compare_weekday_hours(
    filename: str = Form(...)  # Se espera que se envíe un nombre de archivo
):  
    file_path = os.path.join(filename)  # Concatenar el nombre del archivo al directorio

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=os.path.basename(file_path))
    
    return {"error": "File not found"}, 404


@app.post("/api/comparison")
async def compare_weekday_hours(
    weekday: int = Form(...),  # 1-7 where 1 is Monday
    end_time: float = Form(...),
    start_time: int = Form(...)
):
    try:
        
        if not 1 <= weekday <= 7:
            return {"error": "Weekday must be between 1 and 7"}, 400

        python_weekday = weekday - 1

        september_dates = []
        start_date = datetime(2024, 9, 2)  # 2 de septiembre es lunes
        current_date = start_date

        count = 0

        while current_date.month == 9 and count < 4:
            if current_date.weekday() == python_weekday:
                september_dates.append(current_date.day)
                count += 1  # Incrementar el contador cuando se añade una fecha
            current_date += timedelta(days=1)




            # Corregido aquí
            
        # Check business hours based on weekday
        if weekday in [1, 2, 3, 4, 5]:  # Monday to Friday
            if not 7 <= (round(end_time/20)+7) <= 22:
                return {"error": "Hour must be between 7 and 22 for weekdays"}, 400
        else:  # Weekend
            if not 9 <= (round(end_time/20)+9) <= 20:
                return {"error": "Hour must be between 9 and 20 for weekends"}, 400
                
        # Calculate video segments for each date
        results = []
        for date in september_dates:
            try:
                output_filename = f"{date}_{start_time}:{end_time}.mp4"
                output_file_path = os.path.join(OUTPUT_DIR, output_filename)
                if os.path.exists(output_file_path):
                    results.append({
                    "date": date,
                    "start_second": start_time,
                    "end_second": end_time,
                    "outFile": output_file_path
                    })
                    continue
                        
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, trim_video_with_ffmpeg, STATIC_VIDEO_PATH, start_time, end_time, output_file_path)
                results.append({
                    "date": date,
                    "start_second": start_time,
                    "end_second": end_time,
                    "outFile": output_file_path
                })
            except Exception as e:
                results.append({
                    "date": date,
                    "error": str(e)
                })
                
        return {
            "weekday": weekday,
            "results": results
        }
        
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/api/trim-video")
async def trim_video(
    start_time: float = Form(...),  # Tiempo de inicio en segundos
    end_time: float = Form(...),
    september_date: int = Form(...)
              # Tiempo de fin en segundos
):
    try:
        # Generar un nombre único para el archivo de salida
        print("entro antes de los files")
        output_filename = f"{september_date}_{start_time}:{end_time}.mp4"
        output_file_path = os.path.join(OUTPUT_DIR, output_filename)
        if os.path.exists(output_file_path):
            print("devuelvo el fichero")
            print(f"Devolviendo el archivo: {output_file_path} con nombre: {output_filename}")
            return FileResponse(output_file_path, media_type="video/mp4", filename=output_filename)

        # Recortar el video usando ffmpeg (bloqueante)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, trim_video_with_ffmpeg, STATIC_VIDEO_PATH, start_time, end_time, output_file_path)


        print("devuelvo el fichero")
        print(f"Devolviendo el archivo: {output_file_path} con nombre: {output_filename}")
        return FileResponse(output_file_path, media_type="video/mp4", filename=output_filename)

    except subprocess.CalledProcessError as e:
        print("error")
        return {"error": f"ffmpeg failed: {e}"}, 404

    except Exception as e:
        print("error")
        print(e)
        return {"error": str(e)}, 500


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
