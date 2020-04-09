# audio_to_audio_Dialogflow code in Python
Code for audio_to_audio interaction with dialogflow.

Works well only with python 3.5+
Install following packages

pip install gtts
pip install dialogflow
pip install pyaudio
pip install simpleaudio


Get the service key json from dialogflow project & give path in 23rd line!

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/path/to/file.json" #https://dialogflow.com/docs/reference/v2-auth-setup

Get Project Id and paste it in 246th line as follows

    project_id = "YOUR PROJECT ID"   #You can find them under dialogflow settings console

