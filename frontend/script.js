const videos = [
    document.getElementById('video-player-1'),
];
document.getElementById('dailySubmitButton').addEventListener('click', async () => {
    
    const videoPlayer = document.getElementById('dailyVideoPlayer');
    const spinner = document.getElementById('spinner');
    
    // Hide the video player and show the spinner
    videoPlayer.style.display = 'none';
    spinner.style.display = 'block';

    const formData = new FormData();
    
    try {
        const timeInfo = getRealFootageFromDate();
        console.log(timeInfo);
        
        // Convert to types expected by Python backend
        formData.append('start_time', timeInfo.startTime);
        formData.append('end_time', timeInfo.endSecond);
        formData.append('september_date', timeInfo.septemberDay);
        
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
        console.log('Video URL:', videoUrl);
        
        videoPlayer.src = videoUrl;
        videoPlayer.load(); // Ensure the video source is loaded
        
        // Show the video player and hide the spinner
        videoPlayer.style.display = 'block';
        spinner.style.display = 'none';
        
        videoPlayer.play();
        
    } catch (error) {
        console.error('Error recortando el video:', error);
        alert('Hubo un problema al recortar el video. Revisa la consola para más detalles.');
        
        // In case of error, show the video player (with its previous content) and hide the spinner
        videoPlayer.style.display = 'block';
        spinner.style.display = 'none';
    }
});
function getRealFootageFromDate() {
    const startDate = document.getElementById('startDate').value;
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;
    
    if (!startDate || !startTime || !endTime) {
        throw new Error('Por favor, complete todos los campos');
    }
    
    const startDateTime = new Date(`${startDate}T${startTime}`).toISOString();
    const startDateObject = new Date(startDateTime);
    const dayOfWeek = startDateObject.getDay();
    
    let openingHour, closingHour;
    if (dayOfWeek >= 1 && dayOfWeek <= 5) { // Monday to Friday
        openingHour = 7;
        closingHour = 22;
    } else { // Saturday and Sunday
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
        startTime: startSeconds, // Returns as Date object, will be converted to ISO string when sending
        endSecond: Number(endSeconds.toFixed(2)), // Returns as float
        septemberDay: startDateObject.toISOString() // Returns as integer
    };
}


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
    const response = await fetch('http://localhost/api/average', {
        method: 'POST',
        body: formData
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Error: ${errorData.error}`);
    }
    const videoBlob = await response.blob();
    const videoUrl = URL.createObjectURL(videoBlob);
    console.log('Video URL:', videoUrl); // Imprimir la URL

    const videoPlayer = document.getElementById('video-player-1');
    videoPlayer.src = videoUrl;
    videoPlayer.play();
    
    
    
      
    spinner.style.display = 'none';
    xd.style.display = 'block'

})