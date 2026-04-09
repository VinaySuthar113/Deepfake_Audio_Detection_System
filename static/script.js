let mediaRecorder
let history=[]

const resultBox = document.getElementById("result")
const meter = document.getElementById("meterFill")

const wavesurfer = WaveSurfer.create({
container:"#waveform",
waveColor:"cyan",
progressColor:"white"
})

async function startListening(){

const stream = await navigator.mediaDevices.getUserMedia({audio:true})

mediaRecorder = new MediaRecorder(stream)

// ✅ FIXED → 4 sec chunks
mediaRecorder.start(4000)

mediaRecorder.ondataavailable = async function(e){

const blob = e.data

wavesurfer.loadBlob(blob)

sendChunk(blob)

}

}

async function sendChunk(blob){

const formData = new FormData()

formData.append("audio",blob,"chunk.wav")

const response = await fetch("/detect",{
method:"POST",
body:formData
})

const result = await response.json()

updateUI(result)

}

function updateUI(result){

history.push(result.fake_probability)

if(history.length > 5){
history.shift()
}

// ✅ use max instead of avg
let maxVal = Math.max(...history)

if(maxVal > 0.6){

resultBox.innerHTML="⚠ FAKE VOICE DETECTED"
resultBox.style.color="red"

meter.style.width = (maxVal*100)+"%"
meter.style.background="red"

}
else{

resultBox.innerHTML="REAL VOICE"
resultBox.style.color="lightgreen"

meter.style.width = (result.real_probability*100)+"%"
meter.style.background="cyan"

}

}

document.getElementById("recordBtn").onclick = startListening


// upload support
document.getElementById("upload").onchange = async function(){

const file = this.files[0]

wavesurfer.loadBlob(file)

const formData = new FormData()
formData.append("audio", file)

const response = await fetch("/detect",{
method:"POST",
body:formData
})

const result = await response.json()

updateUI(result)

}