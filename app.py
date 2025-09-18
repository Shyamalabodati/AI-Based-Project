from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "secret123"

# Admin credentials (Chrome-safe)
ADMIN_USER = "admin"
ADMIN_PASS = "Admin123!"  # Strong password, avoids Chrome alerts

# FAQ database
faq = {
    "college name": "Our college is ABC Institute of Technology.",
    "courses offered": "We offer B.Tech, M.Tech, MBA, and MCA programs.",
    "library timing": "The library is open from 8 AM to 8 PM.",
    "contact": "You can contact us at contact@abc.edu."
}

# Login HTML
login_html = """
<!DOCTYPE html>
<html>
<head>
<title>Login</title>
<style>
body {font-family: Arial,sans-serif; background: linear-gradient(135deg,#8e44ad,#2c3e50); display:flex; justify-content:center; align-items:center; height:100vh;}
.login-box {background:#fff; padding:40px; border-radius:15px; box-shadow:0 5px 20px rgba(0,0,0,0.3); width:350px;}
h2 {text-align:center; color:#6c5ce7;}
input {width:100%; padding:12px; margin:10px 0; border:1px solid #ccc; border-radius:8px;}
button {width:100%; padding:12px; background:#6c5ce7; border:none; color:white; border-radius:8px; cursor:pointer; font-size:16px;}
button:hover {background:#5a4bcf;}
p {color:red; text-align:center;}
</style>
</head>
<body>
<div class="login-box">
<h2>Admin Login</h2>
<form method="post">
<input type="text" name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Login</button>
</form>
{% if error %}<p>{{ error }}</p>{% endif %}
</div>
</body>
</html>
"""

# Chat HTML (same as before)
chat_html = """
<!DOCTYPE html>
<html>
<head>
<title>Chatbot</title>
<style>
body {font-family:'Segoe UI',sans-serif; margin:0; padding:0; background:linear-gradient(135deg,#8e44ad,#2c3e50); display:flex; justify-content:center; align-items:center; height:100vh;}
.chat-wrapper {width:90%; max-width:900px; height:85vh; background:#fff; border-radius:20px; display:flex; flex-direction:column; box-shadow:0 6px 25px rgba(0,0,0,0.25); overflow:hidden;}
header {background:#6c5ce7; color:white; padding:20px; display:flex; justify-content:space-between; align-items:center;}
header h1 {margin:0; font-size:22px;}
a {background:#d63031; color:white; padding:8px 15px; border-radius:8px; text-decoration:none;}
.chatbox {flex:1; padding:20px; overflow-y:auto; background:#f7f7f7; display:flex; flex-direction:column;}
.message {margin:12px 0; padding:14px 18px; border-radius:25px; max-width:70%; font-size:16px; line-height:1.4;}
.user {background:#6c5ce7; color:white; margin-left:auto; text-align:right;}
.bot {background:#e0e0e0; color:black; margin-right:auto;}
.input-area {display:flex; gap:10px; padding:15px; border-top:1px solid #ddd; background:#fff;}
.input-area input {flex:1; padding:14px; border:1px solid #ccc; border-radius:25px; outline:none; font-size:16px;}
.input-area button {padding:12px 16px; border:none; border-radius:50%; background:#6c5ce7; color:white; font-size:16px; cursor:pointer;}
.input-area button:hover {background:#5a4bcf;}
</style>
</head>
<body>
<div class="chat-wrapper">
<header>
<h1>🎓FAQ Chatbot</h1>
<a href="{{ url_for('logout') }}">Logout</a>
</header>
<div id="chatbox" class="chatbox"></div>
<div class="input-area">
<input type="text" id="userInput" placeholder="Type your question...">
<button onclick="sendMessage()">➡️</button>
<button onclick="startVoice()">🎤</button>
<button onclick="clearChat()">🗑️</button>
</div>
</div>
<script>
function appendMessage(sender,text){
    let div=document.createElement("div");
    div.className="message "+sender;
    div.textContent=text;
    document.getElementById("chatbox").appendChild(div);
    div.scrollIntoView();
}

function sendMessage(){
    let input=document.getElementById("userInput");
    let text=input.value.trim();
    if(text==="") return;
    appendMessage("user",text);
    input.value="";
    fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text})})
    .then(res=>res.json())
    .then(data=>{
        appendMessage("bot",data.reply);
        speak(data.reply);
    });
}

function startVoice(){
    if(!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)){
        alert("Your browser does not support voice recognition!");
        return;
    }
    let rec=new (window.SpeechRecognition||window.webkitSpeechRecognition)();
    rec.lang="en-US"; rec.start();
    rec.onresult=function(e){
        document.getElementById("userInput").value=e.results[0][0].transcript;
        sendMessage();
    }
}

function clearChat(){document.getElementById("chatbox").innerHTML="";}
function speak(text){let u=new SpeechSynthesisUtterance(text); speechSynthesis.speak(u);}
</script>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["user"] = ADMIN_USER
            return redirect(url_for("chat"))
        else:
            return render_template_string(login_html, error="Invalid credentials")
    return render_template_string(login_html)

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(chat_html)

@app.route("/chat", methods=["POST"])
def get_reply():
    user_msg = request.json.get("message","").lower()
    reply = faq.get(user_msg,"❌ Sorry, this information is not available.")
    return {"reply":reply}

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__=="__main__":
    app.run(debug=True)
