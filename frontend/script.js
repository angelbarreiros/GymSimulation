const videos = [
    document.getElementById('video-player-1'),
    document.getElementById('video-player-2'),
    document.getElementById('video-player-3'),
    document.getElementById('video-player-4')
];
document.getElementById('dailySubmitButton').addEventListener('click', async () => {
    const element=document.getElementById('daily-video-container')
    element.style.display='none'
    
    const formData = new FormData();
    xd =getRealFootageFromDate()
    console.log(xd)
    formData.append('start_time', xd.startSecond);
    formData.append('end_time', xd.endSecond);
    formData.append('september_date',xd.septemberDate)
    const spinner = document.getElementById('spinner');
    spinner.style.display='block'
    

    try {
        const response = await fetch('http://localhost/api/trim-video', {
            method: 'POST',
            body: formData,
            
        });
    
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Error: ${errorData.error}`);
        }
    
        const videoBlob = await response.blob();
        const videoUrl = URL.createObjectURL(videoBlob);
        console.log('Video URL:', videoUrl); // Imprimir la URL
    
        const videoPlayer = document.getElementById('dailyVideoPlayer');
        videoPlayer.src = videoUrl;
        videoPlayer.play();
    } catch (error) {
        console.error('Error recortando el video:', error);
        alert('Hubo un problema al recortar el video. Revisa la consola para más detalles.');
    }finally {
        spinner.style.display = 'none';
        element.style.display='block'
    }


    function getRealFootageFromDate(){
        const startDate =document.getElementById('startDate').value // Example: "2024-10-05"
        const date = new Date(startDate);
        const day = ('0' + date.getDate()).slice(-2);  // "05" for the 5th of the month

        
        const startTime =document.getElementById('startTime').value
        const endTime =document.getElementById('endTime').value
        if (!startDate  || !startTime || !endTime) {
            throw new Error('Por favor, complete todos los campos');
        }
        
        const start = new Date(`${startDate}T${startTime}`);
        
        
        const dayOfWeek = start.getDay();
        
        let openingHour, closingHour;
        if (dayOfWeek >= 1 && dayOfWeek <= 5) {  // Monday to Friday
            openingHour = 7;
            closingHour = 22;
        } else {  // Saturday and Sunday
            openingHour = 9;
            closingHour = 20;
        }
        const [startHour, startMinutes] = startTime.split(':').map(Number);
        const [endHour, endMinutes] = endTime.split(':').map(Number);
        if (startHour < openingHour || startHour >= closingHour ||
            endHour < openingHour || endHour > closingHour) {
            throw new Error(`Horario no válido. Horario de atención: ${
                dayOfWeek >= 1 && dayOfWeek <= 5 ? '7:00 - 22:00' : '9:00 - 20:00'
            }`);
        }
        const startSeconds = ((startHour - openingHour) * 20) + (startMinutes * 0.3333333333333333);
        const endSeconds = ((endHour - openingHour) * 20) + (endMinutes * 0.3333333333333333);
        
    
        return {
            startSecond: Number(startSeconds.toFixed(2)),
            endSecond: Number(endSeconds.toFixed(2)),
            duration: Number((endSeconds - startSeconds).toFixed(2)),
            septemberDate: day
        };
        

    }
    
});


const modeSwitch = document.getElementById('modeSwitch');
    const dailyMode = document.getElementById('dailyMode');
    const weeklyMode = document.getElementById('weeklyMode');
    const spinner = document.getElementById('spinner');
    const dailySubmitButton = document.getElementById('dailySubmitButton');
    const weeklySubmitButton = document.getElementById('weeklySubmitButton');
    const tvSubmitButton = document.getElementById('tvSubmitButton');

    modeSwitch.addEventListener('change', function() {
        if (this.checked) {
            dailyMode.style.display = 'none';
            weeklyMode.style.display = 'block';
            const vid =document.getElementById('dailyVideoPlayer')
            console.log(vid)
            vid.pause()
            
        } else {
            dailyMode.style.display = 'block';
            weeklyMode.style.display = 'none';
            for (vide of videos){
                console.log(vide)
                vide.pause()
            }
            
            
            
        }
    });
document.getElementById('weeklySubmitButton').addEventListener('click', async () => {
    const startTime = document.getElementById('weeklyTime').value; 
    const weekDay = document.getElementById('weekDay').value; 
    spinner.style.display = 'block';
    const xd =document.getElementById('video-grid')
    xd.style.display = 'none'
    

    
    let openingHour, closingHour;
    if (weekDay >= 1 && weekDay <= 5) {  // Monday to Friday
        openingHour = 7;
        closingHour = 21;
    } else {  // Saturday and Sunday
        openingHour = 9;
        closingHour = 19;
    }
    const [startHour, startMinutes] = startTime.split(':').map(Number);
    if (startHour < openingHour || startHour >= closingHour) {
        throw new Error(`Horario no válido. Horario de atención: ${
            weekDay >= 1 && weekDay <= 5 ? '7:00 - 22:00' : '9:00 - 20:00'
        }`);
    }
    const startSeconds = ((startHour - openingHour) * 20) + (startMinutes * 0.3333333333333333);
    const endSeconds = startSeconds + 20
    const formData = new FormData();
    formData.append('start_time', startSeconds);
    formData.append('end_time', endSeconds);
    formData.append('weekday',weekDay)
    const response = await fetch('http://localhost/api/comparison', {
        method: 'POST',
        body: formData
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Error: ${errorData.error}`);
    }
    let data = await response.json()
    
    for(file of data.results){
        const formData = new FormData();
        formData.append('filename', file.outFile);
        const responseVideo = await fetch('http://localhost/api/videos', {
            method: 'POST',
            body: formData
        });
        if (!responseVideo.ok) {
            const errorData = await responseVideo.json();
            throw new Error(`Error: ${errorData.error}`);
        }
        const videoBlob = await responseVideo.blob();
        const videoUrl = URL.createObjectURL(videoBlob);
        
        videos.forEach(video=>{
            video.src=videoUrl
        })

    }  
    spinner.style.display = 'none';
    xd.style.display = 'grid'

})

videos.forEach(video => {
    video.addEventListener('play', function() {
        const time = this.currentTime;
        videos.forEach(otherVideo => {
            if(otherVideo !== this) {
                otherVideo.currentTime = time;
                const playPromise = otherVideo.play();
                if (playPromise !== undefined) {
                    playPromise.catch(() => {});
                }
            }
        });
    });
    
    video.addEventListener('pause', function() {
        videos.forEach(otherVideo => {
            if(otherVideo !== this) {
                otherVideo.pause();
            }
        });
    });
    
    video.addEventListener('timeupdate', function() {
        videos.forEach(otherVideo => {
            if(otherVideo !== this && !otherVideo.paused) {
                if(Math.abs(otherVideo.currentTime - this.currentTime) > 0.5) {
                    otherVideo.currentTime = this.currentTime;
                }
            }
        });
    });
});