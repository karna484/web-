document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/login', {
        method: 'POST',
        body: new URLSearchParams({ username, password })
    });
    const result = await response.json();
    alert(result.message);
});

async function startFaceLogin() {
    const video = document.createElement('video');
    video.width = 640;
    video.height = 480;

    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    document.body.appendChild(video);

    video.play();

    setTimeout(async () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const dataUrl = canvas.toDataURL('image/jpeg');
        const blob = await (await fetch(dataUrl)).blob();

        const formData = new FormData();
        formData.append('face_image', blob);

        const response = await fetch('/face_login', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        alert(result.message);

        stream.getTracks().forEach(track => track.stop());
        document.body.removeChild(video);
    }, 3000);  // Capture after 3 seconds
}
