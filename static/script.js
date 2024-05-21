// script.js
const resultDiv = document.getElementById("result");
const urlParams = new URLSearchParams(window.location.search);
const result = urlParams.get("result");
if (result) {
  resultDiv.innerText = result;
  // Show popup with decoded text
  showPopup(result);
}

function showPopup(text) {
  const popupText = document.getElementById("popup-text");
  popupText.innerText = text;
  const popup = document.getElementById("popup");
  popup.style.display = "block";
}

function closePopup() {
  const popup = document.getElementById("popup");
  popup.style.display = "none";
}

// video
document.addEventListener("DOMContentLoaded", function() {
  // Get the video element
  var video = document.querySelector(".background-video");

  // Check if the video element exists
  if(video) {
    // Set the playback rate to 0.5 (half of the original speed)
    video.playbackRate = 0.1;
  }
});
