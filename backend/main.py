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
STATIC_VIDEO_PATH = "./static/"  # Ruta del video estático
OUTPUT_DIR = "./trimmed_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)
start_date = datetime(2024, 9, 2)
def get_date_by_weekday(target_weekday) -> datetime:
    # Convert datetime weekday (0-6, Monday is 0) to match Form weekday (1-7, Monday is 1)
    current_weekday = start_date.weekday() + 1
    
    # Calculate days to add
    days_to_add = (target_weekday - current_weekday) % 7
    
    return start_date + timedelta(days=days_to_add)


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


@app.post("/api/average")
async def compare_weekday_hours(
    weekday: int = Form(...),  # 1-7 where 1 is Monday
    end_time: float = Form(...),
    start_time: int = Form(...)
):
    try:
        print("entro antes de los average")
        fileName = get_date_by_weekday(weekday).strftime('%Y-%m-%d')
        output_filename = f"{fileName}_{start_time}:{end_time}.mp4"
        output_file_path = os.path.join(OUTPUT_DIR, output_filename)
        if os.path.exists(output_file_path):
            print("devuelvo el fichero")
            print(f"Devolviendo el archivo: {output_file_path} con nombre: {output_filename}")
            return FileResponse(output_file_path, media_type="video/mp4", filename=output_filename)

        
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, trim_video_with_ffmpeg,  f"./static/{fileName}_average.mp4", start_time, end_time, output_file_path)

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

@app.post("/api/trim-video")
async def trim_video(
    start_time: float = Form(...),  # Tiempo de inicio en segundos
    end_time: float = Form(...),
    september_date: datetime = Form(...)
              # Tiempo de fin en segundos
):
    try:
        fileName=september_date.strftime('%Y-%m-%d')
        print("entro antes de los files")
        output_filename = f"{fileName}_{start_time}:{end_time}.mp4"
        output_file_path = os.path.join(OUTPUT_DIR, output_filename)
        if os.path.exists(output_file_path):
            
            return FileResponse(output_file_path, media_type="video/mp4", filename=output_filename)

        
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, trim_video_with_ffmpeg, f"./static/{fileName}.mp4", start_time, end_time, output_file_path)


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
