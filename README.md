
<h1>BlindAid</h1>
<p>Computer‑vision & AI for helping visually impaired people avoid obstacles</p>

<h2>Overview</h2>
<p>BlindAid is a computer vision project using Artificial Intelligence to assist visually impaired individuals in navigating their surroundings and avoiding obstacles.<br>
The system captures visual input, processes it to detect depth, and converts that information into audio feedback.</p>

<h2>Motivation</h2>
<p>Many visually impaired individuals lack access to affordable assistive technology.<br>
BlindAid aims to provide a software‑based solution that runs on consumer hardware.</p>

<h2>Repository Structure</h2>
<table>
<tr><th>File</th><th>Description</th></tr>
<tr><td>main.py</td><td>Entry point for video processing and audio feedback</td></tr>
<tr><td>camera_stream.py</td><td>Handles real‑time camera capture</td></tr>
<tr><td>vision_depth.py</td><td>Depth estimation and obstacle detection</td></tr>
<tr><td>generate_sound.py</td><td>Creates audio alerts from detection results</td></tr>
<tr><td>audio_manager.py</td><td>Manages audio output system</td></tr>
</table>

<h2>Key Features</h2>
<ul>
<li>Real‑time camera input</li>
<li>Depth or obstacle detection</li>
<li>Audio feedback system</li>
<li>Modular Python structure</li>
<li>Lightweight, hardware‑friendly implementation</li>
</ul>

<h2>Requirements</h2>
<ul>
<li>Python 3.x</li>
<li>OpenCV</li>
<li>Audio output device</li>
<li>Webcam or USB camera</li>
</ul>

<h2>Usage</h2>
<pre>
git clone https://github.com/aditudor30/BlindAid.git
cd BlindAid
pip install -r requirements.txt
python main.py
</pre>

<h2>Experimentation Ideas</h2>
<ul>
<li>Add advanced depth algorithms</li>
<li>Use object detection models</li>
<li>Reduce latency for real‑time responsiveness</li>
<li>Add configuration panel</li>
<li>Create GUI or mobile version</li>
</ul>

<h2>License</h2>
<p>Open for educational and experimental purposes. Feel free to modify and improve.</p>

