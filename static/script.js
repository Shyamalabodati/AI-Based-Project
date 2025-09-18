function appendMessage(text, sender) {
  const chatbox = document.getElementById("chatbox");
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  msg.innerText = text;
  chatbox.appendChild(msg);
  chatbox.scrollTop = chatbox.scrollHeight;
}

function sendMessage() {
  const input = document.getElementById("userInput");
  const text = input.value.trim();
  if (text === "") return;

  appendMessage(text, "user");
  input.value = "";

  fetch("/get_answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: text })
  })
  .then(res => res.json())
  .then(data => {
    let reply = data.answer || "❌ Sorry, I don’t have an answer for that.";
    appendMessage(reply, "bot");
    // Speak bot reply
    let speech = new SpeechSynthesisUtterance(reply);
    window.speechSynthesis.speak(speech);
  });
}

function clearChat() {
  document.getElementById("chatbox").innerHTML = "";
}

function startVoice() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Your browser does not support speech recognition.");
    return;
  }
  const recognition = new webkitSpeechRecognition();
  recognition.lang = "en-US";
  recognition.start();
  recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    document.getElementById("userInput").value = transcript;
    sendMessage();
  };
}
