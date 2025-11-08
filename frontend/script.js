const generateButton = document.getElementById("generate");
const promptInput = document.getElementById("prompt");
const statusLabel = document.getElementById("status");
const audioPlayer = document.getElementById("audioPlayer");

document.addEventListener("DOMContentLoaded", () => {
    const generateButton = document.getElementById("generate");
    const promptInput = document.getElementById("prompt");
    const statusLabel = document.getElementById("status");
    const progressContainer = document.querySelector(".progress-container");
    const progressBar = document.getElementById("progress-bar");
    const audioContainer = document.getElementById("audioContainer");

    generateButton.addEventListener("click", async () => {
        const prompt = promptInput.value.trim();
        if (!prompt) {
            statusLabel.textContent = "Please enter a prompt.";
            return;
        }

        // Show and reset progress bar container and bar
        progressContainer.style.display = "block";
        progressBar.style.width = "0%";
        statusLabel.textContent = "Generating conversation...";

        let progress = 0;
        const fakeInterval = setInterval(() => {
            if (progress < 95) {
                progress += Math.random() * 5;
                progressBar.style.width = Math.min(progress, 95) + "%";
            }
        }, 200);

        try {
            const formData = new FormData();
            formData.append("prompt", prompt);

            const response = await fetch("/generate", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                statusLabel.textContent = "Error: " + errorText;
                progressContainer.style.display = "none";
                clearInterval(fakeInterval);
                return;
            }

            const blob = await response.blob();
            clearInterval(fakeInterval);
            progressBar.style.width = "100%";

            const audioURL = URL.createObjectURL(blob);

            // Create a new audio element for this session's output
            const newAudio = document.createElement("audio");
            newAudio.controls = true;
            newAudio.src = audioURL;
            newAudio.style.display = "block";
            newAudio.style.marginTop = "10px";

            // Append to container
            audioContainer.appendChild(newAudio);

            // Optionally auto-play the newest audio
            newAudio.play();

            statusLabel.textContent = "✅ Conversation generated successfully!";

            setTimeout(() => {
                progressContainer.style.display = "none";
            }, 500);

        } catch (err) {
            console.error(err);
            statusLabel.textContent = "Error generating conversation.";
            progressContainer.style.display = "none";
            clearInterval(fakeInterval);
        }
    });
});
